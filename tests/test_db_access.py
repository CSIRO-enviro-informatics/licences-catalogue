import pytest
from controller import db_access
import create_database
import _conf
import sqlite3


def setup_module():
    # We want to use test.db to avoid changing the real database
    # Close the current connection, switch the db path, rebuild the db and make a new connection
    _conf.DATABASE_PATH = _conf.APP_DIR + '/tests/test.db'
    db_access.conn.close()
    create_database.teardown()
    create_database.rebuild()
    db_access.conn = sqlite3.connect(_conf.DATABASE_PATH)
    db_access.conn.execute('PRAGMA foreign_keys = 1')
    db_access.conn.row_factory = sqlite3.Row
    db_access.cursor = db_access.conn.cursor()


def setup_function():
    db_access.conn.execute('DELETE FROM RULE_HAS_ASSIGNEE')
    db_access.conn.execute('DELETE FROM RULE_HAS_ASSIGNOR')
    db_access.conn.execute('DELETE FROM PARTY')
    db_access.conn.execute('DELETE FROM RULE_HAS_ACTION')
    db_access.conn.execute('DELETE FROM POLICY_HAS_RULE')
    db_access.conn.execute('DELETE FROM RULE')
    db_access.conn.execute('DELETE FROM ASSET')
    db_access.conn.execute('DELETE FROM POLICY')
    db_access.conn.commit()


def test_create_policy():
    # Should store a new policy entry in the database
    new_policy_uri = 'https://example.com#test'
    db_access.create_policy(new_policy_uri)
    db_access.cursor.execute('SELECT COUNT(1) FROM POLICY WHERE URI = "{uri}"'.format(uri=new_policy_uri))
    assert db_access.cursor.fetchone()[0] == 1

    # Should reject duplicate policies
    with pytest.raises(ValueError):
        db_access.create_policy(new_policy_uri)


def test_delete_policy():
    # Should remove an existing policy
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    db_access.delete_policy(policy_uri)
    assert not db_access.policy_exists(policy_uri)

    # Should have also removed any assets using that policy
    assert not db_access.asset_exists(asset_uri)


def test_policy_exists():
    # Should return true if the policy exists
    uri = 'https://example.com#test'
    db_access.create_policy(uri)
    assert db_access.policy_exists(uri)

    # Should return false if the policy doesn't exist
    nonexistent_uri = 'https://example.com#nonexistent'
    assert not db_access.policy_exists(nonexistent_uri)


def test_set_policy_attribute():
    # Should set a valid attribute for an existing policy
    uri = 'https://example.com#test'
    new_policy_type = 'http://creativecommons.org/ns#License'
    db_access.create_policy(uri)
    db_access.set_policy_attribute(uri, 'TYPE', new_policy_type)
    db_access.cursor.execute('SELECT TYPE FROM POLICY WHERE URI = "{uri}";'.format(uri=uri))
    stored_policy_type = db_access.cursor.fetchone()[0]
    assert stored_policy_type == new_policy_type

    # Should reject attribute change for a policy that does not exist
    with pytest.raises(ValueError):
        db_access.set_policy_attribute('https://example.com#nonexistent', 'TYPE', new_policy_type)

    # Should reject changing attribute that is not permitted
    with pytest.raises(ValueError):
        db_access.set_policy_attribute(uri, 'NONEXISTENT', new_policy_type)


