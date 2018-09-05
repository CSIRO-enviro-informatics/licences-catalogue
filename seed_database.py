import sqlite3
import _conf
from unittest import mock
from controller import db_access
import os

db = None

status = dict()
status['SUBMITTED'] = 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted'

rule_types_dict = {}


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
    global rule_types_dict
    permitted_rule_types = db_access.get_permitted_rule_types()
    for permitted_rule_type in permitted_rule_types:
        rule_types_dict[permitted_rule_type['LABEL']] = permitted_rule_type['URI']

    add_rules()
    readonly_licence()
    cc_by_4()
    cc_by_sa_3_au()
    cc_by_2_5_au()
    cc_by_2_au()
    cc_by_nc_nd_3_au()
    gpl_3()
    mit()
    cc_by_sa_4()
    cc_zero_1()
    gpl_2()
    nem_513a()
    ogl_uk()
    # test_licence()


def add_rules():
    rule_uri = _conf.BASE_URI + '/rule/1'
    db_access.create_rule(rule_uri, rule_types_dict['Permission'], 'Allow reading')
    db_access.add_action_to_rule(get_action_uri('Read'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/2'
    db_access.create_rule(
        rule_uri,
        rule_types_dict['Permission'],
        'Allow distribution, reproduction and derivative works'
    )
    db_access.add_action_to_rule(get_action_uri('Distribute'), rule_uri)
    db_access.add_action_to_rule(get_action_uri('Reproduce'), rule_uri)
    db_access.add_action_to_rule(get_action_uri('Derivative Works'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/3'
    db_access.create_rule(
        rule_uri,
        rule_types_dict['Duty'],
        'Must attribute the use of the asset'
    )
    db_access.add_action_to_rule(get_action_uri('Attribution'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/4'
    db_access.create_rule(
        rule_uri,
        rule_types_dict['Permission'],
        'Allow distribution, reproduction and deriving from the asset'
    )
    db_access.add_action_to_rule(get_action_uri('Distribute'), rule_uri)
    db_access.add_action_to_rule(get_action_uri('Reproduce'), rule_uri)
    db_access.add_action_to_rule(get_action_uri('Derive'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/5'
    db_access.create_rule(
        rule_uri,
        rule_types_dict['Duty'],
        'Must licence derivative works under the same licence'
    )
    db_access.add_action_to_rule(get_action_uri('Share Alike'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/6'
    db_access.create_rule(rule_uri, rule_types_dict['Permission'], 'Allow distribution and reproduction')
    db_access.add_action_to_rule(get_action_uri('Distribute'), rule_uri)
    db_access.add_action_to_rule(get_action_uri('Reproduce'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/7'
    db_access.create_rule(rule_uri, rule_types_dict['Prohibition'], 'Prohibit derivative works')
    db_access.add_action_to_rule(get_action_uri('Derive'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/8'
    db_access.create_rule(rule_uri, rule_types_dict['Duty'], 'Copyright and license notices must be kept intact')
    db_access.add_action_to_rule(get_action_uri('Notice'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/9'
    db_access.create_rule(
        rule_uri,
        rule_types_dict['Duty'],
        'Source code must be provided when exercising some rights granted by the license'
    )
    db_access.add_action_to_rule(get_action_uri('Source Code'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/10'
    db_access.create_rule(rule_uri, rule_types_dict['Permission'], 'Allow selling the asset')
    db_access.add_action_to_rule(get_action_uri('Sell'), rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/11'
    db_access.create_rule(rule_uri, rule_types_dict['Duty'], 'Participants')
    db_access.add_assignor_to_rule('http://test.linked.data.gov.au/board/B-0068', rule_uri)
    db_access.add_assignee_to_rule('http://example.com/group/power-companies', rule_uri)

    rule_uri = _conf.BASE_URI + '/rule/12'
    db_access.create_rule(rule_uri, rule_types_dict['Prohibition'], 'Prohibit commercial use')
    db_access.add_action_to_rule(get_action_uri('Commercial Use'), rule_uri)

    # rule_uri = _conf.BASE_URI + '/rule/13'
    # db_access.create_rule(rule_uri, ruletype['PERMISSION'])
    # db_access.add_action_to_rule(get_action_uri('Derive'), rule_uri)


def readonly_licence():
    policy_uri = _conf.BASE_URI + '/licence/1'
    db_access.create_policy(policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/1', policy_uri)
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
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/2', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)


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
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/5', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)


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
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/5', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)


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
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)


def cc_by_nc_nd_3_au():
    policy_uri = _conf.BASE_URI + '/licence/6'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC-BY-NC-ND 3.0 Australia')
    db_access.set_policy_attribute(policy_uri, 'JURISDICTION', 'http://dbpedia.org/page/Australia')
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '3.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SEE_ALSO', 'http://creativecommons.org/licenses/by-nc-nd/3.0/au')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/cc-by-nc-nd-3.0-au')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/6', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/7', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/12', policy_uri)


def gpl_3():
    policy_uri = _conf.BASE_URI + '/licence/7'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'GNU General Public License v3.0')
    db_access.set_policy_attribute(policy_uri, 'LEGAL_CODE', 'http://gnu.org/licenses/gpl-3.0.html')
    db_access.set_policy_attribute(policy_uri, 'CREATOR', 'http://fsf.org/')
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '1.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SEE_ALSO', 'http://gnu.org/licenses/gpl-3.0.html')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://www.gnu.org/licenses/gpl-3.0.rdf')
    db_access.set_policy_attribute(policy_uri, 'LOGO', 'http://www.gnu.org/graphics/gplv3-127x51.png')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/9', policy_uri)


def mit():
    policy_uri = _conf.BASE_URI + '/licence/8'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'MIT License')
    db_access.set_policy_attribute(policy_uri, 'LEGAL_CODE', 'http://opensource.org/licenses/MIT')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/gpl-2.0')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/10', policy_uri)


def cc_by_sa_4():
    policy_uri = _conf.BASE_URI + '/licence/9'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC-BY-SA 4.0')
    db_access.set_policy_attribute(policy_uri, 'LEGAL_CODE', 'http://creativecommons.org/licenses/by-sa/4.0/')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/cc-by-sa-4.0')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/2', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/5', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)


def cc_zero_1():
    policy_uri = _conf.BASE_URI + '/licence/10'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'Creative Commons CC0')
    db_access.set_policy_attribute(policy_uri, 'LEGAL_CODE', 'http://creativecommons.org/publicdomain/zero/1.0/')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/cc-zero-1.0')
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '1.0')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/2', policy_uri)


def gpl_2():
    policy_uri = _conf.BASE_URI + '/licence/11'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'GNU General Public License v2.0')
    db_access.set_policy_attribute(policy_uri, 'LEGAL_CODE', 'http://gnu.org/licenses/gpl-2.0.html')
    db_access.set_policy_attribute(policy_uri, 'CREATOR', 'http://fsf.org/')
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '1.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SEE_ALSO', 'http://gnu.org/licenses/gpl-2.0.html')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://www.gnu.org/licenses/gpl-2.0.rdf')
    db_access.set_policy_attribute(policy_uri, 'LOGO', 'http://www.gnu.org/graphics/gplv3-127x51.png')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/9', policy_uri)


def nem_513a():
    policy_uri = _conf.BASE_URI + '/licence/12'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(
        policy_uri,
        'LABEL',
        'National Electricity Rules 5.13A Distribution zone substation information'
    )
    db_access.set_policy_attribute(
        policy_uri,
        'LEGAL_CODE',
        'https://www.aemc.gov.au/sites/default/files/2018-04/NER%20-%20v107%20-%20Chapter%205.PDF'
    )
    db_access.set_policy_attribute(policy_uri, 'CREATOR', '''
        http://data.bioregionalassessments.gov.au/person/car587 http://data.bioregionalassessments.gov.au/person/tet004
    ''')
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '107')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(
        policy_uri,
        'SEE_ALSO',
        'https://www.aemc.gov.au/sites/default/files/2018-04/NER%20-%20v107%20-%20Chapter%205.PDF'
    )
    db_access.set_policy_attribute(
        policy_uri,
        'STATUS',
        'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted'
    )
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/11', policy_uri)


def ogl_uk():
    policy_uri = _conf.BASE_URI + '/licence/13'
    db_access.create_policy(policy_uri)
    db_access.set_policy_attribute(policy_uri, 'LABEL', 'UK Non-commercial Government License')
    db_access.set_policy_attribute(policy_uri, 'HAS_VERSION', '1.0')
    db_access.set_policy_attribute(policy_uri, 'LANGUAGE', 'http://www.lexvo.org/page/iso639-3/eng')
    db_access.set_policy_attribute(policy_uri, 'SAME_AS', 'http://test.linked.data.gov.au/license/ogl-uk')
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/3', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/4', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/8', policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/12', policy_uri)


def test_licence():
    policy_uri = _conf.BASE_URI + '/licence/14'
    db_access.create_policy(policy_uri)
    db_access.add_rule_to_policy(_conf.BASE_URI + '/rule/13', policy_uri)


def get_action_uri(action_label):
    actions = db_access.get_all_actions()
    for action in actions:
        if action['LABEL'] == action_label:
            return action['URI']
    raise ValueError('Didn\'t find that action')


if __name__ == '__main__':
    seed()
