import pytest
from controller import db_access


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


def test_policy_has_rule():
    # Should return false if the policy does not have the rule
    policy_uri = 'https://example.com#policy'
    rule_uri = 'http://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    assert not db_access.policy_has_rule(policy_uri, rule_uri)

    # Should return true if the policy has the rule
    db_access.create_policy(policy_uri)
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    assert db_access.policy_has_rule(policy_uri, rule_uri)


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


def test_remove_asset():
    # Should remove an existing asset
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    db_access.remove_asset(asset_uri)
    assert not db_access.asset_exists(asset_uri)


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
    assignor_uri = 'http://example.com#assignor'
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    assignee_uri = 'http://example.com#assignee'
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
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
    assert not db_access.rule_has_assignor(assignor_uri, rule_uri)

    # Should also remove any assignees from the rule
    assert not db_access.rule_has_assignee(assignee_uri, rule_uri)


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

    # Should raise an exception if the rule is already included in the policy
    with pytest.raises(ValueError):
        db_access.add_rule_to_policy(rule_uri, policy_uri)


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


def test_get_all_rules():
    rule1 = 'https://example.com#rule1'
    rule2 = 'https://example.com#rule2'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule1, rule_type)
    db_access.create_rule(rule2, rule_type)
    rules = db_access.get_all_rules()
    assert rules == [rule1, rule2]


def test_rule_exists():
    # Should return false if the policy doesn't exist
    rule_uri = 'https://example.com#rule'
    assert not db_access.rule_exists(rule_uri)

    # Should return true if the party exists
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert db_access.rule_exists(rule_uri)


def test_get_permitted_rule_types():
    permitted_rule_types = db_access.get_permitted_rule_types()
    assert permitted_rule_types == [
        'http://www.w3.org/ns/odrl/2/permission',
        'http://www.w3.org/ns/odrl/2/prohibition',
        'http://www.w3.org/ns/odrl/2/duty'
    ]


def test_get_policies_for_rule():
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    policy1 = 'https://example.com#policy1'
    db_access.create_policy(policy1)
    db_access.add_rule_to_policy(rule_uri, policy1)
    policy2 = 'https://example.com#policy2'
    db_access.create_policy(policy2)
    db_access.add_rule_to_policy(rule_uri, policy2)
    policies = db_access.get_policies_for_rule(rule_uri)
    assert policies == [policy1, policy2]


def test_action_exists():
    # Should return false if the action doesn't exist
    action_uri = 'nonexistant'
    assert not db_access.action_exists(action_uri)

    # Should return true if the action exists
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    assert db_access.action_exists(action_uri)


def test_get_all_actions():
    actions = db_access.get_all_actions()
    assert actions
    for action in actions:
        assert all(x in ['URI', 'LABEL', 'DEFINITION'] for x in action)


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

    # Should raise an exception if the rule already has that action
    with pytest.raises(ValueError):
        db_access.add_action_to_rule(action_uri, rule_uri)


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


def test_get_actions_for_rule():
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    action1 = 'http://www.w3.org/ns/odrl/2/acceptTracking'
    action2 = 'http://www.w3.org/ns/odrl/2/aggregate'
    db_access.add_action_to_rule(action1, rule_uri)
    db_access.add_action_to_rule(action2, rule_uri)
    actions = db_access.get_actions_for_rule(rule_uri)
    assert all(action['URI'] in [action1, action2] for action in actions)


def test_rule_has_action():
    # Should return false if the rule does not have the action
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    assert not db_access.rule_has_action(rule_uri, rule_type)

    # Should return true if the rule has the action
    db_access.add_action_to_rule(action_uri, rule_uri)
    assert db_access.rule_has_action(rule_uri, action_uri)


def test_add_assignor_to_rule():
    # Should raise an exception if the rule doesn't exist
    assignor_uri = 'http://example.com#assignor'
    rule_uri = 'https://example.com#rule'
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(assignor_uri, rule_uri)

    # Should add an assignor to a rule
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    assert db_access.rule_has_assignor(rule_uri, assignor_uri)

    # Should raise an exception if the rule already has that assignor
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(assignor_uri, rule_uri)


def test_remove_assignor_from_rule():
    # Should remove an assignor from a rule
    assignor_uri = 'http://example.com#assignor'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    db_access.remove_assignor_from_rule(assignor_uri, rule_uri)
    assert not db_access.rule_has_assignor(rule_uri, assignor_uri)


def test_rule_has_assignor():
    # Should return false if the rule doesn't have that assignor
    assignor_uri = 'http://example.com#assignor'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert not db_access.rule_has_assignor(rule_uri, assignor_uri)

    # Should return true if the rule does have that assignor
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    assert db_access.rule_has_assignor(rule_uri, assignor_uri)


def test_get_assignors_for_rule():
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assignor1 = 'https://example.com#assignor1'
    assignor2 = 'https://example.com#assignor2'
    db_access.add_assignor_to_rule(assignor1, rule_uri)
    db_access.add_assignor_to_rule(assignor2, rule_uri)
    assignors = db_access.get_assignors_for_rule(rule_uri)
    assert assignors == [assignor1, assignor2]


def test_add_assignee_to_rule():
    # Should raise an exception if the rule doesn't exist
    assignee_uri = 'http://example.com#assignee'
    rule_uri = 'https://example.com#rule'
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(assignee_uri, rule_uri)

    # Should add an assignee to a rule
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    assert db_access.rule_has_assignee(rule_uri, assignee_uri)

    # Should raise an exception if the rule already has that assignee
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(assignee_uri, rule_uri)


def test_remove_assignee_from_rule():
    # Should remove an assignee from a rule
    assignee_uri = 'http://example.com#assignee'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    db_access.remove_assignee_from_rule(assignee_uri, rule_uri)
    assert not db_access.rule_has_assignee(rule_uri, assignee_uri)


def test_rule_has_assignee():
    # Should return false if the rule doesn't have that assignee
    assignee_uri = 'http://example.com#assignee'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert not db_access.rule_has_assignee(rule_uri, assignee_uri)

    # Should return true if the rule does have that assignee
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    assert db_access.rule_has_assignee(rule_uri, assignee_uri)


def test_get_assignees_for_rule():
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assignee1 = 'https://example.com#assignee1'
    assignee2 = 'https://example.com#assignee2'
    db_access.add_assignee_to_rule(assignee1, rule_uri)
    db_access.add_assignee_to_rule(assignee2, rule_uri)
    assignees = db_access.get_assignees_for_rule(rule_uri)
    assert assignees == [assignee1, assignee2]
