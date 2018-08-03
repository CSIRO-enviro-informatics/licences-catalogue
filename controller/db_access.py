import sqlite3
import _conf as conf
import re

# DB
conn = sqlite3.connect(conf.DATABASE_PATH)
conn.execute('PRAGMA foreign_keys = 1')
cursor = conn.cursor()


def create_policy(uri):
    uri = str(uri)
    if not is_valid_uri(uri):
        raise ValueError('Not a valid URI: ' + uri)
    try:
        cursor.execute('INSERT INTO POLICY (URI) VALUES ("{uri:s}");'.format(uri=uri))
    except sqlite3.IntegrityError:
        raise ValueError('A Policy with that URI already exists.')
    conn.commit()
    return cursor.lastrowid


def is_valid_uri(uri):
    return True if re.match('\w+:(/?/?)[^\s]+', uri) else False


def set_policy_type(uri, policy_type):
    cursor.execute('UPDATE POLICY SET TYPE = "{type:s}" WHERE URI = "{uri:s}";'.format(type=policy_type, uri=uri))
    conn.commit()
