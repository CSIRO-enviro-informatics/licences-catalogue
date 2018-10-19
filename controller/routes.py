from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify, Response, flash
import requests
from controller import db_access, functions
import _conf as conf
import json
from uuid import uuid4

from controller.functions import get_policy_json

JSON_CONTEXT_ACTIONS = {
    '@vocab': 'http://www.w3.org/ns/odrl/2/',
    'label': 'http://www.w3.org/2000/01/rdf-schema#label',
    'definition': 'http://www.w3.org/2004/02/skos/core#definition',
    'containedItemClass': 'http://purl.org/linked-data/registry#containedItemClass',
    'comment': 'http://www.w3.org/2000/01/rdf-schema#comment',
    'register': 'http://purl.org/linked-data/registry#register'
}
JSON_CONTEXT_POLICIES = {
    '@vocab': 'http://www.w3.org/ns/odrl/2/',
    'label': 'http://www.w3.org/2000/01/rdf-schema#label',
    'created': 'http://purl.org/dc/terms/created',
    'comment': 'http://www.w3.org/2000/01/rdf-schema#comment',
    'sameAs': 'http://www.w3.org/2002/07/owl#sameAs',
    'register': 'http://purl.org/linked-data/registry#register',
    'containedItemClass': 'http://purl.org/linked-data/registry#containedItemClass',
    'hasVersion': 'http://purl.org/dc/terms/hasVersion',
    'language': 'http://purl.org/dc/terms/language',
    'legalCode': 'http://creativecommons.org/ns#legalcode',
    'jurisdiction': 'http://creativecommons.org/ns#jurisdiction',
    'seeAlso': 'http://www.w3.org/2000/01/rdf-schema#seeAlso',
    'creator': 'http://purl.org/dc/terms/creator',
    'logo': 'http://xmlns.com/foaf/0.1/logo',
    'status': 'http://www.w3.org/ns/adms#status'
}
JSON_CONTEXT_PARTIES = {
    '@vocab': 'http://www.w3.org/ns/odrl/2/',
    'label': 'http://www.w3.org/2000/01/rdf-schema#label',
    'comment': 'http://www.w3.org/2000/01/rdf-schema#comment',
    'register': 'http://purl.org/linked-data/registry#register',
    'containedItemClass': 'http://purl.org/linked-data/registry#containedItemClass',
}

routes = Blueprint('controller', __name__)


@routes.route('/')
def home():
    return render_template('page_home.html')


@routes.route('/about')
def about():
    return render_template('about.html')


@routes.route('/contact_submit', methods=['POST'])
def contact_submit():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']
    if conf.MAILJET_SECRETS and conf.MAILJET_EMAIL_RECEIVERS and conf.MAILJET_EMAIL_SENDER:
        email_body = 'Name: {name}\nEmail: {email}\n\n{message}'.format(name=name, email=email, message=message)
        data = {
            'Messages': [{
                'From': {'Email': conf.MAILJET_EMAIL_SENDER, 'Name': 'Licence Catalogue Contact Form'},
                'To': [{'Email': email, 'Name': ''} for email in conf.MAILJET_EMAIL_RECEIVERS],
                'Subject': '[Licence Catalogue Contact Form] Enquiry from ' + email,
                'TextPart': email_body
            }]
        }
        requests.post(
            conf.MAILJET_SECRETS['API_ENDPOINT'],
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'},
            auth=(conf.MAILJET_SECRETS['MJ_APIKEY_PUBLIC'], conf.MAILJET_SECRETS['MJ_APIKEY_PRIVATE'])
        )
        return redirect(url_for('controller.about'))
    else:
        flash('Contact form is currently disabled')
        return redirect(url_for('controller.about'))


@routes.route('/search')
def search():
    actions = db_access.get_all_actions()
    for action in actions:
        action.update({'LINK': url_for('controller.action_routes', uri=action['URI'])})
    return render_template('search.html', actions=actions, search_url=url_for('controller.search_results'))


@routes.route('/_search_results')
def search_results():
    rules = json.loads(request.args.get('rules'))
    results = functions.search_policies(rules)
    return jsonify(results=results)


@routes.route('/licence/index.json')
def view_licence_list_json():
    redirect_url = url_for('controller.licence_routes', _format='application/json')
    uri = request.values.get('uri')
    if uri is not None:
        redirect_url += '&uri=' + uri
    return redirect(redirect_url)


@routes.route('/licence/')
def licence_routes():
    licence_uri = request.values.get('uri')
    if licence_uri is None:
        return view_licence_list()
    else:
        return view_licence(licence_uri)


