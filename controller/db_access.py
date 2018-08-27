import sqlite3
import _conf as conf
from flask import g

"""
DB_ACCESS

A layer providing functions for interacting with the database.
"""


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(conf.DATABASE_PATH)
        db.execute('PRAGMA foreign_keys = 1')
        db.row_factory = sqlite3.Row  # Allows for accessing query results like a dictionary which is more readable
    return db


def query(query_str, args=(), one=False):
    """
    Queries the database

    :param query_str: The query as a string. Use args for adding variables to prevent SQL Injection
    :param args:
    :param one:
    :return:
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query_str, args)
    results = cursor.fetchall()
    conn.commit()
    cursor.close()
    if one:
        return results[0] if results else None
    else:
        return results


def create_policy(policy_uri):
    """
    Creates a new Policy with the given URI
    """
    if policy_exists(policy_uri):
        raise ValueError('A Policy with that URI already exists.')
    query('INSERT INTO POLICY (URI, CREATED) VALUES (?, CURRENT_TIMESTAMP)', (policy_uri, ))


def delete_policy(policy_uri):
    """
    Deletes the Policy with the given URI
    """
    query('DELETE FROM POLICY WHERE URI = ?', (policy_uri,))


def policy_exists(policy_uri):
    """
    Checks whether a Policy with the given URI exists

    :return:    True if the policy exists
                False if the policy does not exist
    """
    return query('SELECT COUNT(1) FROM POLICY WHERE URI = ?', (policy_uri, ), one=True)[0]


def set_policy_attribute(policy_uri, attr, value):
    """
    For a given Policy, set an attribute to the given value

    :param policy_uri:
    :param attr: Permitted attributes - TYPE, LABEL, JURISDICTION, LEGAL_CODE, HAS_VERSION, LANGUAGE, SEE_ALSO, SAME_AS,
                                        COMMENT, LOGO, STATUS
    :param value:
    """
    permitted_attributes = ['TYPE', 'LABEL', 'JURISDICTION', 'LEGAL_CODE', 'HAS_VERSION', 'LANGUAGE', 'SEE_ALSO',
                            'SAME_AS', 'COMMENT', 'LOGO', 'STATUS']
    attr = attr.upper()
    if attr not in permitted_attributes:
        raise ValueError('Attribute \'' + attr + '\' is not permitted.')
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    query_str = 'UPDATE POLICY SET {attr} = ? WHERE URI = ?'.format(attr=attr)
    query(query_str, (value, policy_uri))


def get_policy(policy_uri):
    """
    Retrieve all the relevant information about a Policy, including its attributes and its Rules. Additionally, the
    Actions, Assignors and Assignees for each of those rules.

    :return: A Dictionary containing the following elements:
                URI - string
                TYPE - string
                LABEL - string
                JURISDICTION - string
                LEGAL_CODE - string
                HAS_VERSION - string
                LANGUAGE - string
                SEE_ALSO - string
                SAME_AS - string
                COMMENT - string
                LOGO - string
                CREATED - string
                STATUS - string
                RULES - List of Rules
                    Each Rule is a Dictionary containing the following elements:
                        URI - string
                        TYPE - string
                        LABEL - string
                        ASSIGNORS - List of strings
                        ASSIGNEES - List of strings
                        ACTIONS - List of Actions
                            Each Action is a Dictionary containing the following elements:
                            URI - string
                            LABEL - string
                            DEFINITION - string
    """
    policy_result = query('SELECT * FROM POLICY WHERE URI = ?', (policy_uri,), one=True)
    if policy_result is None:
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    policy = dict(policy_result)
    policy['RULES'] = get_rules_for_policy(policy_uri)
    return policy


def get_all_policies():
    """
    Returns a lists of all Policy URIs
    """
    policies = list()
    for result in query('SELECT URI FROM POLICY'):
        policies.append(result['URI'])
    return policies


def policy_has_rule(policy_uri, rule_uri):
    """
    Checks if the given Policy includes the given Rule
    """
    query_str = 'SELECT COUNT(1) FROM POLICY_HAS_RULE WHERE POLICY_URI = ? AND RULE_URI = ?'
    return query(query_str, (policy_uri, rule_uri), one=True)[0]


def add_asset(asset_uri, policy_uri):
    """
    Assigns an existing Asset to an existing Policy.
    """
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + asset_uri + ' does not exist.')
    if asset_exists(asset_uri):
        raise ValueError('An Asset with that URI already exists.')
    query('INSERT INTO ASSET (URI, POLICY_URI) VALUES (?, ?)', (asset_uri, policy_uri))


def remove_asset(asset_uri):
    """
    Removes an Asset from its Policy
    """
    query('DELETE FROM ASSET WHERE URI = ?', (asset_uri,))


def asset_exists(uri):
    """
    Checks whether an Asset with a given URI has a record in the database

    :return:    True if the asset exists
                False if the asset does not exist
    """
    return query('SELECT COUNT(1) FROM ASSET WHERE URI = ?', (uri,), one=True)[0]


def get_all_assets():
    """
    Returns a list of all Asset URIs
    """
    assets = list()
    for asset in query('SELECT URI FROM ASSET'):
        assets.append(asset['URI'])
    return assets


def create_rule(rule_uri, rule_type, rule_label):
    """
    Creates a new Rule with the given URI and rule type.

    :param rule_uri:
    :param rule_type: Permitted rule types: http://www.w3.org/ns/odrl/2/permission
                                            http://www.w3.org/ns/odrl/2/prohibition
                                            http://www.w3.org/ns/odrl/2/duty
    :param rule_label:
    """
    if rule_exists(rule_uri):
        raise ValueError('A Rule with that URI already exists.')
    if rule_type not in get_permitted_rule_types():
        raise ValueError('Rule type ' + rule_type + ' is not permitted.')
    if not rule_label:
        raise ValueError('Rule must have a label.')
    query('INSERT INTO RULE (URI, TYPE, LABEL) VALUES (?, ?, ?)', (rule_uri, rule_type, rule_label))


def delete_rule(rule_uri):
    """
    Deletes the Rule with the given URI. A Rule can only be deleted if it is not currently assigned to a policy.
    """
    if len(get_policies_for_rule(rule_uri)) > 0:
        raise ValueError('Cannot delete a Rule while it is assigned to a Policy.')
    query('DELETE FROM RULE WHERE URI = ?', (rule_uri,))


def add_rule_to_policy(rule_uri, policy_uri):
    """
    Assigns a Rule to a policy. Policies are made up of many Rules. Rules can be reused in multiple Policies.
    """
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    if policy_has_rule(policy_uri, rule_uri):
        raise ValueError('Rule ' + rule_uri + ' is already included in Policy ' + policy_uri + '.')
    query('INSERT INTO POLICY_HAS_RULE (POLICY_URI, RULE_URI) VALUES (?, ?)', (policy_uri, rule_uri))


def remove_rule_from_policy(rule_uri, policy_uri):
    """
    Removes a Rule from a Policy. The Rule will still exist unless deleted, but is not assigned to that Policy anymore.
    """
    query_str = 'DELETE FROM POLICY_HAS_RULE WHERE RULE_URI=? AND POLICY_URI IN (SELECT URI FROM POLICY WHERE URI=?)'
    query(query_str, (rule_uri, policy_uri))


def get_rules_for_policy(policy_uri):
    """
    Retrieves all the Rules used by a Policy with the given URI.

    :return: A List of Rules
                Each Rule is a Dictionary containing the following elements:
                    URI - string
                    TYPE - string
                    LABEL - string
                    ASSIGNORS - List of strings
                    ASSIGNEES - List of strings
                    ACTIONS - List of Actions
                        Each Action is a Dictionary containing the following elements:
                        URI - string
                        LABEL - string
                        DEFINITION - string
    """
    query_str = '''
        SELECT R.URI, R.TYPE, R.LABEL FROM RULE R, POLICY_HAS_RULE P_R, POLICY P
        WHERE R.URI = P_R.RULE_URI AND P_R.POLICY_URI = P.URI AND P.URI = ?
    '''
    rules = list()
    for rule_result in query(query_str, (policy_uri,)):
        rule = dict(rule_result)
        rule['ACTIONS'] = get_actions_for_rule(rule['URI'])
        rule['ASSIGNORS'] = get_assignors_for_rule(rule['URI'])
        rule['ASSIGNEES'] = get_assignees_for_rule(rule['URI'])
        rules.append(rule)
    return rules


def get_all_rules():
    """
    Returns a list with all Rule URIs
    """
    rules = list()
    for asset in query('SELECT URI FROM RULE'):
        rules.append(asset['URI'])
    return rules


def rule_exists(rule_uri):
    """
    Checks if a Rule with the given URI exists

    :return:    True if the Rule exists
                False if the Rule does not exist
    """
    return query('SELECT COUNT(1) FROM RULE WHERE URI = ?', (rule_uri,), one=True)[0]


def get_permitted_rule_types():
    """
    Returns a list of all the rules types which are permitted

    Should be: http://www.w3.org/ns/odrl/2/permission
               http://www.w3.org/ns/odrl/2/prohibition
               http://www.w3.org/ns/odrl/2/duty
    However, they can be add/removed from the database at will so using this method to check is advised
    """
    permitted_rule_types = list()
    for rule_type in query('SELECT TYPE FROM RULE_TYPE'):
        permitted_rule_types.append(rule_type['TYPE'])
    return permitted_rule_types


def get_policies_for_rule(rule_uri):
    """
    Returns a list of all the Policies which use the Rule given
    """
    policies = list()
    for result in query('SELECT POLICY_URI FROM POLICY_HAS_RULE WHERE RULE_URI = ?', (rule_uri,)):
        policies.append(result['POLICY_URI'])
    return policies


def action_exists(action_uri):
    """
    Checks if an Action with the given URI exists

    :return:    True if the Action exists
                False if the Action does not exist
    """
    return query('SELECT COUNT(1) FROM ACTION WHERE URI = ?', (action_uri,), one=True)[0]


def add_action_to_rule(action_uri, rule_uri):
    """
    Assign an Action to a Rule. Rules can have multiple Actions associated with them, and Actions can be associated with
    multiple Rules
    """
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + str(rule_uri) + ' does not exist.')
    if not action_exists(action_uri):
        raise ValueError('Action with URI ' + action_uri + ' is not permitted.')
    if rule_has_action(rule_uri, action_uri):
        raise ValueError('Rule ' + rule_uri + ' already includes Action ' + action_uri + '.')
    query('INSERT INTO RULE_HAS_ACTION (RULE_URI, ACTION_URI) VALUES (?, ?)', (rule_uri, action_uri))


def remove_action_from_rule(action_uri, rule_uri):
    """
    Removes an Action from a Rule.
    """
    query('DELETE FROM RULE_HAS_ACTION WHERE RULE_URI = ? AND ACTION_URI = ?', (rule_uri, action_uri))


def get_actions_for_rule(rule_uri):
    """
    Returns a list of all the Actions which are assigned to a given Rule
    """
    query_str = '''
        SELECT A.URI, A.LABEL, A.DEFINITION FROM ACTION A, RULE_HAS_ACTION R_A 
        WHERE R_A.RULE_URI = ?
        AND R_A.ACTION_URI = A.URI
    '''
    actions = list()
    for result in query(query_str, (rule_uri,)):
        actions.append(dict(result))
    return actions


def get_rules_using_action(action_id):
    """
    Returns a list of all the Rules which are currently using a given Action
    """
    rules = list()
    query_str = '''
        SELECT R.URI, R.TYPE, R.LABEL, R.rowid
        FROM RULE R, RULE_HAS_ACTION R_A, ACTION A
        WHERE R.URI = R_A.RULE_URI AND R_A.ACTION_URI = A.URI AND A.rowid = ?'''
    for result in query(query_str, (action_id,)):
        rules.append(dict(result))
    return rules


def rule_has_action(rule_uri, action_uri):
    """
    Checks if a Rule has an Action
    """
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ACTION WHERE RULE_URI = ? AND ACTION_URI = ?'
    return query(query_str, (rule_uri, action_uri), one=True)[0]


def get_action(action_id):
    """
    Returns the URI, Label and Definition of an Action given by ID
    """
    result = query('SELECT URI, LABEL, DEFINITION FROM ACTION WHERE rowid = ?', (action_id,), one=True)
    if result is None:
        raise ValueError('Action with ID ' + str(action_id) + ' not found.')
    return result


def get_all_actions():
    """
    Returns a list of all the Actions which are permitted along with their label and definition

    :return A list of Actions
                Each Action is a dictionary with elements: URI, LABEL, DEFINITION
    """
    actions = list()
    for result in query('SELECT URI, LABEL, DEFINITION FROM ACTION'):
        actions.append({'URI': result['URI'], 'LABEL': result['LABEL'], 'DEFINITION': result['DEFINITION']})
    return actions


def add_assignor_to_rule(assignor_uri, rule_uri):
    """
    Add an Assignor to a Rule
    """
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if rule_has_assignor(rule_uri, assignor_uri):
        raise ValueError('Rule ' + rule_uri + ' already has an Assignor with URI ' + assignor_uri + '.')
    query('INSERT INTO ASSIGNOR (ASSIGNOR_URI, RULE_URI) VALUES (?, ?)', (assignor_uri, rule_uri))


def remove_assignor_from_rule(assignor_uri, rule_uri):
    """
    Remove an Assignor from a Rule
    """
    query('DELETE FROM ASSIGNOR WHERE RULE_URI = ? AND ASSIGNOR_URI = ?', (rule_uri, assignor_uri))


def rule_has_assignor(rule_uri, assignor_uri):
    """
    Checks if a Rule has an Assignor with the given URI

    :return:    True if the Rule has the Assignor
                False if the Rule does not have the Assignor
    """
    query_str = 'SELECT COUNT(1) FROM ASSIGNOR WHERE RULE_URI = ? AND ASSIGNOR_URI = ?'
    return query(query_str, (rule_uri, assignor_uri), one=True)[0]


def get_assignors_for_rule(rule_uri):
    """
    Returns a list of URIs for all Assignors associated with a given Rule
    """
    assignors = list()
    for result in query('SELECT ASSIGNOR_URI FROM ASSIGNOR WHERE RULE_URI = ?', (rule_uri,)):
        assignors.append(result['ASSIGNOR_URI'])
    return assignors


def add_assignee_to_rule(assignee_uri, rule_uri):
    """
    Add an Assignee to a Rule
    """
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if rule_has_assignee(rule_uri, assignee_uri):
        raise ValueError('Rule ' + rule_uri + ' already has an Assignee with URI ' + assignee_uri + '.')
    query('INSERT INTO ASSIGNEE (ASSIGNEE_URI, RULE_URI) VALUES (?, ?)', (assignee_uri, rule_uri))


def remove_assignee_from_rule(assignee_uri, rule_uri):
    """
    Remove an Assignee from a Rule
    """
    query('DELETE FROM ASSIGNEE WHERE RULE_URI = ? AND ASSIGNEE_URI = ?', (rule_uri, assignee_uri))


def rule_has_assignee(rule_uri, assignee_uri):
    """
    Checks if a Rule has an Assignee with the given URI

    :return:    True if the Rule has the Assignee
                False if the Rule does not have the Assignee
    """
    query_str = 'SELECT COUNT(1) FROM ASSIGNEE WHERE RULE_URI = ? AND ASSIGNEE_URI = ?'
    return query(query_str, (rule_uri, assignee_uri), one=True)[0]


def get_assignees_for_rule(rule_uri):
    """
    Returns a list of URIs for all Assignees associated with a given Rule
    """
    assignees = list()
    for result in query('SELECT ASSIGNEE_URI FROM ASSIGNEE WHERE RULE_URI = ?', (rule_uri,)):
        assignees.append(result['ASSIGNEE_URI'])
    return assignees
