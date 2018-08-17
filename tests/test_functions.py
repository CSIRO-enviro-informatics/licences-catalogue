from controller import functions
from unittest import mock


@mock.patch('controller.db_access.set_policy_attribute')
@mock.patch('controller.db_access.create_policy')
def test_create_policy(create_policy_mock, set_policy_attribute_mock):
    # With no attributes
    policy_uri = 'http://exmaple.com#policy'
    functions.create_policy(policy_uri)
    create_policy_mock.assert_called_once_with(policy_uri)

    # With attributes
    create_policy_mock.reset_mock()
    attributes = {'type': 'http://creativecommons.org/ns#License', 'label': 'Some policy'}
    functions.create_policy(policy_uri, attributes)
    create_policy_mock.assert_called_once_with(policy_uri)
    set_policy_attribute_mock.assert_any_call(policy_uri, 'label', attributes['label'])
    set_policy_attribute_mock.assert_any_call(policy_uri, 'type', attributes['type'])


def test_uri_is_valid():
    assert functions.is_valid_uri('not a uri') is False
    assert functions.is_valid_uri('https://example.com#test') is True
