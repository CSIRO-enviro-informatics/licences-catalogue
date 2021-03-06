import re
from controller import db_access
from flask import url_for, jsonify
import _conf
from uuid import uuid4
from rdflib import Graph, URIRef, BNode, OWL, RDF, RDFS, Literal
from rdflib.namespace import DCTERMS, FOAF, XSD, SKOS

ADMS = 'http://www.w3.org/ns/adms#'
CREATIVE_COMMONS = 'http://creativecommons.org/ns#'
ODRL = 'http://www.w3.org/ns/odrl/2/'
REG = 'http://purl.org/linked-data/registry#'
party_register_comment = 'This is a register (controlled list) of machine-readable Parties. The Party entity could be' \
                         ' a person, group of people, organisation, or agent. An agent is a person or thing that take' \
                         's an active role or produces a specified effect.'


def create_policy(policy_uri, attributes=None, rules=None):
    """
    Creates an entire policy with the given URI, attributes and Rules.
    Will attempt to use Rule Type and Actions whether they are given by URI or Label.
    If there is an error at any point, will rollback all changes to database to avoid leaving partially created
    policies.

    :param policy_uri:
    :param attributes:  Dictionary of optional attributes of the policy.
        Permitted attributes:   type, label, jurisdiction, legal_code, has_version, language, see_also
                                same_as, comment, logo, status
    :param rules: List of Rules. Each Rule should be a Dictionary containing the following elements:
        TYPE_URI*: string (i.e. 'http://www.w3.org/ns/odrl/2/duty')
        TYPE_LABEL*: string (i.e. 'duty')
        * At least one of TYPE_URI or TYPE_LABEL should be provided, but both are not required
        ASSIGNORS: List of Assignors. Each Assignor should be a Dictionary containing a URI, LABEL and COMMENT.
        ASSIGNEES: List of Assignees.  Each Assignee should be a Dictionary containing a URI, LABEL and COMMENT.
        ACTIONS: List of strings (URIs or labels)
    :return:
    """
    if not is_valid_uri(policy_uri):
        raise ValueError('Not a valid URI: ' + policy_uri)

    permitted_rule_types = []

    try:
        db_access.create_policy(policy_uri)
        if attributes:
            for attr_name, attr_value in attributes.items():
                db_access.set_policy_attribute(policy_uri, attr_name, attr_value)
        if rules:
            for rule in rules:
                rule_uri = _conf.BASE_URI + 'rules/' + str(uuid4())
                if 'TYPE_URI' in rule:
                    rule_type = rule['TYPE_URI']
                elif 'TYPE_LABEL' in rule:
                    if not permitted_rule_types:
                        permitted_rule_types = db_access.get_permitted_rule_types()
                    rule_type = get_rule_type_uri(rule['TYPE_LABEL'], permitted_rule_types)
                    if not rule_type:
                        raise ValueError('Cannot create policy - Rule type ' + rule['TYPE_LABEL'] +
                                         ' is not permitted')
                else:
                    raise ValueError('Cannot create policy - no Rule type provided')
                db_access.create_rule(rule_uri, rule_type)
                for action in rule['ACTIONS']:
                    if action:
                        if is_valid_uri(action):
                            action_uri = action
                        else:
                            permitted_actions = db_access.get_all_actions()
                            action_uri = get_action_uri(action, permitted_actions)
                            if not action_uri:
                                raise ValueError('Cannot create policy - Action ' + action + ' is not permitted')
                        db_access.add_action_to_rule(action_uri, rule_uri)
                if 'ASSIGNORS' in rule:
                    for assignor in rule['ASSIGNORS']:
                        if not db_access.party_exists(assignor['URI']):
                            db_access.create_party(assignor['URI'], assignor['LABEL'], assignor['COMMENT'])
                        db_access.add_assignor_to_rule(assignor['URI'], rule_uri)
                if 'ASSIGNEES' in rule:
                    for assignee in rule['ASSIGNEES']:
                        if not db_access.party_exists(assignee['URI']):
                            db_access.create_party(assignee['URI'], assignee['LABEL'], assignee['COMMENT'])
                        db_access.add_assignee_to_rule(assignee['URI'], rule_uri)
                db_access.add_rule_to_policy(rule_uri, policy_uri)
    except Exception as error:
        db_access.rollback_db()
        raise error
    db_access.commit_db()


def is_valid_uri(uri):
    # Checks if the URI is valid
    return True if re.match('\w+:(/?/?)[^\s]+', uri) else False


