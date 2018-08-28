from flask import Blueprint, render_template, request, redirect, url_for, abort, Response
from controller import db_access
import json
import _conf as conf

routes = Blueprint('controller', __name__)


#
#   pages
#
@routes.route('/')
def home():
    return render_template('page_home.html')


@routes.route('/search', methods=['GET'])
def search():
    return render_template('search.html')


@routes.route('/licence/')
def browse_licences():
    title = 'Licence Register'
    items = [
        {'label': 'Licence #1', 'uri': url_for('controller.view_licence')},
        {'label': 'Licence #2', 'uri': url_for('controller.view_licence')},
        {'label': 'Licence #3', 'uri': url_for('controller.view_licence')}
    ]
    permalink = conf.BASE_URI + 'licence/'
    rdf_link = '#!'
    json_link = '#!'

    # test for preferred Media Type
    best = request.accept_mimetypes.best_match(['application/json', 'text/html'])
    if best == 'application/json' or request.values.get('_format') == 'application/json':
        json_object = {
            'title': title,
            'items': items,
        }
        return Response(json.dumps(json_object), mimetype='application/json')
    else:
        return render_template(
            'browse_list.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link, json_link=json_link)


@routes.route('/licence/index.json')
def browse_licenses_json():
    return redirect('/licence/?_format=application/json')


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
        items.append({'uri': url_for('controller.rule_routes', uri=rule['URI']), 'label': rule['LABEL']})
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_list.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)


def view_rule(rule_uri):
    try:
        rule = db_access.get_rule(rule_uri)
        policies = db_access.get_policies_for_rule(rule_uri)
    except ValueError:
        abort(404)
        return
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('view_rule.html', permalink=permalink, rdf_link=rdf_link, json_link=json_link, rule=rule,
                           policies=policies, title=rule['LABEL'])


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
    items = list()
    for action in actions:
        items.append({'uri': url_for('controller.action_routes', uri=action['URI']), 'label': action['LABEL']})
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_list.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)


def view_action(action_uri):
    try:
        action = db_access.get_action(action_uri)
        rules = db_access.get_rules_using_action(action_uri)
    except ValueError:
        abort(404)
        return
    rdf_link = '#!'
    json_link = '#!'
    return render_template('view_action.html', permalink=action['URI'], rdf_link=rdf_link, json_link=json_link,
                           action=action, rules=rules)


@routes.route('/licence/example_licence', methods=['GET'])
def view_licence():
    title = 'Example Licence'
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    logo = '/style/logo.gif'
    return render_template('view_licence.html', title=title, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link, logo=logo)
