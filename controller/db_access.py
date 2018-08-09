import sqlite3
import _conf as conf
import re

# DB
conn = sqlite3.connect(conf.DATABASE_PATH)
conn.execute('PRAGMA foreign_keys = 1')
conn.row_factory = sqlite3.Row  # Allows for accessing query results like a dictionary which is more readable
cursor = conn.cursor()


def create_policy(uri):
    uri = str(uri)
    if not is_valid_uri(uri):
        raise ValueError('Not a valid URI: ' + uri)
    if policy_exists(uri):
        raise ValueError('A Policy with that URI already exists.')
    cursor.execute('INSERT INTO POLICY (URI) VALUES ("{uri:s}");'.format(uri=uri))
    conn.commit()
    return cursor.lastrowid


def is_valid_uri(uri):
    return True if re.match('\w+:(/?/?)[^\s]+', uri) else False


def set_policy_attribute(uri, attr, value):
    permitted_attributes = ['TYPE', 'LABEL', 'JURISDICTION', 'LEGAL_CODE', 'HAS_VERSION', 'LANGUAGE', 'SEE_ALSO',
                            'SAME_AS', 'COMMENT', 'LOGO', 'STATUS']
    if attr not in permitted_attributes:
        raise ValueError('Attribute \'' + attr + '\' is not permitted.')
    if not policy_exists(uri):
        raise ValueError('Policy with URI ' + uri + ' does not exist.')
    conn.execute(
        'UPDATE POLICY SET {attr:s} = "{value:s}" WHERE URI = "{uri:s}";'.format(attr=attr, value=value, uri=uri)
    )
    conn.commit()


def policy_exists(uri):
    cursor.execute('SELECT COUNT(1) FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    return cursor.fetchone()[0]


def delete_policy(uri):
    conn.execute('DELETE FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    conn.commit()


def get_policy(uri):
    if not policy_exists(uri):
        raise ValueError('Policy with URI ' + uri + 'does not exist.')
    cursor.execute('SELECT * FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    return dict(cursor.fetchone())


def add_asset(uri, policy_uri):
    uri = str(uri)
    if not is_valid_uri(uri):
        raise ValueError('Not a valid URI: ' + uri)
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + uri + 'does not exist.')
    if asset_exists(uri):
        raise ValueError('An Asset with that URI already exists.')
    cursor.execute('SELECT ID FROM POLICY WHERE URI="{policy_uri:s}"'.format(policy_uri=policy_uri))
    policy_id = cursor.fetchone()['ID']
    cursor.execute(
        'INSERT INTO ASSET (URI, POLICY_ID) VALUES ("{uri:s}", {policy_id})'.format(uri=uri, policy_id=policy_id)
    )
    conn.commit()
    return cursor.lastrowid


def asset_exists(uri):
    cursor.execute('SELECT COUNT(1) FROM ASSET WHERE URI = "{uri:s}"'.format(uri=uri))
    return cursor.fetchone()[0]


def remove_asset(uri):
    conn.execute('DELETE FROM ASSET WHERE URI = "{uri:s}"'.format(uri=uri))
    conn.commit()


def create_rule(rule_type):
    try:
        cursor.execute('INSERT INTO RULE (TYPE) VALUES ("{rule_type:s}")'.format(rule_type=rule_type))
    except sqlite3.IntegrityError:
        raise ValueError('Rule type ' + rule_type + ' is not permitted.')
    conn.commit()
    return cursor.lastrowid


def create_party(uri):
    uri = str(uri)
    if not is_valid_uri(uri):
        raise ValueError('Not a valid URI: ' + uri)
    if party_exists(uri):
        raise ValueError('A Party with that URI already exists.')
    cursor.execute('INSERT INTO PARTY (URI) VALUES ("{uri:s}")'.format(uri=uri))
    conn.commit()
    return cursor.lastrowid


def party_exists(uri):
    cursor.execute('SELECT COUNT(1) FROM PARTY WHERE URI = "{uri:s}"'.format(uri=uri))
    return cursor.fetchone()[0]


def delete_party(uri):
    conn.execute('DELETE FROM PARTY WHERE URI = "{uri:s}"'.format(uri=uri))
    conn.commit()


def rule_exists(rule_id):
    cursor.execute('SELECT COUNT(1) FROM RULE WHERE ID = {id}'.format(id=rule_id))
    return cursor.fetchone()[0]


def add_action_to_rule(rule_id, action_uri):
    if not rule_exists(rule_id):
        raise ValueError('Rule with ID ' + str(rule_id) + ' does not exist.')
    cursor.execute('SELECT ID FROM ACTION WHERE URI = "{uri:s}"'.format(uri=action_uri))
    result = cursor.fetchone()
    if result is None:
        raise ValueError('Action with URI ' + action_uri + ' does not exist.')
    action_id = result['ID']
    query = 'INSERT INTO RULE_HAS_ACTION (RULE_ID, ACTION_ID) VALUES ({rule_id}, {action_id})'
    conn.execute(query.format(rule_id=rule_id, action_id=action_id))
    conn.commit()


def remove_action_from_rule(rule_id, action_uri):
    cursor.execute('SELECT ID FROM ACTION WHERE URI = "{uri:s}"'.format(uri=action_uri))
    result = cursor.fetchone()
    if result is None:
        raise ValueError('Action with URI ' + action_uri + ' does not exist.')
    action_id = result['ID']
    query = 'DELETE FROM RULE_HAS_ACTION WHERE RULE_ID = {rule_id} AND ACTION_ID={action_id}'
    conn.execute(query.format(rule_id=rule_id, action_id=action_id))
    conn.commit()


def get_party_id(uri):
    cursor.execute('SELECT ID FROM PARTY WHERE URI = "{uri}"'.format(uri=uri))
    result = cursor.fetchone()
    if result is None:
        raise ValueError('Party with URI ' + uri + ' does not exist.')
    return result['ID']


def add_assignor_to_rule(party_uri, rule_id):
    if not rule_exists(rule_id):
        raise ValueError('Rule with ID ' + str(rule_id) + ' does not exist.')
    party_id = get_party_id(party_uri)
    query = 'INSERT INTO RULE_HAS_ASSIGNOR (PARTY_ID, RULE_ID) VALUES ({party_id}, {rule_id})'
    conn.execute(query.format(party_id=party_id, rule_id=rule_id))
    conn.commit()


def remove_assignor_from_rule(party_uri, rule_id):
    query = '''
        DELETE FROM RULE_HAS_ASSIGNOR 
        WHERE RULE_ID= {rule_id} AND PARTY_ID IN (
            SELECT ID FROM PARTY WHERE URI = "{party_uri}"
        )
    '''
    conn.execute(query.format(party_uri=party_uri, rule_id=rule_id))
    conn.commit()


def add_assignee_to_rule(party_uri, rule_id):
    if not rule_exists(rule_id):
        raise ValueError('Rule with ID ' + str(rule_id) + ' does not exist.')
    party_id = get_party_id(party_uri)
    query = 'INSERT INTO RULE_HAS_ASSIGNEE (PARTY_ID, RULE_ID) VALUES ({party_id}, {rule_id})'
    conn.execute(query.format(party_id=party_id, rule_id=rule_id))
    conn.commit()


def remove_assignee_from_rule(party_uri, rule_id):
    query = '''
        DELETE FROM RULE_HAS_ASSIGNEE
        WHERE RULE_ID= {rule_id} AND PARTY_ID IN (
            SELECT ID FROM PARTY WHERE URI = "{party_uri}"
        )
    '''
    conn.execute(query.format(party_uri=party_uri, rule_id=rule_id))
    conn.commit()
