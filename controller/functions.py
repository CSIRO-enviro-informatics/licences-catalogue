import re
from controller import db_access
from flask import url_for
import _conf
from uuid import uuid4


def create_policy(policy_uri, attributes=None, rules=None):
    """
    Creates an entire policy with the given URI, attributes and Rules.

    :param policy_uri:
    :param attributes:  Dictionary of optional attributes of the policy.
        Permitted attributes:   type, label, jurisdiction, legal_code, has_version, language, see_also
                                same_as, comment, logo, status
    :param rules: List of Rules. Each Rule should be a Dictionary containing the following elements:
        URI: string
        TYPE_URI: string    * At least one of TYPE_URI or TYPE_LABEL should be provided.
        TYPE_LABEL: string
        ASSIGNORS: List of strings
        ASSIGNEES: List of strings
        ACTIONS: List of strings (URIs or labels)
    :return:
    """
    if not is_valid_uri(policy_uri):
        raise ValueError('Not a valid URI: ' + policy_uri)

    permitted_rule_types = []

    db_access.create_policy(policy_uri)
    if attributes:
        for attr_name, attr_value in attributes.items():
            db_access.set_policy_attribute(policy_uri, attr_name, attr_value)
    if rules:
        for rule in rules:
            rule_uri = _conf.BASE_URI + '/rules/' + str(uuid4())
            if 'TYPE_URI' in rule:
                rule_type = rule['TYPE_URI']
            elif 'TYPE_LABEL' in rule:
                if not permitted_rule_types:
                    permitted_rule_types = db_access.get_permitted_rule_types()
                rule_type = get_rule_type_uri(rule['TYPE_LABEL'], permitted_rule_types)
                if not rule_type:
                    db_access.delete_policy(policy_uri)
                    raise ValueError('Cannot create policy - bad rule type provided')
            else:
                db_access.delete_policy(policy_uri)
                raise ValueError('Cannot create policy - no rule type provided.')
            db_access.create_rule(rule_uri, rule_type)
            for action in rule['ACTIONS']:
                if is_valid_uri(action):
                    action_uri = action
                else:
                    permitted_actions = db_access.get_all_actions()
                    action_uri = get_action_uri(action, permitted_actions)
                    if not action_uri:
                        db_access.delete_rule(rule_uri)
                        db_access.delete_policy(policy_uri)
                        raise ValueError('Cannot create policy - bad action provided.')
                db_access.add_action_to_rule(action_uri, rule_uri)
            if 'ASSIGNORS' in rule:
                for assignor in rule['ASSIGNORS']:
                    db_access.add_assignor_to_rule(assignor, rule_uri)
            if 'ASSIGNEES' in rule:
                for assignee in rule['ASSIGNEES']:
                    db_access.add_assignee_to_rule(assignee, rule_uri)
            db_access.add_rule_to_policy(rule_uri, policy_uri)


def is_valid_uri(uri):
    return True if re.match('\w+:(/?/?)[^\s]+', uri) else False


def get_rule_type_uri(label, permitted_rule_types):
    for permitted_rule_type in permitted_rule_types:
        if permitted_rule_type['LABEL'] == label:
            return permitted_rule_type['URI']
    return None


def get_action_uri(label, permitted_actions):
    for permitted_action in permitted_actions:
        if permitted_action['LABEL'] == label:
            return permitted_action['URI']
    return None


def search_policies(desired_rules):
    policy_uris = db_access.get_all_policies()
    policies = []
    for policy_uri in policy_uris:
        policy = db_access.get_policy(policy_uri)
        policy['RULES'] = [db_access.get_rule(rule_uri) for rule_uri in db_access.get_rules_for_policy(policy_uri)]
        policies.append(policy)

    results = []
    for policy in policies:
        # Compare desired rules and policy rules
        # If any policy rule isn't present in the desired rules, add it to the list of extra rules.
        extra_rules = []
        for rule in policy['RULES']:
            policy_rule_matches_a_desired_rule = False
            for desired_rule in desired_rules:
                if rule['TYPE_URI'] == desired_rule['TYPE_URI']:
                    for action in rule['ACTIONS']:
                        for desired_action in desired_rule['ACTIONS']:
                            if action['URI'] == desired_action['URI']:
                                policy_rule_matches_a_desired_rule = True
            if not policy_rule_matches_a_desired_rule:
                extra_rules.append(rule)
        # If any desired rule isn't present in the policy's rules, add it to the list of missing rules.
        missing_rules = []
        for desired_rule in desired_rules:
            desired_rule_matches_a_policy_rule = False
            for rule in policy['RULES']:
                if rule['TYPE_URI'] == desired_rule['TYPE_URI']:
                    for action in rule['ACTIONS']:
                        for desired_action in desired_rule['ACTIONS']:
                            if action['URI'] == desired_action['URI']:
                                desired_rule_matches_a_policy_rule = True
            if not desired_rule_matches_a_policy_rule:
                missing_rules.append(desired_rule)

        # Give the policy a rank based on how many differences it has from the desired rules
        # Missing requirements count more than extra ones
        differences_rank = len(extra_rules) + len(missing_rules) * 2

        if differences_rank < 5:  # Don't add policies that are too off-mark
            results.append({
                'LABEL': policy['LABEL'],
                'LINK': url_for('controller.licence_routes', uri=policy['URI']),
                'MISSING_RULES': missing_rules,
                'EXTRA_RULES': extra_rules,
                'DIFFERENCES': differences_rank
            })

    results.sort(key=lambda x: x['DIFFERENCES'])
    return results[:10]
