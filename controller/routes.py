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
    return render_template('browse_licences.html')
