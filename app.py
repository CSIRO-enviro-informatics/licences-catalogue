import logging
import _conf as conf
from flask import Flask, g, session
from controller import routes
from uuid import uuid4
from flask_login import LoginManager
from model.user import User

app = Flask(__name__, template_folder=conf.TEMPLATES_DIR, static_folder=conf.STATIC_DIR)
app.secret_key = conf.SECRET_KEY
app.register_blueprint(routes.routes)


# flask-login
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """
    Callback function to load a Flask-Login user object
    """
    return User(user_id)


# Closes connection to database when exiting application. See db_access.py for details.
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Generate token for Cross-Site Request Forgery protection
def generate_csrf_token():
    if '_csrf_token' not in session:
        session['_csrf_token'] = str(uuid4())
    return session['_csrf_token']


app.jinja_env.globals['csrf_token'] = generate_csrf_token


# Run the Flask app
if __name__ == '__main__':
    logging.basicConfig(filename=conf.LOGFILE,
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S',
                        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s %(message)s')
    app.run(debug=conf.DEBUG, use_reloader=False)
