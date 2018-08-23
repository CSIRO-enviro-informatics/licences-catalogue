from flask import Blueprint, render_template, request, redirect, url_for

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
        {'label': 'Licence #1', 'link': '#!'},
        {'label': 'Licence #2', 'link': '#!'},
        {'label': 'Licence #3', 'link': '#!'}
    ]
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_template.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
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
    return render_template('browse_template.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)


@routes.route('/action', methods=['GET'])
def browse_actions():
    title = 'Action Register'
    items = [
        {'label': 'Action #1', 'link': '#!'},
        {'label': 'Action #2', 'link': '#!'},
        {'label': 'Action #3', 'link': '#!'}
    ]
    permalink = 'https://github.com/CSIRO-enviro-informatics/policies-catalogue'
    rdf_link = '#!'
    json_link = '#!'
    return render_template('browse_template.html', title=title, items=items, permalink=permalink, rdf_link=rdf_link,
                           json_link=json_link)
