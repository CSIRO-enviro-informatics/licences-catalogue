from flask import Blueprint, render_template, request, redirect, url_for, abort, jsonify
from controller import db_access, functions
import _conf as conf
import json

routes = Blueprint('controller', __name__)


#
#   pages
#
@routes.route('/')
def home():
    return render_template('page_home.html')


@routes.route('/search')
def search():
    actions = db_access.get_all_actions()
    return render_template('search.html', actions=actions)


@routes.route('/_search_results')
def search_results():
    permissions = json.loads(request.args.get('permissions'))
    duties = json.loads(request.args.get('duties'))
    prohibitions = json.loads(request.args.get('prohibitions'))
    results = functions.get_policies_with_constraints(permissions, duties, prohibitions)
    return jsonify(
        perfect_licences=results['perfect'],
        extra_licences=results['extra'],
        insufficient_licences=results['insufficient']
    )


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
    licences = db_access.get_all_policies()
    items = list()
    for licence in licences:
        if licence['LABEL'] is None:
            licence['LABEL'] = licence['URI']
        items.append({'uri': url_for('controller.licence_routes', uri=licence['URI']), 'label': licence['LABEL']})
    items = sorted(items, key=lambda item:item['label'].lower())
    # test for preferred Media Type
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(licences)
    else:
        return render_template(
            'browse_list.html',
            title=title,
            items=items,
            permalink=conf.BASE_URI + url_for('controller.licence_routes'),
            rdf_link='#!',
            json_link=url_for('controller.licence_routes', _format='application/json')
        )


def view_licence(licence_uri):
    try:
        licence = db_access.get_policy(licence_uri)
        rules = db_access.get_rules_for_policy(licence_uri)
    except ValueError:
        abort(404)
        return
    title = licence['LABEL']
    for rule in rules:
        if rule['LABEL'] is None:
            rule['LABEL'] = rule['URI']
        rule['ACTIONS'] = [action['LABEL'] for action in rule['ACTIONS']]
    rules = sorted(rules, key=lambda rule: rule['LABEL'].lower())
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(licence)
    else:
        return render_template(
            'view_licence.html',
            title=title,
            permalink=conf.BASE_URI + url_for('controller.licence_routes', uri=licence_uri),
            rdf_link='#!',
            json_link=url_for('controller.licence_routes', _format='application/json', uri=licence_uri),
            logo=licence['LOGO'],
            licence=licence,
            rules=rules
        )


@routes.route('/rule/index.json')
def view_rule_list_json():
    redirect_url = '/rule/?_format=application/json'
    uri = request.values.get('uri')
    if uri is not None:
        redirect_url += '&uri=' + uri
    return redirect(redirect_url)


@routes.route('/rule/')
def rule_routes():
    rule_uri = request.values.get('uri')
    if rule_uri is None:
        return view_rules_list()
    else:
        return view_rule(rule_uri)


def view_rules_list():
    title = 'Rule Register'
    rules = db_access.get_all_rules()
    items = list()
    for rule in rules:
        if rule['LABEL'] is None:
            rule['LABEL'] = rule['URI']
        items.append({'uri': url_for('controller.rule_routes', uri=rule['URI']), 'label': rule['LABEL']})
    items = sorted(items, key=lambda item: item['label'].lower())
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(rules)
    else:
        return render_template(
            'browse_list.html',
            title=title,
            items=items,
            permalink=conf.BASE_URI + url_for('controller.rule_routes'),
            rdf_link='#!',
            json_link=url_for('controller.rule_routes', _format='application/json')
        )


def view_rule(rule_uri):
    try:
        rule = db_access.get_rule(rule_uri)
        licences = db_access.get_policies_for_rule(rule_uri)
    except ValueError:
        abort(404)
        return
    for licence in licences:
        if licence['LABEL'] is None:
            licence['LABEL'] = licence['URI']
    licences = sorted(licences, key=lambda licence:licence['LABEL'].lower())
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(rule)
    else:
        return render_template(
            'view_rule.html',
            permalink=conf.BASE_URI + url_for('controller.rule_routes', uri=rule_uri),
            rdf_link='#!',
            json_link=url_for('controller.rule_routes', _format='application/json', uri=rule_uri),
            rule=rule,
            licences=licences,
            title=rule['LABEL']
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
    items = list()
    for action in actions:
        if action['URI'] is None:
            action['LABEL'] = action['URI']
        items.append({'uri': url_for('controller.action_routes', uri=action['URI']), 'label': action['LABEL']})
    items = sorted(items, key=lambda item:item['label'].lower())
    title = 'Action Register'
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(actions)
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
        rules = db_access.get_rules_using_action(action_uri)
    except ValueError:
        abort(404)
        return
    if action['LABEL'] is None:
        action['LABEL'] = action['URI']
    for rule in rules:
        if rule['LABEL'] is None:
            rule['LABEL'] = rule['URI']
    rules = sorted(rules, key=lambda rule: rule['LABEL'].lower())
    preferred_media_type = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if preferred_media_type == 'application/json' or request.values.get('_format') == 'application/json':
        return jsonify(action)
    else:
        return render_template(
            'view_action.html',
            permalink=conf.BASE_URI + url_for('controller.action_routes', uri=action['URI']),
            rdf_link='#!',
            json_link=url_for('controller.action_routes', _format='application/json', uri=action_uri),
            action=action,
            rules=rules
        )


@routes.route('/licence/create')
def create_licence_form():
    rules = db_access.get_all_rules()
    rules.sort(key=lambda rule: rule['LABEL'])
    for rule in rules:
        rule['LINK'] = url_for('controller.rule_routes', uri=rule['URI'])
    return render_template('create_licence.html', rules=rules)