def test_get_policy():
    # Should raise an exception when the policy doesn't exist
    policy_uri = 'https://example.com#policy'
    with pytest.raises(ValueError):
        db_access.get_policy(policy_uri)

    # Should get all the attributes of the policy
    db_access.create_policy(policy_uri)
    rule_uri = 'http://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
    assignor_uri = 'https://example.com#assignor'
    assignee_uri = 'https://example.com#assignee'
    db_access.create_party(assignor_uri)
    db_access.create_party(assignee_uri)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    policy = db_access.get_policy(policy_uri)
    expected_policy_attributes = ['URI', 'TYPE', 'LABEL', 'JURISDICTION', 'LEGAL_CODE', 'HAS_VERSION', 'LANGUAGE',
                                  'SEE_ALSO', 'SAME_AS', 'COMMENT', 'LOGO', 'CREATED', 'STATUS']
    assert all(attr in policy for attr in expected_policy_attributes)
    assert policy['URI'] == policy_uri

    # Should get all of the rules
    assert policy['RULES'][0]['URI'] == rule_uri
    assert policy['RULES'][0]['TYPE'] == rule_type

    # Should get actions associated with the rule
    expected_action_attributes = ['LABEL', 'URI', 'DEFINITION']
    action = policy['RULES'][0]['ACTIONS'][0]
    assert action['URI'] == action_uri
    assert all(attr in action for attr in expected_action_attributes)

    # Should get assignors and assignees associated with the rule
    assignors = policy['RULES'][0]['ASSIGNORS']
    assignees = policy['RULES'][0]['ASSIGNEES']
    assert assignors == [assignor_uri]
    assert assignees == [assignee_uri]


def test_get_all_policies():
    policy1 = 'https://example.com#policy1'
    policy2 = 'https://example.com#policy2'
    db_access.create_policy(policy1)
    db_access.create_policy(policy2)
    assert db_access.get_all_policies() == [policy1, policy2]


def test_add_asset():
    # Should raise an exception when the policy doesn't exist
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    with pytest.raises(ValueError):
        db_access.add_asset(asset_uri, policy_uri)

    # Should store a new asset entry in the database
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    db_access.cursor.execute('SELECT COUNT(1) FROM ASSET WHERE URI = "{uri}"'.format(uri=asset_uri))
    asset_exists = db_access.cursor.fetchone()[0]
    assert asset_exists

    # Should reject duplicate assets
    with pytest.raises(ValueError):
        db_access.add_asset(asset_uri, policy_uri)


def test_asset_exists():
    # Should return true if the asset exists
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    assert db_access.asset_exists(asset_uri)

    # Should return false if the asset doesn't exist
    nonexistent_uri = 'https://example.com#nonexistent'
    assert not db_access.asset_exists(nonexistent_uri)


def test_remove_asset():
    # Should remove an existing asset
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    db_access.remove_asset(asset_uri)
    assert not db_access.asset_exists(asset_uri)


def test_get_asset():
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    asset_uri = 'https://example.com#asset'
    db_access.add_asset(asset_uri, policy_uri)
    asset = db_access.get_asset(asset_uri)
    expected_attributes = ['URI', 'POLICY_URI']
    assert all(attr in asset for attr in expected_attributes)
    assert asset['URI'] == asset_uri


def test_get_all_assets():
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    asset1 = 'https://example.com#asset1'
    asset2 = 'https://example.com#asset2'
    db_access.add_asset(asset1, policy_uri)
    db_access.add_asset(asset2, policy_uri)
    assets = db_access.get_all_assets()
    assert assets == [asset1, asset2]


def test_create_rule():
    # Should raise an exception when the rule type is not valid
    with pytest.raises(ValueError):
        db_access.create_rule('rule', 'invalid_type')

    # Should add a rule
    rule_uri = 'http://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert db_access.rule_exists(rule_uri)

    # Should raise an exception when that rule already exists
    with pytest.raises(ValueError):
        db_access.create_rule(rule_uri, rule_type)


def test_delete_rule():
    # Should not be able to delete if the rule is still used in any policies
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    rule_uri = 'http://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    with pytest.raises(ValueError):
        db_access.delete_rule(rule_uri)

    # Should delete the rule
    db_access.remove_rule_from_policy(rule_uri, policy_uri)
    db_access.delete_rule(rule_uri)
    assert not db_access.rule_exists(rule_uri)

    # Should also remove any actions from the rule
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ACTION WHERE RULE_URI = "{rule_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri))
    rule_has_actions = db_access.cursor.fetchone()[0]
    assert not rule_has_actions

    # Should also remove any assignors from the rule
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ASSIGNOR WHERE RULE_URI = "{rule_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri))
    rule_has_assignors = db_access.cursor.fetchone()[0]
    assert not rule_has_assignors

    # Should also remove any assignees from the rule
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ASSIGNEE WHERE RULE_URI = "{rule_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri))
    rule_has_assignees = db_access.cursor.fetchone()[0]
    assert not rule_has_assignees


