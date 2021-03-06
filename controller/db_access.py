import sqlite3
import _conf as conf
from flask import g
import os

"""
DB_ACCESS

A layer providing functions for interacting with the database.
Database connection is stored in a Flask global variable otherwise Flask complains about threads.
For database access while Flask is not running, use offline_db_access.py
commit_db() or rollback_db() MUST be called when all changes are done or database will be locked to future changes.
"""


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        os.makedirs(os.path.dirname(conf.DATABASE_PATH), exist_ok=True)
        db = g._database = sqlite3.connect(conf.DATABASE_PATH)
        db.execute('PRAGMA foreign_keys = 1')
        db.row_factory = sqlite3.Row  # Allows for accessing query results like a dictionary which is more readable
    return db


def update_db(query_str, args=()):
    """
    Submits a query to update or insert something in the database.

    :param query_str: The query as a string. Use args for including variables to prevent SQL Injection
    :param args:
    :return: The most recent rowid
    """
    cursor = get_db().cursor()
    cursor.execute(query_str, args)
    return cursor.lastrowid


def query_db(query_str, args=(), one=False):
    """
    Queries the database

    :param query_str: The query as a string.
    :param args: Use for adding variables to prevent SQL Injection
    :param one: True if the first result should be returned, False if all results should be returned
    :return: The results of the query
    """
    cursor = get_db().cursor()
    cursor.execute(query_str, args)
    results = cursor.fetchall()
    if one:
        return results[0] if results else None
    else:
        return results


def commit_db():
    conn = get_db()
    conn.commit()


def rollback_db():
    conn = get_db()
    conn.rollback()
    conn.commit()


def create_policy(policy_uri):
    # Creates a new Policy with the given URI
    if policy_exists(policy_uri):
        raise ValueError('A Policy with that URI already exists.')
    query_db('INSERT INTO POLICY (URI, CREATED) VALUES (?, CURRENT_TIMESTAMP)', (policy_uri,))


def delete_policy(policy_uri):
    # Deletes the Policy with the given URI
    query_db('DELETE FROM POLICY WHERE URI = ?', (policy_uri,))


def policy_exists(policy_uri):
    """
    Checks whether a Policy with the given URI exists

    :return:    True if the policy exists
                False if the policy does not exist
    """
    return query_db('SELECT COUNT(1) FROM POLICY WHERE URI = ?', (policy_uri,), one=True)[0]


def set_policy_attribute(policy_uri, attr, value):
    """
    For a given Policy, set an attribute to the given value

    :param policy_uri:
    :param attr: Permitted attributes - TYPE, LABEL, JURISDICTION, LEGAL_CODE, HAS_VERSION, LANGUAGE, SEE_ALSO, SAME_AS,
                                        COMMENT, LOGO, STATUS, CREATOR
    :param value:
    """
    permitted_attributes = ['TYPE', 'LABEL', 'JURISDICTION', 'LEGAL_CODE', 'HAS_VERSION', 'LANGUAGE', 'SEE_ALSO',
                            'SAME_AS', 'COMMENT', 'LOGO', 'STATUS', 'CREATOR']
    attr = attr.upper()
    if attr not in permitted_attributes:
        raise ValueError('Attribute \'' + attr + '\' is not permitted.')
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    query_str = 'UPDATE POLICY SET {attr} = ? WHERE URI = ?'.format(attr=attr)
    query_db(query_str, (value, policy_uri))


def get_policy(policy_uri):
    """
    Retrieve all the relevant information about a Policy, including its attributes and its Rules.

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
        CREATOR - string
        RULES - List of URIs (string)
    """
    policy_result = query_db('SELECT * FROM POLICY WHERE URI = ?', (policy_uri,), one=True)
    if policy_result is None:
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    policy = dict(policy_result)
    policy['RULES'] = get_rules_for_policy(policy_uri)
    return policy


def get_all_policies():
    """
    Retrieve a list of all Policies.

    :return: A List of URIs
    """
    return [result['URI'] for result in query_db('SELECT URI FROM POLICY')]


def policy_has_rule(policy_uri, rule_uri):
    # Checks if the given Policy includes the given Rule
    query_str = 'SELECT COUNT(1) FROM POLICY_HAS_RULE WHERE POLICY_URI = ? AND RULE_URI = ?'
    return query_db(query_str, (policy_uri, rule_uri), one=True)[0]


def create_rule(rule_uri, rule_type, rule_label=None):
    """
    Creates a new Rule with the given URI and rule type.

    :param rule_uri:
    :param rule_type: Permitted rule types: http://www.w3.org/ns/odrl/2/permission
                                            http://www.w3.org/ns/odrl/2/prohibition
                                            http://www.w3.org/ns/odrl/2/duty
    :param rule_label: The human-readable label for the new rule
    """
    if rule_exists(rule_uri):
        raise ValueError('A Rule with that URI already exists.')
    if not any(rule_type == permitted_type['URI'] for permitted_type in get_permitted_rule_types()):
        raise ValueError('Rule type ' + rule_type + ' is not permitted.')
    update_db('INSERT INTO RULE (URI, TYPE, LABEL) VALUES (?, ?, ?)', (rule_uri, rule_type, rule_label))


