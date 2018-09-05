import re
from controller import db_access
from flask import url_for


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


def get_policies_with_constraints(desired_permissions, desired_duties, desired_prohibitions):
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
            action_uris = [action['URI'] for action in rule['ACTIONS']]
            if rule['TYPE_LABEL'] == 'Permission':
                policy_permissions = policy_permissions.union(action_uris)
            elif rule['TYPE_LABEL'] == 'Duty':
                policy_duties = policy_duties.union(action_uris)
            elif rule['TYPE_LABEL'] == 'Prohibition':
                policy_prohibitions = policy_prohibitions.union(action_uris)

        # Compare desired conditions and policy conditions
        desired_permissions = set(desired_permissions)
        desired_duties = set(desired_duties)
        desired_prohibitions = set(desired_prohibitions)
        extra_conditions = {
            'permissions': policy_permissions - desired_permissions,
            'duties': policy_duties - desired_duties,
            'prohibitions': policy_prohibitions - desired_prohibitions}
        missing_conditions = {
            'permissions': desired_permissions - policy_permissions,
            'duties': desired_duties - policy_duties,
            'prohibitions': desired_prohibitions - policy_prohibitions
        }
        if all(len(value) == 0 for label, value in extra_conditions.items()):
            policy_has_extra_conditions = False
        else:
            policy_has_extra_conditions = True
        if all(len(value) == 0 for label, value in missing_conditions.items()):
            policy_has_missing_conditions = False
        else:
            policy_has_missing_conditions = True

        # Place the policy in a category, or don't
        if not policy_has_extra_conditions and not policy_has_missing_conditions:
            perfect_fit_licences.append({
                'LABEL': policy['LABEL'],
                'URI': url_for('controller.licence_routes', uri=policy['URI'])
            })
        elif policy_has_extra_conditions and not policy_has_missing_conditions:
            extra_permissions = [db_access.get_action_label(action) for action in extra_conditions['permissions']]
            extra_duties = [db_access.get_action_label(action) for action in extra_conditions['duties']]
            extra_prohibitions = [db_access.get_action_label(action) for action in extra_conditions['prohibitions']]
            extra_conditions_licences.append({
                'LABEL': policy['LABEL'],
                'URI': url_for('controller.licence_routes', uri=policy['URI']),
                'PERMISSIONS': extra_permissions,
                'DUTIES': extra_duties,
                'PROHIBITIONS': extra_prohibitions
            })
        elif not policy_has_extra_conditions and policy_has_missing_conditions:
            missing_permissions = [db_access.get_action_label(action) for action in missing_conditions['permissions']]
            missing_duties = [db_access.get_action_label(action) for action in missing_conditions['duties']]
            missing_prohibitions = [db_access.get_action_label(action) for action in missing_conditions['prohibitions']]
            missing_conditions_licences.append({
                'LABEL': policy['LABEL'],
                'URI': url_for('controller.licence_routes', uri=policy['URI']),
                'PERMISSIONS': missing_permissions,
                'DUTIES': missing_duties,
                'PROHIBITIONS': missing_prohibitions
            })
    return {
        'perfect': perfect_fit_licences,
        'extra': extra_conditions_licences,
        'insufficient': missing_conditions_licences
    }
