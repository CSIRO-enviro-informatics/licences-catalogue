import sqlite3
import _conf
from unittest import mock
from controller import db_access
import os

db = None

ruletype = dict()
ruletype['PERMISSION'] = 'http://www.w3.org/ns/odrl/2/permission'
ruletype['PROHIBITION'] = 'http://www.w3.org/ns/odrl/2/prohibition'
ruletype['DUTY'] = 'http://www.w3.org/ns/odrl/2/duty'

status = dict()
status['SUBMITTED'] = 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted'


def get_db():
    global db
    if db:
        return db
    else:
        os.makedirs(os.path.dirname(_conf.DATABASE_PATH), exist_ok=True)
        db = sqlite3.connect(_conf.DATABASE_PATH)
        db.execute('PRAGMA foreign_keys = 1')
        db.row_factory = sqlite3.Row
        return db


@mock.patch('controller.db_access.get_db', side_effect=get_db)
def seed(mock):
    # Mocks out get_db() so this can be run independently of the Flask application
    readonly_licence()
    cc_by_4()
    cc_by_sa_3_au()
    cc_by_2_5_au()
    cc_by_2_au()


def readonly_licence():
    policy_uri = _conf.BASE_URI + '/licence/1'
    db_access.create_policy(policy_uri)
    permission_rule_uri = _conf.BASE_URI + '/rule/1'
    db_access.create_rule(permission_rule_uri, ruletype['PERMISSION'], 'Allow reading')
    db_access.add_action_to_rule(get_action_uri('Read'), permission_rule_uri)
    db_access.add_rule_to_policy(permission_rule_uri, policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Discovery Read Only License')
    db_access.set_policy_attribute(policy_uri, 'COMMENT', '''
        This license only allows for one thing: the assignee may *read* the asset (dataset) for which this license is 
        assigned. The intent is for the assignee to be able to assess the dataset for purposes such as evaluation for 
        future use but nothing more: no on-publishing, no distribution etc.
    ''')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/disco')


def cc_by_4():
    policy_uri = _conf.BASE_URI + '/licence/2'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC-BY 4.0')
    db_access.set_policy_attribute(policy_uri, 'LEGAL_CODE', 'http://creativecommons.org/licenses/by/4.0/')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/cc-by-4.0')
    permission_rule_uri = _conf.BASE_URI + '/rule/3'
    db_access.create_rule(
        permission_rule_uri,
        ruletype['PERMISSION'],
        'Allow distribution, reproduction and derivative works'
    )
    db_access.add_action_to_rule(get_action_uri('Distribute'), permission_rule_uri)
    db_access.add_action_to_rule(get_action_uri('Reproduce'), permission_rule_uri)
    db_access.add_action_to_rule(get_action_uri('Derivative Works'), permission_rule_uri)
    db_access.add_rule_to_policy(permission_rule_uri, policy_uri)
    duty_rule_uri = _conf.BASE_URI + '/rule/4'
    db_access.create_rule(
        duty_rule_uri,
        ruletype['DUTY'],
        'Must give credit and keep copyright notices intact'
    )
    db_access.add_action_to_rule(get_action_uri('Attribution'), duty_rule_uri)
    db_access.add_action_to_rule(get_action_uri('Notice'), duty_rule_uri)
    db_access.add_rule_to_policy(duty_rule_uri, policy_uri)


def cc_by_sa_3_au():
    policy_uri = _conf.BASE_URI + '/licence/3'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC-BY-SA 3.0 Australia')
    db_access.set_policy_attribute(policy_uri, 'JURISDICTION', 'http://dbpedia.org/page/Australia')
    db_access.set_policy_attribute(
        policy_uri,
        'LEGAL_CODE',
        'http://creativecommons.org/licenses/by-sa/3.0/au/legalcode'
    )
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '3.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SEE_ALSO', 'http://creativecommons.org/licenses/by-sa/3.0/au')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/cc-by-sa-3.0-au')
    permission_rule_uri = _conf.BASE_URI + '/rule/5'
    db_access.create_rule(
        permission_rule_uri,
        ruletype['PERMISSION'],
        'Allow distribution, reproduction and derivative works'
    )
    db_access.add_action_to_rule(get_action_uri('Distribute'), permission_rule_uri)
    db_access.add_action_to_rule(get_action_uri('Reproduce'), permission_rule_uri)
    db_access.add_action_to_rule(get_action_uri('Derive'), permission_rule_uri)
    db_access.add_rule_to_policy(permission_rule_uri, policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    duty_rule_uri = _conf.BASE_URI + '/rule/6'
    db_access.create_rule(
        duty_rule_uri,
        ruletype['DUTY'],
        'Must licence derivative works under the same licence'
    )
    db_access.add_action_to_rule(get_action_uri('Share Alike'), duty_rule_uri)
    db_access.add_rule_to_policy(duty_rule_uri, policy_uri)


def cc_by_2_5_au():
    policy_uri = _conf.BASE_URI + '/licence/4'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC-BY 2.5 Australia')
    db_access.set_policy_attribute(policy_uri, 'JURISDICTION', 'http://dbpedia.org/page/Australia')
    db_access.set_policy_attribute(
        policy_uri,
        'LEGAL_CODE',
        'https://creativecommons.org/licenses/by/2.5/au/legalcode'
    )
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '1.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SEE_ALSO', 'https://creativecommons.org/licenses/by/2.5/au/')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/5', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/6', policy_uri)


def cc_by_2_au():
    policy_uri = _conf.BASE_URI + '/licence/5'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC-BY 2.0 Australia')
    db_access.set_policy_attribute(policy_uri, 'JURISDICTION', 'http://dbpedia.org/page/Australia')
    db_access.set_policy_attribute(
        policy_uri,
        'LEGAL_CODE',
        'http://creativecommons.org/licenses/by/2.0/au/legalcode'
    )
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '1.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso629-2/eng')
    db_access.set_policy_attribute(policy_uri, 'SEE_ALSO', 'http://creativecommons.org/licenses/by/2.0/au')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/cc-by-2.0-au')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/5', policy_uri)


def get_action_uri(action_label):
    actions = db_access.get_all_actions()
    for action in actions:
        if action['LABEL'] == action_label:
            return action['URI']
    raise ValueError('Didn\'t find that action')


if __name__ == '__main__':
    seed()