def view_licence_list():
    title = 'Licence Register'
    policies = []
    for policy_uri in db_access.get_all_policies():
        policies.append(db_access.get_policy(policy_uri))

    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(functions.get_policies_json(policies, title))
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        policies_rdf = functions.get_policies_rdf(policies).serialize(format='turtle')
        return Response(policies_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_policies_rdf(policies).serialize(format='json-ld', context=JSON_CONTEXT_POLICIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        items = []
        for policy in policies:
            items.append({
                'uri': policy['URI'],
                'label': policy['LABEL'] if policy['LABEL'] else policy['URI'],
                'comment': policy['COMMENT'],
                'link': url_for('controller.licence_routes', uri=policy['URI'])
            })
        items = sorted(items, key=lambda item: item['label'].lower())
        return render_template(
            'browse_list.html',
            title=title,
            items=items,
            permalink=url_for('controller.licence_routes', _external=True),
            rdf_link=url_for('controller.licence_routes', _format='text/turtle'),
            json_link=url_for('controller.licence_routes', _format='application/json'),
            json_ld_link=url_for('controller.licence_routes', _format='application/ld+json')
        )


def view_licence(policy_uri):
    try:
        policy = db_access.get_policy(policy_uri)
    except ValueError:
        abort(404)
        return
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    rules = [db_access.get_rule(rule_uri) for rule_uri in policy['RULES']]
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(get_policy_json(policy, rules))
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        policy_rdf = functions.get_policy_rdf(policy, rules).serialize(format='turtle')
        return Response(policy_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_policy_rdf(policy, rules).serialize(format='json-ld', context=JSON_CONTEXT_POLICIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        permissions = []
        duties = []
        prohibitions = []
        for rule in rules:
            rule['ASSIGNORS'] = [db_access.get_party(assignor) for assignor in rule['ASSIGNORS']]
            rule['ASSIGNEES'] = [db_access.get_party(assignee) for assignee in rule['ASSIGNEES']]
            if rule['LABEL'] is None:
                rule['LABEL'] = rule['URI']
            if rule['TYPE_LABEL'] == 'Permission':
                permissions.append(rule)
            elif rule['TYPE_LABEL'] == 'Duty':
                duties.append(rule)
            elif rule['TYPE_LABEL'] == 'Prohibition':
                prohibitions.append(rule)
        return render_template(
            'view_licence.html',
            title=policy['LABEL'],
            permalink=url_for('controller.licence_routes', uri=policy_uri, _external=True),
            rdf_link=url_for('controller.licence_routes', _format='text/turtle', uri=policy_uri),
            json_link=url_for('controller.licence_routes', _format='application/json', uri=policy_uri),
            json_ld_link=url_for('controller.licence_routes', _format='application/ld+json', uri=policy_uri),
            logo=policy['LOGO'],
            licence=policy,
            permissions=permissions,
            duties=duties,
            prohibitions=prohibitions
        )


@routes.route('/action/index.json')
def view_action_list_json():
    redirect_url = '/action/?_format=application/json'
    uri = request.values.get('uri')
    if uri is not None:
        redirect_url += '&uri=' + uri
    return redirect(redirect_url)


@routes.route('/action/')
def action_routes():
    action_uri = request.values.get('uri')
    if action_uri is None:
        return view_actions_list()
    else:
        return view_action(action_uri)


def view_actions_list():
    title = 'Action Register'
    actions = db_access.get_all_actions()
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(functions.get_actions_json(actions, title))
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        actions_rdf = functions.get_actions_rdf(actions).serialize(format='turtle')
        return Response(actions_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_actions_rdf(actions).serialize(format='json-ld', context=JSON_CONTEXT_ACTIONS)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        items = []
        for action in actions:
            items.append({
                'label': action['LABEL'] if action['LABEL'] else action['URI'],
                'uri': action['URI'],
                'comment': action['DEFINITION'],
                'link': url_for('controller.action_routes', uri=action['URI'])
            })
        items = sorted(items, key=lambda item: item['label'].lower())
        return render_template(
            'browse_list.html',
            title=title,
            items=items,
            permalink=url_for('controller.action_routes', _external=True),
            rdf_link=url_for('controller.action_routes', _format='text/turtle'),
            json_link=url_for('controller.action_routes', _format='application/json'),
            json_ld_link=url_for('controller.action_routes', _format='application/ld+json')
        )


def view_action(action_uri):
    try:
        action = db_access.get_action(action_uri)
    except ValueError:
        abort(404)
        return
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify({action['URI']: {'label': action['LABEL'], 'definition': action['DEFINITION']}})
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        return Response(functions.get_action_rdf(action).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_action_rdf(action).serialize(format='json-ld', context=JSON_CONTEXT_ACTIONS)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        policies = db_access.get_policies_using_action(action_uri)
        if action['LABEL'] is None:
            action['LABEL'] = action['URI']
        for policy in policies:
            if policy['LABEL'] is None:
                policy['LABEL'] = policy['URI']
        policies = sorted(policies, key=lambda rule: rule['LABEL'].lower())
        return render_template(
            'view_action.html',
            permalink=conf.BASE_URI + url_for('controller.action_routes', uri=action['URI']),
            rdf_link=url_for('controller.action_routes', _format='text/turtle', uri=action_uri),
            json_link=url_for('controller.action_routes', _format='application/json', uri=action_uri),
            json_ld_link=url_for('controller.action_routes', _format='application/ld+json', uri=action_uri),
            action=action,
            licences=policies
        )


@routes.route('/licence/create')
def create_licence_form():
    actions = db_access.get_all_actions()
    parties = db_access.get_all_parties()
    try:
        external_parties = json.loads(requests.get('http://catalogue.linked.data.gov.au/org/json').text)
        for external_party in external_parties:
            if not any(external_party['view_taxonomy_term'] == party['URI'] for party in parties):
                parties.append({
                    'URI': external_party['view_taxonomy_term'],
                    'LABEL': external_party['name'],
                    'COMMENT': external_party['description__value']
                })
    except requests.ConnectionError:
        pass
    actions.sort(key=lambda x: (x['LABEL'] is None, x['LABEL']))
    parties.sort(key=lambda x: (x['LABEL'] is None, x['LABEL']))
    for action in actions:
        action.update({'LINK': url_for('controller.action_routes', uri=action['URI'])})
    for party in parties:
        party.update({'LINK': url_for('controller.party_routes', uri=party['URI'])})
    return render_template('create_licence.html', actions=actions, parties=parties,
                           search_url=url_for('controller.search_results'))


@routes.route('/licence/create', methods=['POST'])
def create_licence():
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted'
    }
    attributes.update(request.form.items())
    uri = conf.BASE_URI + '/' + str(uuid4())
    rules = json.loads(attributes.pop('rules'))
    for rule in rules:
        rule['ACTIONS'] = [action['URI'] for action in rule['ACTIONS']]
    try:
        functions.create_policy(uri, attributes, rules)
    except ValueError as error:
        flash(error.args, category='error')
        return redirect(url_for('controller.create_licence_form'))
    return redirect(url_for('controller.licence_routes', uri=uri))


@routes.route('/party/')
def party_routes():
    party_uri = request.values.get('uri')
    if party_uri is None:
        return view_party_list()
    else:
        return view_party(party_uri)


def view_party_list():
    title = 'Party Register'
    subtitle = 'This register only contains Parties currently used by Licences in the Licence Register. Other ' \
               'available Parties are excluded for brevity.'
    parties = db_access.get_all_parties()
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(functions.get_party_json(parties, title))
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        parties_rdf = functions.get_parties_rdf(parties).serialize(format='turtle')
        return Response(parties_rdf, status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_parties_rdf(parties).serialize(format='json-ld', context=JSON_CONTEXT_PARTIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        items = []
        for party in parties:
            items.append({
                'label': party['LABEL'] if party['LABEL'] else party['URI'],
                'uri': party['URI'],
                'comment': party['COMMENT'],
                'link': url_for('controller.party_routes', uri=party['URI'])
            })
        items = sorted(items, key=lambda item: item['label'].lower())
        return render_template(
            'browse_list.html',
            title=title,
            subtitle=subtitle,
            items=items,
            permalink=url_for('controller.party_routes', _external=True),
            rdf_link=url_for('controller.party_routes', _format='text/turtle'),
            json_link=url_for('controller.party_routes', _format='application/json'),
            json_ld_link=url_for('controller.party_routes', _format='application/ld+json')
        )


def view_party(party_uri):
    try:
        party = db_access.get_party(party_uri)
    except ValueError:
        abort(404)
        return
    # Respond according to preferred media type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify({party['URI']: {'label': party['LABEL'], 'comment': party['COMMENT']}})
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        return Response(functions.get_party_rdf(party).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        json_ld = functions.get_party_rdf(party).serialize(format='json-ld', context=JSON_CONTEXT_PARTIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
        rules = db_access.get_rules_for_party(party_uri)
        policies = []
        for rule in rules:
            policies.extend(db_access.get_policies_for_rule(rule))
        if party['LABEL'] is None:
            party['LABEL'] = party['URI']
        for policy in policies:
            if policy['LABEL'] is None:
                policy['LABEL'] = policy['URI']
        policies = sorted(policies, key=lambda rule: rule['LABEL'].lower())
        return render_template(
            'view_party.html',
            permalink=conf.BASE_URI + url_for('controller.action_routes', uri=party['URI']),
            rdf_link=url_for('controller.party_routes', _format='text/turtle', uri=party_uri),
            json_link=url_for('controller.party_routes', _format='application/json', uri=party_uri),
            json_ld_link=url_for('controller.party_routes', _format='application/ld+json', uri=party_uri),
            party=party,
            licences=policies
        )