def delete_rule(rule_uri):
    # Deletes the Rule with the given URI. A Rule can only be deleted if it is not currently assigned to a policy.
    if len(get_policies_for_rule(rule_uri)) > 0:
        raise ValueError('Cannot delete a Rule while it is assigned to a Policy.')
    query_db('DELETE FROM RULE WHERE URI = ?', (rule_uri,))


def get_rule(rule_uri):
    """
    Retrieve all the relevant information about a Rule, including its Actions, Assignors and Assignees.

    :return: A Dictionary containing the following elements:
        URI - string
        TYPE_URI - string
        TYPE_LABEL - string
        LABEL - string
        ASSIGNORS - List of strings
        ASSIGNEES - List of strings
        ACTIONS - List of Actions
            Each Action is a Dictionary containing the following elements:
            URI - string
            LABEL - string
            DEFINITION - string
    """
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    query_str = '''
        SELECT R.URI, R.LABEL, R.TYPE AS TYPE_URI, RT.LABEL AS TYPE_LABEL
        FROM RULE R, RULE_TYPE RT
        WHERE R.TYPE = RT.URI AND R.URI = ?
    '''
    rule = dict(query_db(query_str, (rule_uri,), one=True))
    rule['ACTIONS'] = get_actions_for_rule(rule['URI'])
    rule['ASSIGNORS'] = get_assignors_for_rule(rule['URI'])
    rule['ASSIGNEES'] = get_assignees_for_rule(rule['URI'])
    return rule


def add_rule_to_policy(rule_uri, policy_uri):
    # Assigns a Rule to a policy. Policies are made up of many Rules. Rules can be reused in multiple Policies.
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if not policy_exists(policy_uri):
        raise ValueError('Policy with URI ' + policy_uri + ' does not exist.')
    if policy_has_rule(policy_uri, rule_uri):
        raise ValueError('Rule ' + rule_uri + ' is already included in Policy ' + policy_uri + '.')
    query_db('INSERT INTO POLICY_HAS_RULE (POLICY_URI, RULE_URI) VALUES (?, ?)', (policy_uri, rule_uri))


def remove_rule_from_policy(rule_uri, policy_uri):
    # Removes a Rule from a Policy. The Rule will still exist unless deleted, but is not assigned to that Policy anymore
    query_str = 'DELETE FROM POLICY_HAS_RULE WHERE RULE_URI=? AND POLICY_URI IN (SELECT URI FROM POLICY WHERE URI=?)'
    query_db(query_str, (rule_uri, policy_uri))


def get_rules_for_policy(policy_uri):
    """
    Retrieves all the Rules used by a Policy with the given URI.

    :param policy_uri: The URI of the Policy
    :return: A List of Rule URIs
    """
    query_str = 'SELECT RULE_URI FROM POLICY_HAS_RULE WHERE POLICY_URI = ?'
    return [rule_result['RULE_URI'] for rule_result in query_db(query_str, (policy_uri,))]


def get_all_rules():
    # Retrieves list of all Rules' URIs
    return [result['URI'] for result in query_db('SELECT URI FROM RULE')]


def rule_exists(rule_uri):
    """
    Checks if a Rule with the given URI exists

    :return:    True if the Rule exists
                False if the Rule does not exist
    """
    return query_db('SELECT COUNT(1) FROM RULE WHERE URI = ?', (rule_uri,), one=True)[0]


def get_permitted_rule_types():
    """
    Returns a list of all the rules types which are permitted

    Should be: [
        {'URI': 'http://www.w3.org/ns/odrl/2/permission', 'LABEL': 'Permission'},
        {'URI': 'http://www.w3.org/ns/odrl/2/prohibition', 'LABEL': 'Prohibition'},
        {'URI': 'http://www.w3.org/ns/odrl/2/duty', 'LABEL': 'Duty'}
    ]
    However, they can be added/removed from the database at will so using this method to check is advised
    """
    permitted_rule_types = list()
    for rule_type in query_db('SELECT URI, LABEL FROM RULE_TYPE'):
        permitted_rule_types.append(dict(rule_type))
    return permitted_rule_types


def get_policies_for_rule(rule_uri):
    """
    Returns a List of all the Policies which use the Rule given

    :param rule_uri: The URI of the Rule
    :return: A List of Policy URIs
    """
    policies = list()
    query_str = 'SELECT P.URI, P.LABEL FROM POLICY_HAS_RULE P_R, POLICY P ' \
                'WHERE P.URI = P_R.POLICY_URI AND P_R.RULE_URI = ?'
    for result in query_db(query_str, (rule_uri,)):
        policies.append(dict(result))
    return policies


