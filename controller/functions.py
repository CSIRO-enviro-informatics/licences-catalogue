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


def get_policies_with_constraints(permissions, duties, prohibitions):
    perfect_fit_licences = []
    extra_conditions_licences = []
    missing_conditions_licences = []
    policies = db_access.get_all_policies()
    for policy in policies:
        # Collect all permissions, duties and prohibitions found in the policy's rules
        policy_permissions = set()
        policy_duties = set()
        policy_prohibitions = set()
        for rule in policy['RULES']:
            if rule['TYPE'] == db_access.ruletype['PERMISSION']:
                policy_permissions = policy_permissions.union(set(rule['ACTIONS']))
            elif rule['TYPE'] == db_access.ruletype['DUTY']:
                policy_duties = policy_duties.union(set(rule['ACTIONS']))
            elif rule['TYPE'] == db_access.ruletype['PROHIBITION']:
                policy_prohibitions = policy_prohibitions.union(set(rule['ACTIONS']))

        # todo: Compare desired conditions and policy conditions
        policy_has_extra_conditions = None
        policy_is_missing_conditions = None
        extra_conditions = {'permissions': None, 'duties': None, 'prohibitions': None}
        missing_conditions = {'permissions': None, 'duties': None, 'prohibitions': None}

        # Place the policy in a category, or don't
        if not policy_has_extra_conditions and not policy_is_missing_conditions:
            perfect_fit_licences.append({'label': policy['LABEL'], 'uri': policy['URI']})
        elif policy_has_extra_conditions and not policy_is_missing_conditions:
            extra_conditions_licences.append({
                'label': policy['LABEL'],
                'uri': policy['URI'],
                'permissions': extra_conditions['permissions'],
                'duties': extra_conditions['duties'],
                'prohibitions': extra_conditions['prohibitions']
            })
        elif not policy_has_extra_conditions and policy_is_missing_conditions:
            missing_conditions_licences.append({
                'label': policy['LABEL'],
                'uri': policy['URI'],
                'permissions': missing_conditions['permissions'],
                'duties': missing_conditions['duties'],
                'prohibitions': missing_conditions['prohibitions']
            })
        print(policy['LABEL'])
        print(list(policy_permissions))
        print(list(policy_duties))
        print(list(policy_prohibitions))

    return {'perfect': perfect_fit_licences, 'extra': extra_conditions_licences, 'missing': missing_conditions_licences}