def test_add_rule_to_policy():
    # Should raise an exception if the rule does not exist
    rule_uri = 'https://example.com#nonexistant'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    with pytest.raises(ValueError):
        db_access.add_rule_to_policy(rule_uri, policy_uri)

    # Should raise an exception if the policy does not exist
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.delete_policy(policy_uri)
    with pytest.raises(ValueError):
        db_access.add_rule_to_policy(rule_uri, policy_uri)

    # Should add a rule to a policy
    db_access.create_policy(policy_uri)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    query_str = 'SELECT COUNT(1) FROM POLICY_HAS_RULE WHERE RULE_URI = "{rule_uri}" AND POLICY_URI = "{policy_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri, policy_uri=policy_uri))
    rule_assigned = db_access.cursor.fetchone()[0]
    assert rule_assigned


def test_remove_rule_from_policy():
    # Should remove a rule from a policy
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    db_access.remove_rule_from_policy(rule_uri, policy_uri)
    query_str = 'SELECT COUNT(1) FROM POLICY_HAS_RULE WHERE RULE_URI = "{rule_uri}" AND POLICY_URI = "{policy_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri, policy_uri=policy_uri))
    rule_assigned = db_access.cursor.fetchone()[0]
    assert not rule_assigned


def test_create_party():
    # Should store a new party entry in the database
    party_uri = 'https://example.com#test'
    db_access.create_party(party_uri)
    db_access.cursor.execute('SELECT COUNT(1) FROM PARTY WHERE URI = "{uri}"'.format(uri=party_uri))
    party_exists = db_access.cursor.fetchone()[0]
    assert party_exists

    # Should reject duplicate parties
    with pytest.raises(ValueError):
        db_access.create_party(party_uri)


def test_party_exists():
    # Should return true if the party exists
    uri = 'https://example.com#test'
    db_access.create_party(uri)
    assert db_access.party_exists(uri)

    # Should return false if the policy doesn't exist
    nonexistent_uri = 'https://example.com#nonexistent'
    assert not db_access.party_exists(nonexistent_uri)


def test_delete_party():
    # Should delete the entry for a party
    party_uri = 'http://example.com#party'
    db_access.create_party(party_uri)
    db_access.delete_party(party_uri)
    db_access.cursor.execute('SELECT COUNT(1) FROM PARTY WHERE URI = "{party_uri}"'.format(party_uri=party_uri))
    party_exists = db_access.cursor.fetchone()[0]
    assert not party_exists


def test_rule_exists():
    # Should return false if the policy doesn't exist
    rule_uri = 'https://example.com#rule'
    assert not db_access.rule_exists(rule_uri)

    # Should return true if the party exists
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert db_access.rule_exists(rule_uri)


def test_action_exists():
    # Should return false if the action doesn't exist
    action_uri = 'nonexistant'
    assert not db_access.action_exists(action_uri)

    # Should return true if the action exists
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    assert db_access.action_exists(action_uri)


def test_add_action_to_rule():
    # Should raise an exception if the rule doesn't exist
    rule_uri = 'https://example.com#rule'
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    with pytest.raises(ValueError):
        db_access.add_action_to_rule(action_uri, rule_uri)

    # Should raise an exception if the action doesn't exist
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    action_uri = 'nonexistent'
    with pytest.raises(ValueError):
        db_access.add_action_to_rule(action_uri, rule_uri)

    # Should add an action to a rule
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ACTION WHERE RULE_URI = "{rule_uri}" AND ACTION_URI = "{action_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri, action_uri=action_uri))
    action_entry_exists = db_access.cursor.fetchone()[0]
    assert action_entry_exists


