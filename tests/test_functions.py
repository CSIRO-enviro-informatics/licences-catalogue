from controller import functions
from unittest import mock
from seed_database import get_db as mock_get_db


@mock.patch('controller.db_access.set_policy_attribute')
@mock.patch('controller.db_access.create_policy')
@mock.patch('controller.db_access.create_rule')
@mock.patch('controller.db_access.add_rule_to_policy')
@mock.patch('controller.db_access.add_assignor_to_rule')
@mock.patch('controller.db_access.add_assignee_to_rule')
@mock.patch('controller.db_access.add_action_to_rule')
@mock.patch('controller.db_access.get_db', side_effect=mock_get_db)
def test_create_policy(db_mock, add_action_to_rule_mock, add_assignee_to_rule_mock, add_assignor_to_rule_mock, add_rule_to_policy_mock, create_rule_mock, create_policy_mock, set_policy_attribute_mock):
    # With no attributes
    policy_uri = 'http://example.com#policy'
    functions.create_policy(policy_uri)
    create_policy_mock.assert_called_once_with(policy_uri)

    # With attributes and rules
    create_policy_mock.reset_mock()
    attributes = {'type': 'http://creativecommons.org/ns#License', 'label': 'Some policy'}
    rules = [
        {
            'TYPE_URI': 'http://www.w3.org/ns/odrl/2/permission',
            'ASSIGNORS': [{'URI': 'http://example.com/assignor/1', 'LABEL': None, 'COMMENT': None},
                          {'URI': 'http://example.com/assignor/2', 'LABEL': None, 'COMMENT': None}],
            'ASSIGNEES': [{'URI': 'http://example.com/assignee/1', 'LABEL': None, 'COMMENT': None},
                          {'URI': 'http://example.com/assignee/2', 'LABEL': None, 'COMMENT': None}],
            'ACTIONS': ['http://www.w3.org/ns/odrl/2/acceptTracking']
        },
        {
            'TYPE_URI': 'http://www.w3.org/ns/odrl/2/duty',
            'ACTIONS': ['http://www.w3.org/ns/odrl/2/aggregate']
        }
    ]
    functions.create_policy(policy_uri, attributes, rules)
    create_policy_mock.assert_called_once_with(policy_uri)
    set_policy_attribute_mock.assert_any_call(policy_uri, 'label', attributes['label'])
    set_policy_attribute_mock.assert_any_call(policy_uri, 'type', attributes['type'])
    create_rule_mock.assert_called()
    add_action_to_rule_mock.assert_called()
    add_rule_to_policy_mock.assert_called()
    add_assignor_to_rule_mock.assert_called()
    add_assignee_to_rule_mock.assert_called()


def test_uri_is_valid():
    assert functions.is_valid_uri('not a uri') is False
    assert functions.is_valid_uri('https://example.com#test') is True
