import re
from controller import db_access


def create_policy(policy_uri, attributes=None):
    """
    :param policy_uri:
    :param attributes:  Dictionary of optional attributes of the policy.
                        Permitted attributes:   type, label, jurisdiction, legal_code, has_version, language, see_also
                                                same_as, comment, logo, status
    :return:
    """
    if not is_valid_uri(policy_uri):
        raise ValueError('Not a valid URI: ' + policy_uri)
    db_access.create_policy(policy_uri)
    if attributes:
        for attr_name, attr_value in attributes.items():
            db_access.set_policy_attribute(policy_uri, attr_name, attr_value)


def is_valid_uri(uri):
    return True if re.match('\w+:(/?/?)[^\s]+', uri) else False
