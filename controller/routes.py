from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify
from controller import db_access, functions
import _conf as conf
import json
from uuid import uuid4

CC_LICENCE = 'http:/creativecommons.org/ns#License'
ODRL_RULE = 'http://www.w3.org/ns/odrl/2/Rule'
ODRL_ACTION = 'http://www.w3.org/ns/odrl/2/Action'

routes = Blueprint('controller', __name__)


#
#   pages
#
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
    return render_template('search.html', actions=actions)


@routes.route('/_search_results')
def search_results():
    rules = json.loads(request.args.get('rules'))
    results = functions.search_policies(rules)
    return jsonify(results=results)


@routes.route('/licence/index.json')
def view_licence_list_json():
    redirect_url = '/licence/?_format=application/json'
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
    items = []
    policy_uris = db_access.get_all_policies()
    for policy_uri in policy_uris:
        policy = db_access.get_policy(policy_uri)
        items.append({
            'uri': policy['URI'],
            'label': policy['LABEL'] if policy['LABEL'] else policy['URI'],
            'link': url_for('controller.licence_routes', uri=policy['URI']),
            'comment': policy['COMMENT']
        })
    items = sorted(items, key=lambda item: item['label'].lower())
    # test for preferred Media Type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        register_uri = url_for('controller.licence_routes', _external=True)
        register_json = {
            register_uri: {
                'type': 'http://purl.org/linked-data/registry#Register',
                'label': 'Licence Register',
                'comment': 'This is a register (controlled list) of machine-readable Licenses which are a particular '
                           'type of Policy.',
                'containedItemClass': CC_LICENCE
            }
        }
        for item in items:
            register_json[item['uri']] = {
                'type': CC_LICENCE,
                'label': item['label'],
                'comment': item['comment'],
                'register': register_uri
            }
        return jsonify(register_json)
    else:
        return render_template(
            'browse_list.html',
            title=title,
            items=items,
            permalink=conf.BASE_URI + url_for('controller.licence_routes'),
            rdf_link='#!',
            json_link=url_for('controller.licence_routes', _format='application/json')
        )


def view_licence(policy_uri):
    try:
        policy = db_access.get_policy(policy_uri)
    except ValueError:
        abort(404)
        return
    title = policy['LABEL']
    permissions = []
    duties = []
    prohibitions = []
    policy['RULES'] = [db_access.get_rule(rule_uri) for rule_uri in policy['RULES']]
    for rule in policy['RULES']:
        if rule['LABEL'] is None:
            rule['LABEL'] = rule['URI']
        if rule['TYPE_LABEL'] == 'Permission':
            permissions.append(rule)
        elif rule['TYPE_LABEL'] == 'Duty':
            duties.append(rule)
        elif rule['TYPE_LABEL'] == 'Prohibition':
            prohibitions.append(rule)
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
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
                'containedItemClass': ODRL_RULE
            }
        }
        for rule in policy['RULES']:
            licence_json[rule['URI']] = {
                'label': rule['LABEL'],
                'type': [rule['TYPE_URI'], ODRL_RULE],
                'assignors': rule['ASSIGNORS'],
                'assignees': rule['ASSIGNEES'],
                'actions': [action['URI'] for action in rule['ACTIONS']],
                'licence': policy['URI']
            }
        return jsonify(licence_json)
    else:
        return render_template(
            'view_licence.html',
            title=title,
            permalink=conf.BASE_URI + url_for('controller.licence_routes', uri=policy_uri),
            rdf_link='#!',
            json_link=url_for('controller.licence_routes', _format='application/json', uri=policy_uri),
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
    actions = db_access.get_all_actions()
    items = []
    for action in actions:
        if action['URI'] is None:
            action['LABEL'] = action['URI']
        items.append({
            'link': url_for('controller.action_routes', uri=action['URI']),
            'uri': action['URI'],
            'label': action['LABEL'],
            'comment': action['DEFINITION']
        })
    items = sorted(items, key=lambda item: item['label'].lower())
    title = 'Action Register'
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        register_uri = url_for('controller.action_routes', _external=True)
        actions_json = {
            register_uri: {
                'type': 'http://purl.org/linked-data/registry#Register',
                'label': 'Action Register',
                'comment': 'This is a register (controlled list) of machine-readable Actions.',
                'containedItemClass': ODRL_ACTION
            }
        }
        for item in items:
            actions_json[item['uri']] = {
                'type': ODRL_ACTION,
                'label': item['label'],
                'comment': item['comment'],
                'register': register_uri
            }
        return jsonify(actions_json)
    else:
        return render_template(
            'browse_list.html',
            title=title,
            items=items,
            permalink=conf.BASE_URI + url_for('controller.action_routes'),
            rdf_link='#!',
            json_link=url_for('controller.action_routes', _format='application/json')
        )


def view_action(action_uri):
    try:
        action = db_access.get_action(action_uri)
        licences = db_access.get_policies_using_action(action_uri)
    except ValueError:
        abort(404)
        return
    if action['LABEL'] is None:
        action['LABEL'] = action['URI']
    for policy in licences:
        if policy['LABEL'] is None:
            policy['LABEL'] = policy['URI']
    licences = sorted(licences, key=lambda rule: rule['LABEL'].lower())
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify({action['URI']: {'label': action['LABEL'], 'definition': action['DEFINITION']}})
    else:
        return render_template(
            'view_action.html',
            permalink=conf.BASE_URI + url_for('controller.action_routes', uri=action['URI']),
            rdf_link='#!',
            json_link=url_for('controller.action_routes', _format='application/json', uri=action_uri),
            action=action,
            licences=licences
        )


@routes.route('/licence/create')
def create_licence_form():
    actions = db_access.get_all_actions()
    actions.sort(key=lambda x: x['LABEL'])
    for action in actions:
        action.update({'LINK': url_for('controller.action_routes', uri=action['URI'])})
    return render_template('create_licence.html', actions=actions)


@routes.route('/licence/create', methods=['POST'])
def create_licence():
    attributes = {'type': 'http://creativecommons.org/ns#License'}
    attributes.update(request.form.items())
    uri = 'http://example.com/licence/' + str(uuid4())
    rules = []
    for permission in json.loads(attributes.pop('permissions')):
        permission['RULE_TYPE'] = 'http://www.w3.org/ns/odrl/2/permission'
        rules.append(permission)
    for duty in json.loads(attributes.pop('duties')):
        duty['RULE_TYPE'] = 'http://www.w3.org/ns/odrl/2/duty'
        rules.append(duty)
    for prohibition in json.loads(attributes.pop('prohibitions')):
        prohibition['RULE_TYPE'] = 'http://www.w3.org/ns/odrl/2/prohibition'
        rules.append(prohibition)
    functions.create_policy(uri, attributes, rules)
    return redirect(url_for('controller.licence_routes', uri=uri))
