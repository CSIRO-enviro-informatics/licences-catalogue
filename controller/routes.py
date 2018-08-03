from flask import Blueprint, render_template, request, redirect, url_for

routes = Blueprint('controller', __name__)


#
#   pages
#
@routes.route('/')
def home():
    return render_template('page_home.html')