def action_exists(action_uri):
    """
    Checks if an Action with the given URI exists

    :return:    True if the Action exists
                False if the Action does not exist
    """
    return query_db('SELECT COUNT(1) FROM ACTION WHERE URI = ?', (action_uri,), one=True)[0]


def add_action_to_rule(action_uri, rule_uri):
    """
    Assign an Action to a Rule. Rules can have multiple Actions associated with them, and Actions can be associated with
    multiple Rules

    :param action_uri: The URI of the Action to be assigned to the Rule
    :param rule_uri: The URI of the Rule to which the Action will be assigned
    """
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if not action_exists(action_uri):
        raise ValueError('Action with URI ' + action_uri + ' is not permitted.')
    if rule_has_action(rule_uri, action_uri):
        raise ValueError('Rule ' + rule_uri + ' already includes Action ' + action_uri + '.')
    query_db('INSERT INTO RULE_HAS_ACTION (RULE_URI, ACTION_URI) VALUES (?, ?)', (rule_uri, action_uri))


def remove_action_from_rule(action_uri, rule_uri):
    """
    Unassign an Action from a Rule

    :param action_uri: The URI of the Action to be unassigned from the Rule
    :param rule_uri: The URI of the Rule from which the Action will be unassigned
    :return:
    """
    query_db('DELETE FROM RULE_HAS_ACTION WHERE RULE_URI = ? AND ACTION_URI = ?', (rule_uri, action_uri))


def get_actions_for_rule(rule_uri):
    """
    Returns a list of all the Actions which are assigned to a given Rule

    :return: A List of Actions. Each Action is a Dictionary containing the following elements: URI, LABEL, DEFINITION
    """
    query_str = '''
        SELECT A.URI, A.LABEL, A.DEFINITION FROM ACTION A, RULE_HAS_ACTION R_A 
        WHERE R_A.RULE_URI = ?
        AND R_A.ACTION_URI = A.URI
    '''
    actions = list()
    for result in query_db(query_str, (rule_uri,)):
        actions.append(dict(result))
    return actions


def get_rules_using_action(action_uri):
    """
    Returns a list of all the Rules which are currently using a given Action
    Each Rule is a Dictionary containing the following elements: URI, TYPE, LABEL
    """
    rules = list()
    query_str = '''
        SELECT R.URI, R.URI, R.LABEL
        FROM RULE R, RULE_HAS_ACTION R_A
        WHERE R.URI = R_A.RULE_URI AND R_A.ACTION_URI = ?'''
    for result in query_db(query_str, (action_uri,)):
        rules.append(dict(result))
    return rules


def get_policies_using_action(action_uri):
    """
    Returns a list of all the Policies which are currently using a given Action.
    Each Policy is a Dictionary containing the following elements: URI, LABEL
    """
    policies = list()
    query_str = '''
        SELECT DISTINCT P.URI, P.LABEL 
        FROM POLICY P, ACTION A, POLICY_HAS_RULE P_R, RULE_HAS_ACTION R_A
        WHERE P.URI = P_R.POLICY_URI AND P_R.RULE_URI = R_A.RULE_URI AND R_A.ACTION_URI = ?
    '''
    for result in query_db(query_str, (action_uri,)):
        policies.append(dict(result))
    return policies


def rule_has_action(rule_uri, action_uri):
    # Checks if a Rule has an Action
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ACTION WHERE RULE_URI = ? AND ACTION_URI = ?'
    return query_db(query_str, (rule_uri, action_uri), one=True)[0]


def get_action(action_uri):
    # Returns the URI, Label and Definition of an Action
    result = query_db('SELECT URI, LABEL, DEFINITION FROM ACTION WHERE URI = ?', (action_uri,), one=True)
    if result is None:
        raise ValueError('Action with ID ' + action_uri + ' not found.')
    return dict(result)


def get_all_actions():
    # Returns a List of all Actions as URIs
    actions = list()
    for result in query_db('SELECT URI, LABEL, DEFINITION FROM ACTION'):
        actions.append(dict(result))
    return actions


def create_party(party_uri, label=None, comment=None):
    """
    Creates a new Party with the given URI, label and comment.

    :param party_uri: Unique identifier for the Party
    :param label: Human-readable name for the Party
    :param comment: Any other information about the Party
    """
    if party_exists(party_uri):
        raise ValueError('A Party with that URI already exists.')
    update_db('INSERT INTO PARTY (URI, LABEL, COMMENT) VALUES (?, ?, ?)', (party_uri, label, comment))


