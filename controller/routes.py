from flask import Blueprint, render_template, request, redirect, url_for
import _conf as conf
import sqlite3

routes = Blueprint('controller', __name__)


#
#   pages
#
@routes.route('/')
def home():
    return render_template('page_home.html')


# DB
conn = sqlite3.connect(conf.DATABASE_PATH)
conn.execute('PRAGMA foreign_keys = 1')
cursor = conn.cursor()
cursor.execute('SELECT * FROM RULE_TYPE')
print('Rule Types', cursor.fetchall())