def test_remove_action_from_rule():
    # Should remove an action from a rule
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
    db_access.remove_action_from_rule(action_uri, rule_uri)
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ACTION WHERE RULE_URI = "{rule_uri}" AND ACTION_URI = "{action_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri, action_uri=action_uri))
    action_entry_exists = db_access.cursor.fetchone()[0]
    assert not action_entry_exists


def test_add_assignor_to_rule():
    # Should raise an exception if the rule doesn't exist
    party_uri = 'http://example.com#party'
    rule_uri = 'https://example.com#rule'
    db_access.create_party(party_uri)
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(party_uri, rule_uri)

    # Should raise an exception if the party doesn't exist
    party_uri = 'nonexistent'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(party_uri, rule_uri)

    # Should add an assignor to a rule
    party_uri = 'http://example.com#party'
    db_access.add_assignor_to_rule(party_uri, rule_uri)
    query_str = 'SELECT COUNT(1) FROM RULE_HAS_ASSIGNOR WHERE RULE_URI = "{rule_uri}" AND PARTY_URI = "{party_uri}"'
    db_access.cursor.execute(query_str.format(rule_uri=rule_uri, party_uri=party_uri))
    assignor_exists = db_access.cursor.fetchone()[0]
    assert assignor_exists


def test_remove_assignor_from_rule():
    # Should remove an action from a rule
    party_uri = 'http://example.com#party'
    db_access.create_party(party_uri)
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignor_to_rule(party_uri, rule_uri)
    db_access.remove_assignor_from_rule(party_uri, rule_uri)
    query = 'SELECT COUNT(1) FROM RULE_HAS_ASSIGNOR WHERE RULE_URI = "{rule_uri}" AND PARTY_URI = "{party_uri}"'
    db_access.cursor.execute(query.format(rule_uri=rule_uri, party_uri=party_uri))
    assignor_exists = db_access.cursor.fetchone()[0]
    assert not assignor_exists


def test_add_assignee_to_rule():
    # Should raise an exception if the rule doesn't exist
    party_uri = 'http://example.com#party'
    rule_uri = 'nonexistant'
    db_access.create_party(party_uri)
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(party_uri, rule_uri)

    # Should raise an exception if the party doesn't exist
    party_uri = 'nonexistent'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(party_uri, rule_uri)

    # Should add an assignee to a rule
    party_uri = 'http://example.com#party'
    db_access.add_assignee_to_rule(party_uri, rule_uri)
    query = 'SELECT COUNT(1) FROM RULE_HAS_ASSIGNEE WHERE RULE_URI = "{rule_uri}" AND PARTY_URI = "{party_uri}"'
    db_access.cursor.execute(query.format(rule_uri=rule_uri, party_uri=party_uri))
    assignee_exists = db_access.cursor.fetchone()[0]
    assert assignee_exists


def test_remove_assignee_from_rule():
    # Should remove an action from a rule
    party_uri = 'http://example.com#party'
    db_access.create_party(party_uri)
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignee_to_rule(party_uri, rule_uri)
    db_access.remove_assignee_from_rule(party_uri, rule_uri)
    query = 'SELECT COUNT(1) FROM RULE_HAS_ASSIGNEE WHERE RULE_URI = "{rule_uri}" AND PARTY_URI = "{party_uri}"'
    db_access.cursor.execute(query.format(rule_uri=rule_uri, party_uri=party_uri))
    assignee_exists = db_access.cursor.fetchone()[0]
    assert not assignee_exists


def test_get_permitted_rule_types():
    permitted_rule_types = db_access.get_permitted_rule_types()
    assert permitted_rule_types == [
        'http://www.w3.org/ns/odrl/2/permission',
        'http://www.w3.org/ns/odrl/2/prohibition',
        'http://www.w3.org/ns/odrl/2/duty'
    ]