def get_rule_type_uri(label, permitted_rule_types):
    # Takes a ruletype Label tries to figure out the corresponding URI
    for permitted_rule_type in permitted_rule_types:
        if permitted_rule_type['LABEL'] == label:
            return permitted_rule_type['URI']
    return None


def get_action_uri(label, permitted_actions):
    # Takes an Action Label and tries to figure out the corresponding URI
    for permitted_action in permitted_actions:
        if permitted_action['LABEL'] == label:
            return permitted_action['URI']
    return None


def filter_policies(desired_rules, num_results=10):
    """
    Filters through all available policies according to the rules supplied. Does not take assignors or assignees into
    account at this time.

    :param desired_rules: A List of Rules. Each Rule is a Dictionary containing the following elements:
        TYPE_URI: string
        ACTIONS: A List of Actions. Each Action is a Dictionary containing a URI
    :param num_results: The maximum number of policies to return
    :return: A List of Policies. Each Policy is a Dictionary containing the following elements:
        LABEL: string
        LINK: string
        DIFFERENCES: int
        RULES: A List of Rules. Each Rule is a Dictionary containing the following elements:
            URI: string
            LABEL: string
            TYPE_URI: string
            TYPE_LABEL: string
            ASSIGNORS: List of Assignors. Each Assignor is a Dictionary containing a URI, LABEL and COMMENT.
            ASSIGNEES: List of Assignees.  Each Assignee is a Dictionary containing a URI, LABEL and COMMENT.
            ACTIONS: List of Actions. Each Action is a Dictionary containing a URI, LABEL and DEFINITION.
    """
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
            for action in rule['ACTIONS']:
                policy_rule_matches_a_desired_rule = False
                for desired_rule in desired_rules:
                    if rule['TYPE_URI'] == desired_rule['TYPE_URI']:
                        for desired_action in desired_rule['ACTIONS']:
                            if action['URI'] == desired_action['URI']:
                                policy_rule_matches_a_desired_rule = True
                if not policy_rule_matches_a_desired_rule:
                    extra_rules.append(rule)
        # If any desired rule isn't present in the policy's rules, skip to next policy
        policy_has_missing_rules = False
        for desired_rule in desired_rules:
            desired_rule_matches_a_policy_rule = False
            for rule in policy['RULES']:
                if rule['TYPE_URI'] == desired_rule['TYPE_URI']:
                    for action in rule['ACTIONS']:
                        for desired_action in desired_rule['ACTIONS']:
                            if action['URI'] == desired_action['URI']:
                                desired_rule_matches_a_policy_rule = True
            if not desired_rule_matches_a_policy_rule:
                policy_has_missing_rules = True
        if policy_has_missing_rules:
            continue

        results.append({
            'LABEL': policy['LABEL'],
            'LINK': url_for('controller.licence_routes', uri=policy['URI']),
            'RULES': policy['RULES'],
            'DIFFERENCES': len(extra_rules)
        })
    results.sort(key=lambda x: x['DIFFERENCES'])
    return results[:num_results]


