#
#   Rename this file __init__.py and replace variable placeholders for use
#
#   DO NOT commit your own __init__.py file to a public repository!
#
from os import path

APP_DIR = path.dirname(path.dirname(path.realpath(__file__)))
TEMPLATES_DIR = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'view', 'templates')
STATIC_DIR = path.join(APP_DIR, 'view', 'style')
LOGFILE = APP_DIR + '/flask.log'
DEBUG = True

PAGE_SIZE_DEFAULT = 100
PAGE_SIZE_MAX = 10000

# Database config
DATABASE_PATH = {{YOUR_DB_LOCATION}}

# The base uri for all uris minted by this application
BASE_URI = {{YOUR_URI}}
# The base uri for building the permalinks in this application
PERMALINK_BASE = {{YOUR_PERMALINK_BASE}}
# any password-like string, for session stuff
SECRET_KEY = {{YOUR_SECRET_KEY}}

# For emailing messages sent via the contact form in the About page
MAILJET_SECRETS = {
    'API_ENDPOINT': {{YOUR_MAILJET_ENDPOINT}},
    'MJ_APIKEY_PUBLIC': {{YOUR_PUBLIC_KEY}},
    'MJ_APIKEY_PRIVATE': {{YOUR_PRIVATE_KEY}}
}
MAILJET_EMAIL_SENDER = {{YOUR_SENDER_EMAIL}}  # Who the emails will appear to come from
MAILJET_EMAIL_RECEIVERS = [{{YOUR_RECEIVE_EMAIL}}]  # Who will receive the emails

# Register username and password to create licences for this system
USERNAME = {{YOUR_USERNAME}}
PASSWORD = {{YOUR_PASSWORD}}