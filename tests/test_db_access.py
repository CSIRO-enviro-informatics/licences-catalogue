import pytest
from controller import db_access
from unittest import mock
from seed_database import get_db as mock_get_db


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_create_policy(mock):
    # Should store a new policy entry in the database
    new_policy_uri = 'https://example.com#test'
    db_access.create_policy(new_policy_uri)
    assert db_access.policy_exists(new_policy_uri)

    # Should reject duplicate policies
    with pytest.raises(ValueError):
        db_access.create_policy(new_policy_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_delete_policy(mock):
    # Should remove an existing policy
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    db_access.delete_policy(policy_uri)
    assert not db_access.policy_exists(policy_uri)

    # Should have also removed any assets using that policy
    assert not db_access.asset_exists(asset_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_policy_exists(mock):
    # Should return true if the policy exists
    uri = 'https://example.com#test'
    db_access.create_policy(uri)
    assert db_access.policy_exists(uri)

    # Should return false if the policy doesn't exist
    nonexistent_uri = 'https://example.com#nonexistent'
    assert not db_access.policy_exists(nonexistent_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_set_policy_attribute(mock):
    # Should set a valid attribute for an existing policy
    uri = 'https://example.com#test'
    new_policy_type = 'http://creativecommons.org/ns#License'
    db_access.create_policy(uri)
    db_access.set_policy_attribute(uri, 'TYPE', new_policy_type)
    stored_policy_type = db_access.query_db('SELECT TYPE FROM POLICY WHERE URI = ?', (uri,), one=True)[0]
    assert stored_policy_type == new_policy_type

    # Should reject attribute change for a policy that does not exist
    with pytest.raises(ValueError):
        db_access.set_policy_attribute('https://example.com#nonexistent', 'TYPE', new_policy_type)

    # Should reject changing attribute that is not permitted
    with pytest.raises(ValueError):
        db_access.set_policy_attribute(uri, 'NONEXISTENT', new_policy_type)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_policy(mock):
    # Should raise an exception when the policy doesn't exist
    policy_uri = 'https://example.com#policy'
    with pytest.raises(ValueError):
        db_access.get_policy(policy_uri)

    # Should get all the attributes of the policy
    db_access.create_policy(policy_uri)
    policy_type = 'http://creativecommons.org/ns#License'
    db_access.set_policy_attribute(policy_uri, 'TYPE', policy_type)
    rule_uri = 'http://example.com#rule'
    rule_type_uri = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type_uri, rule_label)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    policy = db_access.get_policy(policy_uri)
    expected_policy_attributes = ['URI', 'TYPE', 'LABEL', 'JURISDICTION', 'LEGAL_CODE', 'HAS_VERSION', 'LANGUAGE',
                                  'SEE_ALSO', 'SAME_AS', 'COMMENT', 'LOGO', 'CREATED', 'STATUS', 'RULES']
    assert all(attr in policy for attr in expected_policy_attributes)
    assert policy['URI'] == policy_uri
    assert policy['TYPE'] == policy_type
    assert policy['RULES'] == [rule_uri]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_all_policies(mock):
    policy1_uri = 'https://example.com#policy1'
    policy2_uri = 'https://example.com#policy2'
    db_access.create_policy(policy1_uri)
    db_access.create_policy(policy2_uri)

    # Should retrieve every policy
    assert db_access.get_all_policies() == [policy1_uri, policy2_uri]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_policy_has_rule(mock):
    # Should return false if the policy does not have the rule
    policy_uri = 'https://example.com#policy'
    rule_uri = 'http://example.com#rule'
    assert not db_access.policy_has_rule(policy_uri, rule_uri)

    # Should return true if the policy has the rule
    db_access.create_policy(policy_uri)
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    assert db_access.policy_has_rule(policy_uri, rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_add_asset(mock):
    # Should raise an exception when the policy doesn't exist
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    with pytest.raises(ValueError):
        db_access.add_asset(asset_uri, policy_uri)

    # Should store a new asset entry in the database
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    asset_exists = db_access.query_db('SELECT COUNT(1) FROM ASSET WHERE URI = ?', (asset_uri,), one=True)[0]
    assert asset_exists

    # Should reject duplicate assets
    with pytest.raises(ValueError):
        db_access.add_asset(asset_uri, policy_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_remove_asset(mock):
    # Should remove an existing asset
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    db_access.remove_asset(asset_uri)
    assert not db_access.asset_exists(asset_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_asset_exists(mock):
    # Should return true if the asset exists
    asset_uri = 'https://example.com#asset'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    db_access.add_asset(asset_uri, policy_uri)
    assert db_access.asset_exists(asset_uri)

    # Should return false if the asset doesn't exist
    nonexistent_uri = 'https://example.com#nonexistent'
    assert not db_access.asset_exists(nonexistent_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_all_assets(mock):
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    asset1 = 'https://example.com#asset1'
    asset2 = 'https://example.com#asset2'
    db_access.add_asset(asset1, policy_uri)
    db_access.add_asset(asset2, policy_uri)
    assets = db_access.get_all_assets()
    assert assets == [asset1, asset2]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_create_rule(mock):
    # Should raise an exception when the rule type is not valid
    rule_label = 'Rule'
    with pytest.raises(ValueError):
        db_access.create_rule('rule', 'invalid_type', rule_label)

    # Should add a rule
    rule_uri = 'http://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    assert db_access.rule_exists(rule_uri)

    # Should raise an exception when that rule already exists
    with pytest.raises(ValueError):
        db_access.create_rule(rule_uri, rule_type, rule_label)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_delete_rule(mock):
    # Should not be able to delete if the rule is still used in any policies
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    rule_uri = 'http://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    assignor_uri = 'http://example.com#assignor'
    db_access.create_party(assignor_uri)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    assignee_uri = 'http://example.com#assignee'
    db_access.create_party(assignee_uri)
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
    assert not db_access.rule_has_action(rule_uri, action_uri)

    # Should also remove any assignors from the rule
    assert not db_access.rule_has_assignor(assignor_uri, rule_uri)

    # Should also remove any assignees from the rule
    assert not db_access.rule_has_assignee(assignee_uri, rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_rule(mock):
    # Should raise an exception when the rule doesn't exist
    rule_uri = 'http://example.com#rule'
    with pytest.raises(ValueError):
        db_access.get_rule(rule_uri)

    # Should get uri, type and label of the rule
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
    assignor_uri = 'https://example.com#assignor'
    assignee_uri = 'https://example.com#assignee'
    db_access.create_party(assignor_uri)
    db_access.create_party(assignee_uri)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    rule = db_access.get_rule(rule_uri)
    assert rule['URI'] == rule_uri
    assert rule['TYPE_URI'] == rule_type
    assert rule['TYPE_LABEL'] == 'Permission'
    assert rule['LABEL'] == rule_label

    # Should get actions associated with the rule
    action = rule['ACTIONS'][0]
    assert action['LABEL'] == 'Distribute'
    assert action['URI'] == action_uri
    assert action['DEFINITION'] == 'To supply the Asset to third-parties.'

    # Should get assignors and assignees associated with the rule
    assert rule['ASSIGNORS'] == [assignor_uri]
    assert rule['ASSIGNEES'] == [assignee_uri]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_add_rule_to_policy(mock):
    # Should raise an exception if the rule does not exist
    rule_uri = 'https://example.com#nonexistant'
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    with pytest.raises(ValueError):
        db_access.add_rule_to_policy(rule_uri, policy_uri)

    # Should raise an exception if the policy does not exist
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    db_access.delete_policy(policy_uri)
    with pytest.raises(ValueError):
        db_access.add_rule_to_policy(rule_uri, policy_uri)

    # Should add a rule to a policy
    db_access.create_policy(policy_uri)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    query_str = 'SELECT COUNT(1) FROM POLICY_HAS_RULE WHERE RULE_URI = ? AND POLICY_URI = ?'
    rule_assigned = db_access.query_db(query_str, (rule_uri, policy_uri), one=True)[0]
    assert rule_assigned

    # Should raise an exception if the rule is already included in the policy
    with pytest.raises(ValueError):
        db_access.add_rule_to_policy(rule_uri, policy_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_remove_rule_from_policy(mock):
    # Should remove a rule from a policy
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    db_access.add_rule_to_policy(rule_uri, policy_uri)
    db_access.remove_rule_from_policy(rule_uri, policy_uri)
    assert not db_access.policy_has_rule(policy_uri, rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_rules_for_policy(mock):
    # Should return a list of URIs for all Rules assigned to a Policy
    policy_uri = 'https://example.com#policy'
    db_access.create_policy(policy_uri)
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    rule1_uri = 'https://example.com#rule1'
    rule2_uri = 'https://example.com#rule2'
    db_access.create_rule(rule1_uri, rule_type, rule_label)
    db_access.create_rule(rule2_uri, rule_type, rule_label)
    db_access.add_rule_to_policy(rule1_uri, policy_uri)
    db_access.add_rule_to_policy(rule2_uri, policy_uri)
    assert db_access.get_rules_for_policy(policy_uri) == [rule1_uri, rule2_uri]

    # Shouldn't include any other Rules
    rule3_uri = 'https://example.com#rule3'
    db_access.create_rule(rule3_uri, rule_type, rule_label)
    assert db_access.get_rules_for_policy(policy_uri) == [rule1_uri, rule2_uri]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_all_rules(mock):
    rule1 = 'https://example.com#rule1'
    rule2 = 'https://example.com#rule2'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule1_label = 'Rule1'
    rule2_label = 'Rule2'
    db_access.create_rule(rule1, rule_type, rule1_label)
    db_access.create_rule(rule2, rule_type, rule2_label)
    rules = db_access.get_all_rules()
    assert rules == [rule1, rule2]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_rule_exists(mock):
    # Should return false if the policy doesn't exist
    rule_uri = 'https://example.com#rule'
    assert not db_access.rule_exists(rule_uri)

    # Should return true if the party exists
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    assert db_access.rule_exists(rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_permitted_rule_types(mock):
    permitted_rule_types = db_access.get_permitted_rule_types()
    assert permitted_rule_types == [
        {'URI': 'http://www.w3.org/ns/odrl/2/permission', 'LABEL': 'Permission'},
        {'URI': 'http://www.w3.org/ns/odrl/2/prohibition', 'LABEL': 'Prohibition'},
        {'URI': 'http://www.w3.org/ns/odrl/2/duty', 'LABEL': 'Duty'}
    ]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_policies_for_rule(mock):
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    policy1 = 'https://example.com#policy1'
    db_access.create_policy(policy1)
    db_access.add_rule_to_policy(rule_uri, policy1)
    policy2 = 'https://example.com#policy2'
    db_access.create_policy(policy2)
    db_access.add_rule_to_policy(rule_uri, policy2)
    policies = db_access.get_policies_for_rule(rule_uri)
    assert {'URI': policy1, 'LABEL': None} in policies
    assert {'URI': policy2, 'LABEL': None} in policies


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_action_exists(mock):
    # Should return false if the action doesn't exist
    action_uri = 'nonexistent'
    assert not db_access.action_exists(action_uri)

    # Should return true if the action exists
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    assert db_access.action_exists(action_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_action(mock):
    # Should raise an exception if the action does not exist
    action_uri = 'nonexistent'
    with pytest.raises(ValueError):
        db_access.get_action(action_uri)

    # Should return uri, label, and definition
    action_uri = 'http://www.w3.org/ns/odrl/2/acceptTracking'
    action = db_access.get_action(action_uri)
    assert action['LABEL'] == 'Accept Tracking'
    assert action['URI'] == 'http://www.w3.org/ns/odrl/2/acceptTracking'
    assert action['DEFINITION'] == 'To accept that the use of the Asset may be tracked.'


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_all_actions(mock):
    actions = db_access.get_all_actions()
    assert actions
    for action in actions:
        assert all(x in ['URI', 'LABEL', 'DEFINITION'] for x in action)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_action_label(mock):
    assert db_access.get_action_label('http://www.w3.org/ns/odrl/2/acceptTracking') == 'Accept Tracking'


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_add_action_to_rule(mock):
    # Should raise an exception if the rule doesn't exist
    rule_uri = 'https://example.com#rule'
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    with pytest.raises(ValueError):
        db_access.add_action_to_rule(action_uri, rule_uri)

    # Should raise an exception if the action doesn't exist
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    action_uri = 'nonexistent'
    with pytest.raises(ValueError):
        db_access.add_action_to_rule(action_uri, rule_uri)

    # Should add an action to a rule
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
    assert db_access.rule_has_action(rule_uri, action_uri)

    # Should raise an exception if the rule already has that action
    with pytest.raises(ValueError):
        db_access.add_action_to_rule(action_uri, rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_remove_action_from_rule(mock):
    # Should remove an action from a rule
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    db_access.add_action_to_rule(action_uri, rule_uri)
    db_access.remove_action_from_rule(action_uri, rule_uri)
    assert not db_access.rule_has_action(rule_uri, action_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_actions_for_rule(mock):
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    action1 = 'http://www.w3.org/ns/odrl/2/acceptTracking'
    action2 = 'http://www.w3.org/ns/odrl/2/aggregate'
    db_access.add_action_to_rule(action1, rule_uri)
    db_access.add_action_to_rule(action2, rule_uri)
    actions = db_access.get_actions_for_rule(rule_uri)
    assert all(action['URI'] in [action1, action2] for action in actions)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_rules_using_action(mock):
    action_uri = 'http://www.w3.org/ns/odrl/2/acceptTracking'
    rule1_uri = 'https://example.com#rule1'
    rule1_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule1_label = 'Rule1'
    db_access.create_rule(rule1_uri, rule1_type, rule1_label)
    db_access.add_action_to_rule(action_uri, rule1_uri)
    rule2_uri = 'https://example.com#rule2'
    rule2_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule2_label = 'Rule2'
    db_access.create_rule(rule2_uri, rule2_type, rule2_label)
    db_access.add_action_to_rule(action_uri, rule2_uri)
    rules = db_access.get_rules_using_action(action_uri)
    assert all(rule['URI'] in [rule1_uri, rule2_uri] for rule in rules)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_policies_using_action(mock):
    action_uri = 'http://www.w3.org/ns/odrl/2/acceptTracking'
    rule1_uri = 'https://example.com#rule1'
    rule1_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule1_label = 'Rule1'
    db_access.create_rule(rule1_uri, rule1_type, rule1_label)
    db_access.add_action_to_rule(action_uri, rule1_uri)
    rule2_uri = 'https://example.com#rule2'
    rule2_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule2_label = 'Rule2'
    db_access.create_rule(rule2_uri, rule2_type, rule2_label)
    db_access.add_action_to_rule(action_uri, rule2_uri)
    policy1_uri = 'http://example.com#policy1'
    policy2_uri = 'http://example.com#policy2'
    policy3_uri = 'http://example.com#policy3'
    db_access.create_policy(policy1_uri)
    db_access.create_policy(policy2_uri)
    db_access.create_policy(policy3_uri)
    db_access.add_rule_to_policy(rule1_uri, policy1_uri)
    db_access.add_rule_to_policy(rule2_uri, policy2_uri)
    db_access.add_rule_to_policy(rule2_uri, policy3_uri)
    policies = db_access.get_policies_using_action(action_uri)
    assert all(policy['URI'] in [policy1_uri, policy2_uri, policy3_uri] for policy in policies)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_rule_has_action(mock):
    # Should return false if the rule does not have the action
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    action_uri = 'http://www.w3.org/ns/odrl/2/distribute'
    assert not db_access.rule_has_action(rule_uri, rule_type)

    # Should return true if the rule has the action
    db_access.add_action_to_rule(action_uri, rule_uri)
    assert db_access.rule_has_action(rule_uri, action_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_create_party(mock):
    # Should create a party with the URI, label and comment given
    party_uri = 'https://example.com#party'
    label = 'Party'
    comment = 'This is a test party.'
    db_access.create_party(party_uri, label, comment)
    assert db_access.party_exists(party_uri)

    # Should raise an exception of the party already exists
    with pytest.raises(ValueError):
        db_access.create_party(party_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_delete_party(mock):
    # Should raise an exception if the Party is currently assigned to a Rule
    party_uri = 'https://example.com#party'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_party(party_uri)
    db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignor_to_rule(party_uri, rule_uri)
    with pytest.raises(ValueError):
        db_access.delete_party(party_uri)

    # Should delete the Party if not currently assigned to a Rule (deleting the rule drops the assignment)
    db_access.delete_rule(rule_uri)
    db_access.delete_party(party_uri)
    assert not db_access.party_exists(party_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_party_exists(mock):
    # Should return false if the party does not exist
    party_uri = 'https://example.com#party'
    assert not db_access.party_exists(party_uri)

    # Should return true of the party exists
    db_access.create_party(party_uri)
    assert db_access.party_exists(party_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_rules_for_party(mock):
    party_uris = ['https://example.com/party/1', 'https://example.com/party/2']
    for party_uri in party_uris:
        db_access.create_party(party_uri)
    rule_uris = ['http://example.com/rule/1', 'http://example.com/rule/2', 'http://example.com/rule/3',
                 'http://example.com/rule/4']
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    for rule_uri in rule_uris:
        db_access.create_rule(rule_uri, rule_type)
    db_access.add_assignor_to_rule(party_uris[0], rule_uris[0])
    db_access.add_assignor_to_rule(party_uris[0], rule_uris[1])
    db_access.add_assignee_to_rule(party_uris[0], rule_uris[2])
    db_access.add_assignor_to_rule(party_uris[1], rule_uris[3])

    # Should list the parties assigned to a rule and only those parties
    assert {rule_uris[0], rule_uris[1], rule_uris[2]} == set(db_access.get_rules_for_party(party_uris[0]))
    assert [rule_uris[3]] == db_access.get_rules_for_party(party_uris[1])


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_add_assignor_to_rule(mock):
    # Should raise an exception if the rule doesn't exist
    assignor_uri = 'http://example.com#assignor'
    rule_uri = 'https://example.com#rule'
    db_access.create_party(assignor_uri)
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(assignor_uri, rule_uri)

    # Should raise an exception if the assignor doesn't exist
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.delete_party(assignor_uri)
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(assignor_uri, rule_uri)

    # Should add an assignor to a rule
    db_access.create_party(assignor_uri)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    assert db_access.rule_has_assignor(rule_uri, assignor_uri)

    # Should raise an exception if the rule already has that assignor
    with pytest.raises(ValueError):
        db_access.add_assignor_to_rule(assignor_uri, rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_remove_assignor_from_rule(mock):
    # Should remove an assignor from a rule
    assignor_uri = 'http://example.com#assignor'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    db_access.create_party(assignor_uri)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    db_access.remove_assignor_from_rule(assignor_uri, rule_uri)
    assert not db_access.rule_has_assignor(rule_uri, assignor_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_rule_has_assignor(mock):
    # Should return false if the rule doesn't have that assignor
    assignor_uri = 'http://example.com#assignor'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert not db_access.rule_has_assignor(rule_uri, assignor_uri)

    # Should return true if the rule does have that assignor
    db_access.create_party(assignor_uri)
    db_access.add_assignor_to_rule(assignor_uri, rule_uri)
    assert db_access.rule_has_assignor(rule_uri, assignor_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_assignors_for_rule(mock):
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assignor1 = 'https://example.com#assignor1'
    assignor2 = 'https://example.com#assignor2'
    db_access.create_party(assignor1)
    db_access.create_party(assignor2)
    db_access.add_assignor_to_rule(assignor1, rule_uri)
    db_access.add_assignor_to_rule(assignor2, rule_uri)
    assignors = db_access.get_assignors_for_rule(rule_uri)
    assert assignors == [assignor1, assignor2]


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_add_assignee_to_rule(mock):
    # Should raise an exception if the rule doesn't exist
    rule_uri = 'https://example.com#rule'
    assignee_uri = 'http://example.com#assignee'
    db_access.create_party(assignee_uri)
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(assignee_uri, rule_uri)

    # Should raise an exception if the assignee doesn't exist
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.delete_party(assignee_uri)
    db_access.create_rule(rule_uri, rule_type)
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(assignee_uri, rule_uri)

    # Should add an assignee to a rule
    db_access.create_party(assignee_uri)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    assert db_access.rule_has_assignee(rule_uri, assignee_uri)

    # Should raise an exception if the rule already has that assignee
    with pytest.raises(ValueError):
        db_access.add_assignee_to_rule(assignee_uri, rule_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_remove_assignee_from_rule(mock):
    # Should remove an assignee from a rule
    assignee_uri = 'http://example.com#assignee'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    db_access.create_party(assignee_uri)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    db_access.remove_assignee_from_rule(assignee_uri, rule_uri)
    assert not db_access.rule_has_assignee(rule_uri, assignee_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_rule_has_assignee(mock):
    # Should return false if the rule doesn't have that assignee
    assignee_uri = 'http://example.com#assignee'
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    db_access.create_rule(rule_uri, rule_type)
    assert not db_access.rule_has_assignee(rule_uri, assignee_uri)

    # Should return true if the rule does have that assignee
    db_access.create_party(assignee_uri)
    db_access.add_assignee_to_rule(assignee_uri, rule_uri)
    assert db_access.rule_has_assignee(rule_uri, assignee_uri)


@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_get_assignees_for_rule(mock):
    rule_uri = 'https://example.com#rule'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule_label = 'Rule'
    db_access.create_rule(rule_uri, rule_type, rule_label)
    assignee1 = 'https://example.com#assignee1'
    assignee2 = 'https://example.com#assignee2'
    db_access.create_party(assignee1)
    db_access.create_party(assignee2)
    db_access.add_assignee_to_rule(assignee1, rule_uri)
    db_access.add_assignee_to_rule(assignee2, rule_uri)
    assignees = db_access.get_assignees_for_rule(rule_uri)
    assert assignees == [assignee1, assignee2]