def get_policy_rdf(policy, rules):
    """
    Converts a policy into RDF format

    :param policy:
    :param rules: The rules which are included in the policy
    :return: an RDFlib graph
    """
    graph = Graph()
    graph.bind('odrl', ODRL)
    graph.bind('cc', CREATIVE_COMMONS)
    graph.bind('owl', OWL)
    graph.bind('dct', DCTERMS)
    graph.bind('foaf', FOAF)
    graph.bind('adms', ADMS)
    policy_node = URIRef(policy['URI'])
    graph.add((policy_node, RDF.type, URIRef(ODRL + 'Policy')))
    if policy['TYPE']:
        graph.add((policy_node, RDF.type, URIRef(policy['TYPE'])))
    if policy['LABEL']:
        graph.add((policy_node, RDFS.label, Literal(policy['LABEL'], lang='en')))
    if policy['COMMENT']:
        graph.add((policy_node, RDFS.comment, Literal(policy['COMMENT'], lang='en')))
    if policy['CREATED']:
        graph.add((policy_node, DCTERMS.created, Literal(policy['CREATED'], datatype=XSD.date)))
    if policy['CREATOR']:
        graph.add((policy_node, DCTERMS.creator, URIRef(policy['CREATOR'])))
    if policy['HAS_VERSION']:
        graph.add((policy_node, DCTERMS.hasVersion, Literal(policy['HAS_VERSION'])))
    if policy['JURISDICTION']:
        graph.add((policy_node, URIRef(CREATIVE_COMMONS + 'jurisdiction'), URIRef(policy['JURISDICTION'])))
    if policy['LANGUAGE']:
        graph.add((policy_node, DCTERMS.language, URIRef(policy['LANGUAGE'])))
    if policy['LEGAL_CODE']:
        graph.add((policy_node, URIRef(CREATIVE_COMMONS + 'legalcode'), URIRef(policy['LEGAL_CODE'])))
    if policy['LOGO']:
        graph.add((policy_node, URIRef(FOAF + 'logo'), URIRef(policy['LOGO'])))
    if policy['SAME_AS']:
        graph.add((policy_node, OWL.sameAs, URIRef(policy['SAME_AS'])))
    if policy['SEE_ALSO']:
        graph.add((policy_node, RDFS.seeAlso, URIRef(policy['SEE_ALSO'])))
    if policy['STATUS']:
        graph.add((policy_node, URIRef(ADMS + 'status'), URIRef(policy['STATUS'])))
    for rule in rules:
        rule_node = BNode()
        graph.add((policy_node, URIRef(ODRL + rule['TYPE_LABEL'].lower()), rule_node))
        graph.add((rule_node, RDF.type, URIRef(ODRL + rule['TYPE_LABEL'])))
        for action in rule['ACTIONS']:
            graph.add((rule_node, URIRef(ODRL + 'action'), URIRef(action['URI'])))
        for assignor in rule['ASSIGNORS']:
            graph.add((rule_node, URIRef(ODRL + 'assignor'), URIRef(assignor)))
        for assignee in rule['ASSIGNEES']:
            graph.add((rule_node, URIRef(ODRL + 'assignee'), URIRef(assignee)))
    return graph


def get_policy_json(policy, rules):
    """
    Converts a policy into JSON format

    :param policy:
    :param rules: The rules which are included in the policy
    :return: A Flask Response containing the policy in JSON format
    """
    rules_json = []
    for rule in rules:
        rules_json.append({
            rule['URI']: {
                'label': rule['LABEL'],
                'type': [rule['TYPE_URI'], ODRL + 'Rule'],
                'assignors': rule['ASSIGNORS'],
                'assignees': rule['ASSIGNEES'],
                'actions': [action['URI'] for action in rule['ACTIONS']]
            }
        })
    policy_json = {
        policy['URI']: {
            'comment': policy['COMMENT'],
            'created': policy['CREATED'],
            'creator': policy['CREATOR'],
            'hasVersion': policy['HAS_VERSION'],
            'jurisdiction': policy['JURISDICTION'],
            'label': policy['LABEL'],
            'language': policy['LANGUAGE'],
            'legalCode': policy['LEGAL_CODE'],
            'logo': policy['LOGO'],
            'sameAs': policy['SAME_AS'],
            'seeAlso': policy['SEE_ALSO'],
            'status': policy['STATUS'],
            'type': policy['TYPE'],
            'rules': rules_json
        }
    }
    return jsonify(policy_json)


def get_policies_rdf(policies):
    """
    Converts a policy register into RDF format

    :param policies:
    :return: an RDFlib graph
    """
    graph = Graph()
    graph.bind('odrl', ODRL)
    graph.bind('cc', CREATIVE_COMMONS)
    graph.bind('owl', OWL)
    graph.bind('dct', DCTERMS)
    graph.bind('foaf', FOAF)
    graph.bind('adms', ADMS)
    graph.bind('reg', REG)
    register_node = URIRef(url_for('controller.licence_routes', _external=True))
    graph.add((register_node, RDF.type, URIRef(REG + 'Register')))
    graph.add((register_node, RDFS.label, Literal('Licence Register')))
    graph.add((register_node, RDFS.comment, Literal('This is a register (controlled list) of machine-readable Licenses '
                                                    'which are a particular type of Policy.')))
    graph.add((register_node, URIRef(REG + 'containedItemClass'), URIRef(ODRL + 'Policy')))
    for policy in policies:
        policy_node = URIRef(policy['URI'])
        graph.add((policy_node, RDF.type, URIRef(ODRL + 'Policy')))
        if policy['TYPE']:
            graph.add((policy_node, RDF.type, URIRef(policy['TYPE'])))
        if policy['LABEL']:
            graph.add((policy_node, RDFS.label, Literal(policy['LABEL'], lang='en')))
        if policy['COMMENT']:
            graph.add((policy_node, RDFS.comment, Literal(policy['COMMENT'], lang='en')))
        graph.add((policy_node, URIRef(REG + 'register'), URIRef(register_node)))
    return graph