def delete_party(party_uri):
    # Deletes the Party with the given URI. A Party can only be deleted if it is not currently assigned to a Rule.
    try:
        query_db('DELETE FROM PARTY WHERE URI = ?', (party_uri,))
    except sqlite3.IntegrityError as error:
        raise ValueError('Cannot delete a Party while it is assigned to a Rule.')


def party_exists(party_uri):
    """
    Checks if a Party with the given URI exists

    :return:    True if the Party exists
                False if the Party does not exist
    """
    return query_db('SELECT COUNT(1) FROM PARTY WHERE URI = ?', (party_uri,), one=True)[0]


def get_rules_for_party(party_uri):
    # Returns a list of all the Rules to which the Party is assigned.
    query_str = '''
        SELECT DISTINCT R.URI FROM RULE R, ASSIGNOR A1, ASSIGNEE A2 
        WHERE (R.URI = A1.RULE_URI AND A1.PARTY_URI = ?) OR (R.URI = A2.RULE_URI AND A2.PARTY_URI = ?)
    '''
    return [result['URI'] for result in query_db(query_str, (party_uri, party_uri))]


def add_assignor_to_rule(assignor_uri, rule_uri):
    # Add an Assignor to a Rule
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if not party_exists(assignor_uri):
        raise ValueError('Party with URI ' + assignor_uri + ' does not exist.')
    if rule_has_assignor(rule_uri, assignor_uri):
        raise ValueError('Rule ' + rule_uri + ' already has an Assignor with URI ' + assignor_uri + '.')
    query_db('INSERT INTO ASSIGNOR (PARTY_URI, RULE_URI) VALUES (?, ?)', (assignor_uri, rule_uri))


def remove_assignor_from_rule(assignor_uri, rule_uri):
    # Remove an Assignor from a Rule
    query_db('DELETE FROM ASSIGNOR WHERE RULE_URI = ? AND PARTY_URI = ?', (rule_uri, assignor_uri))


def rule_has_assignor(rule_uri, assignor_uri):
    """
    Checks if a Rule has an Assignor with the given URI

    :return:    True if the Rule has the Assignor
                False if the Rule does not have the Assignor
    """
    query_str = 'SELECT COUNT(1) FROM ASSIGNOR WHERE RULE_URI = ? AND PARTY_URI = ?'
    return query_db(query_str, (rule_uri, assignor_uri), one=True)[0]


def get_assignors_for_rule(rule_uri):
    # Returns a list of URIs for all Assignors associated with a given Rule
    query_str = 'SELECT PARTY_URI FROM ASSIGNOR WHERE RULE_URI = ?'
    return [result['PARTY_URI'] for result in query_db(query_str, (rule_uri,))]


def add_assignee_to_rule(assignee_uri, rule_uri):
    # Add an Assignee to a Rule
    if not rule_exists(rule_uri):
        raise ValueError('Rule with URI ' + rule_uri + ' does not exist.')
    if not party_exists(assignee_uri):
        raise ValueError('Party with URI ' + assignee_uri + ' does not exist.')
    if rule_has_assignee(rule_uri, assignee_uri):
        raise ValueError('Rule ' + rule_uri + ' already has an Assignee with URI ' + assignee_uri + '.')
    query_db('INSERT INTO ASSIGNEE (PARTY_URI, RULE_URI) VALUES (?, ?)', (assignee_uri, rule_uri))


def remove_assignee_from_rule(assignee_uri, rule_uri):
    # Remove an Assignee from a Rule
    query_db('DELETE FROM ASSIGNEE WHERE RULE_URI = ? AND PARTY_URI = ?', (rule_uri, assignee_uri))


def rule_has_assignee(rule_uri, assignee_uri):
    """
    Checks if a Rule has an Assignee with the given URI

    :return:    True if the Rule has the Assignee
                False if the Rule does not have the Assignee
    """
    query_str = 'SELECT COUNT(1) FROM ASSIGNEE WHERE RULE_URI = ? AND PARTY_URI = ?'
    return query_db(query_str, (rule_uri, assignee_uri), one=True)[0]


def get_assignees_for_rule(rule_uri):
    # Returns a list of URIs for all Assignees associated with a given Rule
    query_str = 'SELECT PARTY_URI FROM ASSIGNEE WHERE RULE_URI = ?'
    return [result['PARTY_URI'] for result in query_db(query_str, (rule_uri,))]


def get_all_parties():
    # Returns a List of Parties. Each Party is a Dictionary containing the URI, Label and Comment
    return [dict(result) for result in query_db('SELECT * FROM PARTY')]


def get_party(party_uri):
    """
    Returns information about the Party with the given URI
    Returns a Dictionary with the following elements: URI, LABEL, COMMENT
    """
    result = query_db('SELECT * FROM PARTY WHERE URI = ?', (party_uri,), one=True)
    if result is None:
        raise ValueError('Party with URI ' + party_uri + ' not found.')
    return dict(result)