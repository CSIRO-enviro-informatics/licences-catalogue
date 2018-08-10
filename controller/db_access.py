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


def policy_exists(uri):
    cursor.execute('SELECT COUNT(1) FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    return cursor.fetchone()[0]


def delete_policy(uri):
    conn.execute('DELETE FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    conn.commit()


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


def get_policy(policy_uri):
    cursor.execute('SELECT * FROM POLICY WHERE URI = "{uri}"'.format(uri=policy_uri))
    policy_result = cursor.fetchone()
    if policy_result is None:
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    policy = dict(policy_result)
    policy['RULES'] = get_rules_for_policy(policy_uri)
    return policy


def get_all_policies():
    # Returns a list of policies given by uri
    cursor.execute('SELECT URI FROM POLICY')
    policies = list()
    for result in cursor.fetchall():
        policies.append(result['URI'])
    return policies


def add_asset(uri, policy_uri):
    uri = str(uri)
    if not is_valid_uri(uri):
        raise ValueError('Not a valid URI: ' + uri)
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + uri + ' does not exist.')
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


def get_asset(asset_uri):
    # Returns a dictionary with all the attributes of that asset
    cursor.execute('SELECT * FROM ASSET WHERE URI = "{asset_uri}"'.format(asset_uri=asset_uri))
    return dict(cursor.fetchone())


def get_all_assets():
    # Returns a list of all asset uris
    cursor.execute('SELECT URI FROM ASSET')
    results = cursor.fetchall()
    assets = list()
    for asset in results:
        assets.append(asset['URI'])
    return assets


def create_rule(rule_type):
    try:
        cursor.execute('INSERT INTO RULE (TYPE) VALUES ("{rule_type:s}")'.format(rule_type=rule_type))
    except sqlite3.IntegrityError:
        raise ValueError('Rule type ' + rule_type + ' is not permitted.')
    conn.commit()
    return cursor.lastrowid


def delete_rule(rule_id):
    try:
        conn.execute('DELETE FROM RULE WHERE ID = {id}'.format(id=rule_id))
    except sqlite3.IntegrityError:
        raise ValueError('Cannot delete a Rule while it is assigned to a Policy.')
    conn.commit()


def add_rule_to_policy(rule_id, policy_uri):
    if not rule_exists(rule_id):
        raise ValueError('Rule with ID ' + str(rule_id) + ' does not exist.')
    cursor.execute('SELECT ID FROM POLICY WHERE URI = "{uri}"'.format(uri=policy_uri))
    result = cursor.fetchone()
    if result is None:
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    policy_id = result['ID']
    query_str = 'INSERT INTO POLICY_HAS_RULE (POLICY_ID, RULE_ID) VALUES ({policy_id}, {rule_id})'
    conn.execute(query_str.format(policy_id=policy_id, rule_id=rule_id))


def remove_rule_from_policy(rule_id, policy_uri):
    conn.execute('''
        DELETE FROM POLICY_HAS_RULE
        WHERE RULE_ID = {rule_id} AND POLICY_ID IN (
            SELECT ID FROM POLICY WHERE URI = "{policy_uri}"
        )'''.format(rule_id=rule_id, policy_uri=policy_uri))


def get_rules_for_policy(policy_uri):
    query_str = '''
        SELECT R.ID, R.TYPE FROM RULE R, POLICY_HAS_RULE P_R, POLICY P
        WHERE R.ID = P_R.RULE_ID AND P_R.POLICY_ID = P.ID AND P.URI = "{policy_uri}"
    '''
    cursor.execute(query_str.format(policy_uri=policy_uri))
    rules_results = cursor.fetchall()
    if len(rules_results) == 0:
        return None
    else:
        rules = list()
        for rule_result in rules_results:
            rule = dict(rule_result)
            rule['ACTIONS'] = get_actions_for_rule(rule['ID'])
            rule['ASSIGNORS'] = get_assignors_for_rule(rule['ID'])
            rule['ASSIGNEES'] = get_assignees_for_rule(rule['ID'])
            rules.append(rule)
        return rules


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
    query_str = 'INSERT INTO RULE_HAS_ACTION (RULE_ID, ACTION_ID) VALUES ({rule_id}, {action_id})'
    conn.execute(query_str.format(rule_id=rule_id, action_id=action_id))
    conn.commit()


def remove_action_from_rule(rule_id, action_uri):
    cursor.execute('SELECT ID FROM ACTION WHERE URI = "{uri:s}"'.format(uri=action_uri))
    result = cursor.fetchone()
    if result is None:
        raise ValueError('Action with URI ' + action_uri + ' does not exist.')
    action_id = result['ID']
    query_str = 'DELETE FROM RULE_HAS_ACTION WHERE RULE_ID = {rule_id} AND ACTION_ID={action_id}'
    conn.execute(query_str.format(rule_id=rule_id, action_id=action_id))
    conn.commit()


def get_actions_for_rule(rule_id):
    cursor.execute('''
        SELECT A.ID, A.LABEL, A.URI, A.DEFINITION FROM ACTION A, RULE_HAS_ACTION R_A 
        WHERE R_A.RULE_ID = {rule_id}
        AND R_A.ACTION_ID = A.ID
    '''.format(rule_id=rule_id))
    results = cursor.fetchall()
    actions = list()
    for result in results:
        actions.append(dict(result))
    return actions


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
    query_str = 'INSERT INTO RULE_HAS_ASSIGNOR (PARTY_ID, RULE_ID) VALUES ({party_id}, {rule_id})'
    conn.execute(query_str.format(party_id=party_id, rule_id=rule_id))
    conn.commit()


def remove_assignor_from_rule(party_uri, rule_id):
    query_str = '''
        DELETE FROM RULE_HAS_ASSIGNOR 
        WHERE RULE_ID= {rule_id} AND PARTY_ID IN (
            SELECT ID FROM PARTY WHERE URI = "{party_uri}"
        )
    '''
    conn.execute(query_str.format(party_uri=party_uri, rule_id=rule_id))
    conn.commit()


def get_assignors_for_rule(rule_id):
    cursor.execute('''
        SELECT P.URI FROM RULE_HAS_ASSIGNOR R_A, PARTY P 
        WHERE R_A.RULE_ID = {rule_id}
        AND R_A.PARTY_ID = P.ID
    '''.format(rule_id=rule_id))
    assignors = list()
    for result in cursor.fetchall():
        assignors.append(result['URI'])
    return assignors


def add_assignee_to_rule(party_uri, rule_id):
    if not rule_exists(rule_id):
        raise ValueError('Rule with ID ' + str(rule_id) + ' does not exist.')
    party_id = get_party_id(party_uri)
    query_str = 'INSERT INTO RULE_HAS_ASSIGNEE (PARTY_ID, RULE_ID) VALUES ({party_id}, {rule_id})'
    conn.execute(query_str.format(party_id=party_id, rule_id=rule_id))
    conn.commit()


def remove_assignee_from_rule(party_uri, rule_id):
    query_str = '''
        DELETE FROM RULE_HAS_ASSIGNEE
        WHERE RULE_ID= {rule_id} AND PARTY_ID IN (
            SELECT ID FROM PARTY WHERE URI = "{party_uri}"
        )
    '''
    conn.execute(query_str.format(party_uri=party_uri, rule_id=rule_id))
    conn.commit()


def get_assignees_for_rule(rule_id):
    cursor.execute('''
        SELECT P.URI FROM RULE_HAS_ASSIGNEE R_A, PARTY P 
        WHERE R_A.RULE_ID = {rule_id}
        AND R_A.PARTY_ID = P.ID
    '''.format(rule_id=rule_id))
    assignees = list()
    for result in cursor.fetchall():
        assignees.append(result['URI'])
    return assignees


def query(query_str):
    cursor.execute(query_str)
    return cursor.fetchall()