def get_policies_json(policies):
    """
    Converts a policy register into JSON format

    :param policies:
    :return: A Flask Response containing the policies in JSON format
    """
    register_uri = url_for('controller.licence_routes', _external=True)
    policy_json = {
        register_uri: {
            'type': REG + 'Register',
            'label': 'Licence Register',
            'comment': 'This is a register (controlled list) of machine-readable Licenses which are a particular '
                       'type of Policy.',
            'containedItemClass': CREATIVE_COMMONS + 'License'
        }
    }
    for policy in policies:
        policy_json[policy['URI']] = {
            'type': CREATIVE_COMMONS + 'License',
            'label': policy['LABEL'],
            'comment': policy['COMMENT'],
            'register': register_uri
        }
    return jsonify(policy_json)


def get_actions_rdf(actions):
    """
    Converts an action register into RDF format

    :param actions:
    :return: an RDFlib graph
    """
    graph = Graph()
    graph.bind('odrl', 'http://www.w3.org/ns/odrl/2/')
    graph.bind('skos', SKOS)
    register_node = URIRef(url_for('controller.action_register', _external=True))
    graph.add((register_node, RDF.type, URIRef(REG + 'Register')))
    graph.add((register_node, RDFS.label, Literal('Action Register')))
    graph.add((
        register_node,
        RDFS.comment,
        Literal('This is a register (controlled list) of machine-readable Actions.')
    ))
    graph.add((register_node, URIRef(REG + 'containedItemClass'), URIRef(ODRL + 'Action')))
    for action in actions:
        action_node = URIRef(action['URI'])
        graph.add((action_node, RDF.type, URIRef(ODRL + 'Action')))
        graph.add((action_node, RDFS.label, Literal(action['LABEL'], lang='en')))
        graph.add((action_node, SKOS.definition, Literal(action['DEFINITION'], lang='en')))
        graph.add((action_node, URIRef(REG + 'register'), URIRef(register_node)))
    return graph


def get_actions_json(actions):
    """
    Converts an action register into JSON format

    :param actions:
    :return: A Flask Response containing the actions in JSON format
    """
    register_uri = url_for('controller.action_register', _external=True)
    actions_json = {
        register_uri: {
            'type': REG + 'Register',
            'label': 'Action Register',
            'comment': 'This is a register (controlled list) of machine-readable Actions.',
            'containedItemClass': ODRL + 'Action'
        }
    }
    for action in actions:
        actions_json[action['URI']] = {
            'type': ODRL + 'Action',
            'label': action['LABEL'],
            'comment': action['DEFINITION'],
            'register': register_uri
        }
    return jsonify(actions_json)


def get_parties_rdf(parties):
    """
    Converts a party register into RDF format

    :param parties:
    :return: an RDFlib graph
    """
    graph = Graph()
    graph.bind('odrl', 'http://www.w3.org/ns/odrl/2/')
    graph.bind('skos', SKOS)
    register_node = URIRef(url_for('controller.party_register', _external=True))
    graph.add((register_node, RDF.type, URIRef(REG + 'Register')))
    graph.add((register_node, RDFS.label, Literal('Party Register')))
    graph.add((
        register_node,
        RDFS.comment,
        Literal(party_register_comment)
    ))
    graph.add((register_node, URIRef(REG + 'containedItemClass'), URIRef(ODRL + 'Party')))
    for party in parties:
        party_node = URIRef(party['URI'])
        graph.add((party_node, RDF.type, URIRef(ODRL + 'Party')))
        if party['LABEL']:
            graph.add((party_node, RDFS.label, Literal(party['LABEL'], lang='en')))
        if party['COMMENT']:
            graph.add((party_node, RDFS.comment, Literal(party['COMMENT'], lang='en')))
        graph.add((party_node, URIRef(REG + 'register'), URIRef(register_node)))
    return graph


def get_parties_json(parties):
    """
    Converts a party register into JSON format

    :param parties:
    :return: A Flask Response containing the actions in JSON format
    """
    register_uri = url_for('controller.party_register', _external=True)
    parties_json = {
        register_uri: {
            'type': REG + 'Register',
            'label': 'Party Register',
            'comment': party_register_comment,
            'containedItemClass': ODRL + 'Party'
        }
    }
    for party in parties:
        parties_json[party['URI']] = {
            'type': ODRL + 'Party',
            'label': party['LABEL'],
            'comment': party['COMMENT'],
            'register': register_uri
        }
    return jsonify(parties_json)
