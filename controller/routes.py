from flask import Blueprint, render_template, request, redirect, url_for, abort
from controller import db_access
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


@routes.route('/licence', methods=['GET'])
def browse_licences():
    title = 'Licence Register'
    items = [
        {'label': 'Licence #1', 'link': url_for('controller.view_licence')},
        {'label': 'Licence #2', 'link': url_for('controller.view_licence')},
        {'label': 'Licence #3', 'link': url_for('controller.view_licence')}
    ]
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_list.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)


@routes.route('/rule', methods=['GET'])
def browse_rules():
    title = 'Rule Register'
    items = [
        {'label': 'Rule #1', 'link': '#!'},
        {'label': 'Rule #2', 'link': '#!'},
        {'label': 'Rule #3', 'link': '#!'}
    ]
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_list.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)


@routes.route('/action', methods=['GET'])
def browse_actions():
    title = 'Action Register'
    actions = db_access.get_all_actions()
    items = list()
    for action in actions:
        items.append({'link': url_for('controller.view_action', action_id=action['rowid']), 'label': action['LABEL']})
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_list.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)


@routes.route('/licence/example_licence', methods=['GET'])
def view_licence():
    title = 'Example Licence'
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    logo = '/style/logo.gif'
    return render_template('view_licence.html', title=title, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link, logo=logo)


@routes.route('/rule/<rule_id>', methods=['GET'])
def view_rule(rule_id):
    rule_uri = conf.BASE_URI + 'rule/' + rule_id
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
                           policies=policies)


@routes.route('/action/<action_id>', methods=['GET'])
def view_action(action_id):
    try:
        action = db_access.get_action(action_id)
        rules = db_access.get_rules_using_action(action_id)
    except ValueError:
        abort(404)
        return
    rdf_link = '#!'
    json_link = '#!'
    return render_template('view_action.html', permalink=action['URI'], rdf_link=rdf_link, json_link=json_link,
                           action=action, rules=rules)
