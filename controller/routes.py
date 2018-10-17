from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify, Response
from controller import db_access, functions
import _conf as conf
import json
from uuid import uuid4
from rdflib import Graph, RDF, RDFS, Literal, URIRef, XSD, OWL, BNode
from rdflib.namespace import SKOS, DCTERMS, FOAF

ADMS = 'http://www.w3.org/ns/adms#'
CREATIVE_COMMONS = 'http://creativecommons.org/ns#'
ODRL = 'http://www.w3.org/ns/odrl/2/'
REG = 'http://purl.org/linked-data/registry#'
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
party_register_comment = 'This is a register (controlled list) of machine-readable Parties. The Party entity could be' \
                         ' a person, group of people, organisation, or agent. An agent is a person or thing that take' \
                         's an active role or produces a specified effect.'

routes = Blueprint('controller', __name__)


@routes.route('/')
def home():
    return render_template('page_home.html')


@routes.route('/about')
def about():
    return render_template('about.html')


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
    items = []
    for policy_uri in db_access.get_all_policies():
        policies.append(db_access.get_policy(policy_uri))

    # Test for preferred Media Type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        # Display as JSON
        register_uri = url_for('controller.licence_routes', _external=True)
        register_json = {
            register_uri: {
                'type': REG + 'Register',
                'label': title,
                'comment': 'This is a register (controlled list) of machine-readable Licenses which are a particular '
                           'type of Policy.',
                'containedItemClass': CREATIVE_COMMONS + 'License'
            }
        }
        for policy in policies:
            register_json[policy['URI']] = {
                'type': CREATIVE_COMMONS + 'License',
                'label': policy['LABEL'],
                'comment': policy['COMMENT'],
                'register': register_uri
            }
        return jsonify(register_json)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        # Display as RDF
        return Response(get_policy_list_rdf(policies).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        # Display as JSON-LD
        json_ld = get_policy_list_rdf(policies).serialize(format='json-ld', context=JSON_CONTEXT_POLICIES)
        return Response(json_ld, status=200, mimetype='application/json')
    else:
        # Display as HTML
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


def get_policy_list_rdf(policies):
    graph = Graph()
    graph.bind('odrl', ODRL)
    graph.bind('cc', CREATIVE_COMMONS)
    graph.bind('owl', OWL)
    graph.bind('dct', DCTERMS)
    graph.bind('foaf', FOAF)
    graph.bind('adms', ADMS)
    graph.bind('reg', REG)
    register_node = URIRef(url_for('controller.licence_routes', _external=True))
    graph.add((register_node, RDF.type, URIRef(REG + 'Register')))
    graph.add((register_node, RDFS.label, Literal('Licence Register')))
    graph.add((register_node, RDFS.comment, Literal('This is a register (controlled list) of machine-readable Licenses '
                                                    'which are a particular type of Policy.')))
    graph.add((register_node, URIRef(REG + 'containedItemClass'), URIRef(ODRL + 'Policy')))
    for policy in policies:
        policy_node = URIRef(policy['URI'])
        graph.add((policy_node, RDF.type, URIRef(ODRL + 'Policy')))
        if policy['TYPE']:
            graph.add((policy_node, RDF.type, URIRef(policy['TYPE'])))
        if policy['LABEL']:
            graph.add((policy_node, RDFS.label, Literal(policy['LABEL'], lang='en')))
        if policy['COMMENT']:
            graph.add((policy_node, RDFS.comment, Literal(policy['COMMENT'], lang='en')))
        graph.add((policy_node, URIRef(REG + 'register'), URIRef(register_node)))
    return graph


def view_licence(policy_uri):
    try:
        policy = db_access.get_policy(policy_uri)
    except ValueError:
        abort(404)
        return
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    rules = [db_access.get_rule(rule_uri) for rule_uri in policy['RULES']]
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        # Display as JSON
        licence_json = {
            policy['URI']: {
                'comment': policy['COMMENT'],
                'created': policy['CREATED'],
                'creator': policy['CREATOR'],
                'hasVersion': policy['HAS_VERSION'],
                'jurisdiction': policy['JURISDICTION'],
                'label': policy['LABEL'],
                'language': policy['LANGUAGE'],
                'legalCode': policy['LEGAL_CODE'],
                'logo': policy['LOGO'],
                'sameAs': policy['SAME_AS'],
                'seeAlso': policy['SEE_ALSO'],
                'status': policy['STATUS'],
                'type': policy['TYPE'],
                'containedItemClass': ODRL + 'Rule'
            }
        }
        for rule in rules:
            licence_json[rule['URI']] = {
                'label': rule['LABEL'],
                'type': [rule['TYPE_URI'], ODRL + 'Rule'],
                'assignors': rule['ASSIGNORS'],
                'assignees': rule['ASSIGNEES'],
                'actions': [action['URI'] for action in rule['ACTIONS']],
                'licence': policy['URI']
            }
        return jsonify(licence_json)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        # Display as RDF
        return Response(get_policy_rdf(policy, rules).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        # Display as JSON-LD
        json_ld = get_policy_rdf(policy, rules).serialize(format='json-ld', context=JSON_CONTEXT_POLICIES)
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


def get_policy_rdf(policy, rules):
    graph = Graph()
    graph.bind('odrl', ODRL)
    graph.bind('cc', CREATIVE_COMMONS)
    graph.bind('owl', OWL)
    graph.bind('dct', DCTERMS)
    graph.bind('foaf', FOAF)
    graph.bind('adms', ADMS)
    policy_node = URIRef(policy['URI'])
    graph.add((policy_node, RDF.type, URIRef(ODRL + 'Policy')))
    if policy['TYPE']:
        graph.add((policy_node, RDF.type, URIRef(policy['TYPE'])))
    if policy['LABEL']:
        graph.add((policy_node, RDFS.label, Literal(policy['LABEL'], lang='en')))
    if policy['COMMENT']:
        graph.add((policy_node, RDFS.comment, Literal(policy['COMMENT'], lang='en')))
    if policy['CREATED']:
        graph.add((policy_node, DCTERMS.created, Literal(policy['CREATED'], datatype=XSD.date)))
    if policy['CREATOR']:
        graph.add((policy_node, DCTERMS.creator, URIRef(policy['CREATOR'])))
    if policy['HAS_VERSION']:
        graph.add((policy_node, DCTERMS.hasVersion, Literal(policy['HAS_VERSION'])))
    if policy['JURISDICTION']:
        graph.add((policy_node, URIRef(CREATIVE_COMMONS + 'jurisdiction'), URIRef(policy['JURISDICTION'])))
    if policy['LANGUAGE']:
        graph.add((policy_node, DCTERMS.language, URIRef(policy['LANGUAGE'])))
    if policy['LEGAL_CODE']:
        graph.add((policy_node, URIRef(CREATIVE_COMMONS + 'legalcode'), URIRef(policy['LEGAL_CODE'])))
    if policy['LOGO']:
        graph.add((policy_node, URIRef(FOAF + 'logo'), URIRef(policy['LOGO'])))
    if policy['SAME_AS']:
        graph.add((policy_node, OWL.sameAs, URIRef(policy['SAME_AS'])))
    if policy['SEE_ALSO']:
        graph.add((policy_node, RDFS.seeAlso, URIRef(policy['SEE_ALSO'])))
    if policy['STATUS']:
        graph.add((policy_node, URIRef(ADMS + 'status'), URIRef(policy['STATUS'])))
    for rule in rules:
        rule_node = BNode()
        graph.add((policy_node, URIRef(ODRL + rule['TYPE_LABEL'].lower()), rule_node))
        graph.add((rule_node, RDF.type, URIRef(ODRL + rule['TYPE_LABEL'])))
        for action in rule['ACTIONS']:
            graph.add((rule_node, URIRef(ODRL + 'action'), URIRef(action['URI'])))
        for assignor in rule['ASSIGNORS']:
            graph.add((rule_node, URIRef(ODRL + 'assignor'), URIRef(assignor)))
        for assignee in rule['ASSIGNEES']:
            graph.add((rule_node, URIRef(ODRL + 'assignee'), URIRef(assignee)))
    return graph


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
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        # Display as JSON
        register_uri = url_for('controller.action_routes', _external=True)
        actions_json = {
            register_uri: {
                'type': REG + 'Register',
                'label': title,
                'comment': 'This is a register (controlled list) of machine-readable Actions.',
                'containedItemClass': ODRL + 'Action'
            }
        }
        for action in actions:
            actions_json[action['URI']] = {
                'type': ODRL + 'Action',
                'label': action['LABEL'],
                'comment': action['DEFINITION'],
                'register': register_uri
            }
        return jsonify(actions_json)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        # Display as RDF
        return Response(get_action_list_rdf(actions).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        # Display as JSON-LD
        json_ld = get_action_list_rdf(actions).serialize(format='json-ld', context=JSON_CONTEXT_ACTIONS)
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


def get_action_list_rdf(actions):
    graph = Graph()
    graph.bind('odrl', 'http://www.w3.org/ns/odrl/2/')
    graph.bind('skos', SKOS)
    register_node = URIRef(url_for('controller.action_routes', _external=True))
    graph.add((register_node, RDF.type, URIRef(REG + 'Register')))
    graph.add((register_node, RDFS.label, Literal('Action Register')))
    graph.add((
        register_node,
        RDFS.comment,
        Literal('This is a register (controlled list) of machine-readable Actions.')
    ))
    graph.add((register_node, URIRef(REG + 'containedItemClass'), URIRef(ODRL + 'Action')))
    for action in actions:
        action_node = URIRef(action['URI'])
        graph.add((action_node, RDF.type, URIRef(ODRL + 'Action')))
        graph.add((action_node, RDFS.label, Literal(action['LABEL'], lang='en')))
        graph.add((action_node, SKOS.definition, Literal(action['DEFINITION'], lang='en')))
        graph.add((action_node, URIRef(REG + 'register'), URIRef(register_node)))
    return graph


def view_action(action_uri):
    try:
        action = db_access.get_action(action_uri)
    except ValueError:
        abort(404)
        return
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        # Display as JSON
        return jsonify({action['URI']: {'label': action['LABEL'], 'definition': action['DEFINITION']}})
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        # Display as RDF
        return Response(get_action_rdf(action).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        # Display as JSON-LD
        json_ld = get_action_rdf(action).serialize(format='json-ld', context=JSON_CONTEXT_ACTIONS)
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


def get_action_rdf(action):
    graph = Graph()
    graph.bind('odrl', 'http://www.w3.org/ns/odrl/2/')
    graph.bind('skos', SKOS)
    action_node = URIRef(action['URI'])
    graph.add((action_node, RDF.type, URIRef(ODRL + 'Action')))
    graph.add((action_node, RDFS.label, Literal(action['LABEL'], lang='en')))
    graph.add((action_node, SKOS.definition, Literal(action['DEFINITION'], lang='en')))
    return graph


@routes.route('/licence/create')
def create_licence_form():
    actions = db_access.get_all_actions()
    parties = db_access.get_all_parties()
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
        return Response(error.args, status=500, mimetype='text/plain')
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
    parties = db_access.get_all_parties()
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        # Display as JSON
        register_uri = url_for('controller.party_routes', _external=True)
        parties_json = {
            register_uri: {
                'type': REG + 'Register',
                'label': title,
                'comment': party_register_comment,
                'containedItemClass': ODRL + 'Party'
            }
        }
        for party in parties:
            parties_json[party['URI']] = {
                'type': ODRL + 'Party',
                'label': party['LABEL'],
                'comment': party['COMMENT'],
                'register': register_uri
            }
        return jsonify(parties_json)
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        # Display as RDF
        return Response(get_party_list_rdf(parties).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        # Display as JSON-LD
        json_ld = get_party_list_rdf(parties).serialize(format='json-ld', context=JSON_CONTEXT_PARTIES)
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
            items=items,
            permalink=url_for('controller.party_routes', _external=True),
            rdf_link=url_for('controller.party_routes', _format='text/turtle'),
            json_link=url_for('controller.party_routes', _format='application/json'),
            json_ld_link=url_for('controller.party_routes', _format='application/ld+json')
        )


def get_party_list_rdf(parties):
    graph = Graph()
    graph.bind('odrl', 'http://www.w3.org/ns/odrl/2/')
    graph.bind('skos', SKOS)
    register_node = URIRef(url_for('controller.party_routes', _external=True))
    graph.add((register_node, RDF.type, URIRef(REG + 'Register')))
    graph.add((register_node, RDFS.label, Literal('Party Register')))
    graph.add((
        register_node,
        RDFS.comment,
        Literal(party_register_comment)
    ))
    graph.add((register_node, URIRef(REG + 'containedItemClass'), URIRef(ODRL + 'Party')))
    for party in parties:
        party_node = URIRef(party['URI'])
        graph.add((party_node, RDF.type, URIRef(ODRL + 'Party')))
        if party['LABEL']:
            graph.add((party_node, RDFS.label, Literal(party['LABEL'], lang='en')))
        if party['COMMENT']:
            graph.add((party_node, RDFS.comment, Literal(party['COMMENT'], lang='en')))
        graph.add((party_node, URIRef(REG + 'register'), URIRef(register_node)))
    return graph


def view_party(party_uri):
    try:
        party = db_access.get_party(party_uri)
    except ValueError:
        abort(404)
        return
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        # Display as JSON
        return jsonify({party['URI']: {'label': party['LABEL'], 'comment': party['COMMENT']}})
    elif preferred_media_type == 'text/turtle' or request.values.get('_format') == 'text/turtle':
        # Display as RDF
        return Response(get_party_rdf(party).serialize(format='turtle'), status=200, mimetype='text/turtle')
    elif preferred_media_type == 'application/ld+json' or request.values.get('_format') == 'application/ld+json':
        # Display as JSON-LD
        json_ld = get_party_rdf(party).serialize(format='json-ld', context=JSON_CONTEXT_PARTIES)
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


def get_party_rdf(party):
    graph = Graph()
    graph.bind('odrl', 'http://www.w3.org/ns/odrl/2/')
    party_node = URIRef(party['URI'])
    graph.add((party_node, RDF.type, URIRef(ODRL + 'Party')))
    if party['LABEL']:
        graph.add((party_node, RDFS.label, Literal(party['LABEL'], lang='en')))
    if party['COMMENT']:
        graph.add((party_node, RDFS.comment, Literal(party['COMMENT'], lang='en')))
    return graph
