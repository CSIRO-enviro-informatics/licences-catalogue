import sqlite3
import _conf as conf

# DB
conn = sqlite3.connect(conf.DATABASE_PATH)
conn.execute('PRAGMA foreign_keys = 1')
conn.row_factory = sqlite3.Row  # Allows for accessing query results like a dictionary which is more readable
cursor = conn.cursor()


def create_policy(uri):
    if policy_exists(uri):
        raise ValueError('A Policy with that URI already exists.')
    cursor.execute('INSERT INTO POLICY (URI) VALUES ("{uri:s}");'.format(uri=uri))
    conn.commit()


def delete_policy(uri):
    conn.execute('DELETE FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    conn.commit()


def policy_exists(uri):
    cursor.execute('SELECT COUNT(1) FROM POLICY WHERE URI = "{uri:s}"'.format(uri=uri))
    return cursor.fetchone()[0]


def set_policy_attribute(uri, attr, value):
    permitted_attributes = ['TYPE', 'LABEL', 'JURISDICTION', 'LEGAL_CODE', 'HAS_VERSION', 'LANGUAGE', 'SEE_ALSO',
                            'SAME_AS', 'COMMENT', 'LOGO', 'STATUS']
    attr = attr.upper()
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
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + uri + ' does not exist.')
    if asset_exists(uri):
        raise ValueError('An Asset with that URI already exists.')
    cursor.execute(
        'INSERT INTO ASSET (URI, POLICY_URI) VALUES ("{uri}", "{policy_uri}")'.format(uri=uri, policy_uri=policy_uri)
    )
    conn.commit()


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


def create_rule(uri, rule_type):
    if rule_exists(uri):
        raise ValueError('A Rule with that URI already exists.')
    try:
        query_str = 'INSERT INTO RULE (URI, TYPE) VALUES ("{uri}", "{rule_type}")'
        cursor.execute(query_str.format(uri=uri, rule_type=rule_type))
    except sqlite3.IntegrityError:
        raise ValueError('Rule type ' + rule_type + ' is not permitted.')
    conn.commit()


def delete_rule(rule_uri):
    try:
        conn.execute('DELETE FROM RULE WHERE URI = "{uri}"'.format(uri=rule_uri))
    except sqlite3.IntegrityError:
        raise ValueError('Cannot delete a Rule while it is assigned to a Policy.')
    conn.commit()


def add_rule_to_policy(rule_uri, policy_uri):
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + str(rule_uri) + ' does not exist.')
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    query_str = 'INSERT INTO POLICY_HAS_RULE (POLICY_URI, RULE_URI) VALUES ("{policy_uri}", "{rule_uri}")'
    conn.execute(query_str.format(policy_uri=policy_uri, rule_uri=rule_uri))


def remove_rule_from_policy(rule_uri, policy_uri):
    conn.execute('''
        DELETE FROM POLICY_HAS_RULE
        WHERE RULE_URI = "{rule_uri}" AND POLICY_URI IN (
            SELECT URI FROM POLICY WHERE URI = "{policy_uri}"
        )'''.format(rule_uri=rule_uri, policy_uri=policy_uri))


def get_rules_for_policy(policy_uri):
    query_str = '''
        SELECT R.URI, R.TYPE FROM RULE R, POLICY_HAS_RULE P_R, POLICY P
        WHERE R.URI = P_R.RULE_URI AND P_R.POLICY_URI = P.URI AND P.URI = "{policy_uri}"
    '''
    cursor.execute(query_str.format(policy_uri=policy_uri))
    rules_results = cursor.fetchall()
    if len(rules_results) == 0:
        return None
    else:
        rules = list()
        for rule_result in rules_results:
            rule = dict(rule_result)
            rule['ACTIONS'] = get_actions_for_rule(rule['URI'])
            rule['ASSIGNORS'] = get_assignors_for_rule(rule['URI'])
            rule['ASSIGNEES'] = get_assignees_for_rule(rule['URI'])
            rules.append(rule)
        return rules


def create_party(uri):
    if party_exists(uri):
        raise ValueError('A Party with that URI already exists.')
    cursor.execute('INSERT INTO PARTY (URI) VALUES ("{uri:s}")'.format(uri=uri))
    conn.commit()


def party_exists(uri):
    cursor.execute('SELECT COUNT(1) FROM PARTY WHERE URI = "{uri:s}"'.format(uri=uri))
    return cursor.fetchone()[0]


def delete_party(uri):
    conn.execute('DELETE FROM PARTY WHERE URI = "{uri:s}"'.format(uri=uri))
    conn.commit()


