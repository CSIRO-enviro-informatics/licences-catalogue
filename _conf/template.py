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

# URI minting
BASE_URI = {{YOUR_URI}}