def rule_exists(rule_uri):
    cursor.execute('SELECT COUNT(1) FROM RULE WHERE URI = "{uri}"'.format(uri=rule_uri))
    return cursor.fetchone()[0]


def action_exists(action_uri):
    cursor.execute('SELECT COUNT(1) FROM ACTION WHERE URI = "{uri}"'.format(uri=action_uri))
    return cursor.fetchone()[0]


def add_action_to_rule(action_uri, rule_uri):
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + str(rule_uri) + ' does not exist.')
    if not action_exists(action_uri):
        raise ValueError('Action with URI ' + action_uri + ' is not permitted.')
    query_str = 'INSERT INTO RULE_HAS_ACTION (RULE_URI, ACTION_URI) VALUES ("{rule_uri}", "{action_uri}")'
    conn.execute(query_str.format(rule_uri=rule_uri, action_uri=action_uri))
    conn.commit()


def remove_action_from_rule(action_uri, rule_uri):
    query_str = 'DELETE FROM RULE_HAS_ACTION WHERE RULE_URI = "{rule_uri}" AND ACTION_URI = "{action_uri}"'
    conn.execute(query_str.format(rule_uri=rule_uri, action_uri=action_uri))
    conn.commit()


def get_actions_for_rule(rule_uri):
    cursor.execute('''
        SELECT A.URI, A.LABEL, A.DEFINITION FROM ACTION A, RULE_HAS_ACTION R_A 
        WHERE R_A.RULE_URI = "{rule_uri}"
        AND R_A.ACTION_URI = A.URI
    '''.format(rule_uri=rule_uri))
    results = cursor.fetchall()
    actions = list()
    for result in results:
        actions.append(dict(result))
    return actions


def add_assignor_to_rule(party_uri, rule_uri):
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    query_str = 'INSERT INTO RULE_HAS_ASSIGNOR (PARTY_URI, RULE_URI) VALUES ("{party_uri}", "{rule_uri}")'
    try:
        conn.execute(query_str.format(party_uri=party_uri, rule_uri=rule_uri))
    except sqlite3.IntegrityError:
        raise ValueError('Party with URI ' + party_uri + ' does not exist.')
    conn.commit()


def remove_assignor_from_rule(party_uri, rule_uri):
    query_str = 'DELETE FROM RULE_HAS_ASSIGNOR WHERE RULE_URI = "{rule_uri}" AND PARTY_URI = "{party_uri}"'
    conn.execute(query_str.format(party_uri=party_uri, rule_uri=rule_uri))
    conn.commit()


def get_assignors_for_rule(rule_uri):
    cursor.execute('SELECT PARTY_URI FROM RULE_HAS_ASSIGNOR WHERE RULE_URI = "{rule_uri}"'.format(rule_uri=rule_uri))
    assignors = list()
    for result in cursor.fetchall():
        assignors.append(result['PARTY_URI'])
    return assignors


def add_assignee_to_rule(party_uri, rule_uri):
    if not party_exists(party_uri):
        raise ValueError('Party with URI ' + party_uri + ' does not exist.')
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    query_str = 'INSERT INTO RULE_HAS_ASSIGNEE (PARTY_URI, RULE_URI) VALUES ("{party_uri}", "{rule_uri}")'
    conn.execute(query_str.format(party_uri=party_uri, rule_uri=rule_uri))
    conn.commit()


def remove_assignee_from_rule(party_uri, rule_uri):
    query_str = 'DELETE FROM RULE_HAS_ASSIGNEE WHERE RULE_URI = "{rule_uri}" AND PARTY_URI = "{party_uri}"'
    conn.execute(query_str.format(party_uri=party_uri, rule_uri=rule_uri))
    conn.commit()


def get_assignees_for_rule(rule_uri):
    cursor.execute('SELECT PARTY_URI FROM RULE_HAS_ASSIGNEE WHERE RULE_URI = "{rule_uri}"'.format(rule_uri=rule_uri))
    assignees = list()
    for result in cursor.fetchall():
        assignees.append(result['PARTY_URI'])
    return assignees


def get_permitted_rule_types():
    cursor.execute('SELECT TYPE FROM RULE_TYPE')
    return list(cursor.fetchall())


def get_permitted_rule_types():
    cursor.execute('SELECT TYPE FROM RULE_TYPE')
    permitted_rule_types = list()
    for rule_type in cursor.fetchall():
        permitted_rule_types.append(rule_type['TYPE'])
    return permitted_rule_types


def query(query_str):
    cursor.execute(query_str)
    return cursor.fetchall()
