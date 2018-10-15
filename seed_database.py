import sqlite3
import _conf
from unittest import mock
from controller import functions
import os
from uuid import uuid4
from controller import db_access

db = None


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
    cc_by_nd_4()
    cc_by_nc_nd_4()
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
    csiro_data_licence()
    csiro_open_source_software_licence()
    csiro_binary_software_licence()
    gpl3_csiro()
    cc_public_domain()
    cc_by_3_unported()
    cc_by_sa_3_unported()
    cc_by_nc_nd_3_unported()
    db_access.commit_db()


def readonly_licence():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'same_as': 'http://test.linked.data.gov.au/license/disco',
        'comment': 'This license only allows for one thing: the assignee may *read* the asset (dataset) for which this '
                   'license is assigned. The intent is for the assignee to be able to assess the dataset for purposes '
                   'such as evaluation for future use but nothing more: no on-publishing, no distribution etc.',
        'label': 'Discovery Read Only License'
    }
    rules = [{'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission', 'ACTIONS': ['Read']}]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_4():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY 4.0',
        'legal_code': 'https://creativecommons.org/licenses/by/4.0/legalcode',
        'see_also': 'https://creativecommons.org/licenses/by/4.0/',
        'creator': 'https://creativecommons.org',
        'same_as': 'http://test.linked.data.gov.au/license/cc-by-4.0',
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()),
         'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute', 'Reproduce', 'Derivative Works']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nd_4():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-ND 4.0',
        'legal_code': 'https://creativecommons.org/licenses/by-nd/4.0/legalcode',
        'see_also': 'https://creativecommons.org/licenses/by-nd/4.0/',
        'creator': 'https://creativecommons.org',
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()),
         'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute', 'Reproduce']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Notice', 'Derivative Works']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nc_nd_4():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-NC-ND 4.0',
        'legal_code': 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode',
        'see_also': 'https://creativecommons.org/licenses/by-nc-nd/4.0/',
        'creator': 'https://creativecommons.org'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()),
         'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute', 'Reproduction']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Commercial Use', 'Derivative Works']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_sa_3_au():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-SA 3.0 Australia',
        'jurisdiction': 'http://dbpedia.org/page/Australia',
        'legal_code': 'http://creativecommons.org/licenses/by-sa/3.0/au/legalcode',
        'has_version': '3.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'http://creativecommons.org/licenses/by-sa/3.0/au',
        'creator': 'https://creativecommons.org',
        'same_as': 'http://test.linked.data.gov.au/license/cc-by-sa-3.0-au'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_2_5_au():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY 2.5 Australia',
        'jurisdiction': 'http://dbpedia.org/page/Australia',
        'legal_code': 'https://creativecommons.org/licenses/by/2.5/au/legalcode',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'creator': 'https://creativecommons.org',
        'see_also': 'https://creativecommons.org/licenses/by/2.5/au/'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_2_au():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY 2.0 Australia',
        'jurisdiction': 'http://dbpedia.org/page/Australia',
        'legal_code': 'http://creativecommons.org/licenses/by/2.0/au/legalcode',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso629-2/eng',
        'see_also': 'http://creativecommons.org/licenses/by/2.0/au',
        'creator': 'https://creativecommons.org',
        'same_as': 'http://test.linked.data.gov.au/license/cc-by-2.0-au'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribute', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nc_nd_3_au():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-NC-ND 3.0 Australia',
        'jurisdiction': 'http://dbpedia.org/page/Australia',
        'has_version': '3.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'http://creativecommons.org/licenses/by-nc-nd/3.0/au',
        'same_as': 'http://test.linked.data.gov.au/license/cc-by-nc-nd-3.0-au',
        'creator': 'https://creativecommons.org',
        'legal_code': 'http://creativecommons.org/licenses/by-nc-nd/3.0/au/legalcode'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Derive', 'Commercial Use']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def gpl_3():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'GNU General Public License v3.0',
        'legal_code': 'http://gnu.org/licenses/gpl-3.0.html',
        'creator': 'http://fsf.org/',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'http://gnu.org/licenses/gpl-3.0.html',
        'same_as': 'http://www.gnu.org/licenses/gpl-3.0.rdf',
        'logo': 'http://www.gnu.org/graphics/gplv3-127x51.png'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice', 'Source Code']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def mit():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'MIT License',
        'legal_code': 'http://opensource.org/licenses/MIT',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [{'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
              'ACTIONS': ['Distribute', 'Reproduce', 'Derive', 'Sell']}]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_sa_4():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-SA 4.0',
        'legal_code': 'https://creativecommons.org/licenses/by-sa/4.0/legalcode',
        'see_also': 'http://creativecommons.org/licenses/by-sa/4.0/',
        'creator': 'https://creativecommons.org',
        'same_as': 'http://test.linked.data.gov.au/license/cc-by-sa-4.0'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derivative Works']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_zero_1():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC0',
        'legal_code': 'https://creativecommons.org/publicdomain/zero/1.0/legalcode',
        'see_also': 'http://creativecommons.org/publicdomain/zero/1.0/',
        'same_as': 'http://test.linked.data.gov.au/license/cc-zero-1.0',
        'creator': 'https://creativecommons.org',
        'has_version': '1.0'
    }
    rules = [{'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
              'ACTIONS': ['Distribute', 'Reproduce', 'Derivative Works']}]
    functions.create_policy(policy_uri, attributes, rules)


def gpl_2():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'GNU General Public License v2.0',
        'creator': 'http://fsf.org/',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'http://gnu.org/licenses/gpl-2.0.html',
        'same_as': 'http://www.gnu.org/licenses/gpl-2.0.rdf',
        'logo': 'http://www.gnu.org/graphics/gplv3-127x51.png'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice', 'Source Code']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def nem_513a():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'National Electricity Rules 5.13A Distribution zone substation information',
        'legal_code': 'https://www.aemc.gov.au/sites/default/files/2018-04/NER%20-%20v107%20-%20Chapter%205.PDF',
        'creator': 'http://data.bioregionalassessments.gov.au/person/car587',
        'has_version': '107',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'https://www.aemc.gov.au/sites/default/files/2018-04/NER%20-%20v107%20-%20Chapter%205.PDF'
    }
    rules = [{'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': [],
              'ASSIGNORS': ['http://test.linked.data.gov.au/board/B-0068'],
              'ASSIGNEES': ['http://example.com/group/power-companies']}]
    functions.create_policy(policy_uri, attributes, rules)


def ogl_uk():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'UK Non-commercial Government License',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'same_as': 'http://test.linked.data.gov.au/license/ogl-uk',
        'legal_code': 'http://www.nationalarchives.gov.uk/doc/non-commercial-government-licence/'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Derive', 'Distribute', 'Reproduce']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition', 'ACTIONS': ['Commercial Use']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def csiro_data_licence():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'CSIRO Data Licence',
        'comment': 'A licence for files downloaded from CSIRO\'s Data Access Portal',
        'creator': 'https://data.csiro.au/dap/',
        'jurisdiction': 'http://dbpedia.org/page/Australian_Capital_Territory',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124838',
        'see_also': 'https://confluence.csiro.au/display/daphelp/CSIRO+Data+Licence',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission', 'ACTIONS': ['Reproduce']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Grant Use', 'Commercial Use', 'Sell', 'Distribute']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def csiro_open_source_software_licence():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'CSIRO Open Source Software Licence',
        'comment': 'Based on MIT/BSD Open Source Licence',
        'creator': 'https://confluence.csiro.au/display/~coo353',
        'jurisdiction': 'http://dbpedia.org/page/Australian_Capital_Territory',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124838',
        'see_also': 'https://confluence.csiro.au/display/daphelp/CSIRO+Data+Licence',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def csiro_binary_software_licence():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'CSIRO Binary Software Licence',
        'comment': 'This is a template and further rights and obligations are set out in the Supplementary Licence '
                   'specific to the Software you are licensing from CSIRO.  Both documents together form this '
                   'agreement.',
        'creator': 'https://confluence.csiro.au/display/~coo353',
        'jurisdiction': 'http://dbpedia.org/page/New_South_Wales',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124802',
        'see_also': 'https://confluence.csiro.au/display/daphelp/CSIRO+Binary+Software+Licence+Agreement',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Install', 'Reproduction']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Concurrent Use', 'Modify', 'Distribute', 'Derive']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def gpl3_csiro():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'GPL3 with CSIRO Disclaimer',
        'comment': 'Except where otherwise indicated, including in the Supplementary Licence, CSIRO grants you a '
                   'licence to the Software on the terms of the GNU General Public Licence version 3 (GPLv3), '
                   'distributed at: http://www.gnu.org/licenses/gpl.html.',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124793',
        'creator': 'http://fsf.org/',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'https://confluence.csiro.au/display/daphelp/GPLv3+Licence+with+CSIRO+Disclaimer',
        'logo': 'http://www.gnu.org/graphics/gplv3-127x51.png'
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice', 'Source Code']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_public_domain():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'label': 'CC Public Domain',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'comment': 'A work with this licence is free of known restrictions under copyright law, including all related'
                   'and neighbouring rights. You can copy, modify, distribute and perform the work, even for commercial'
                   ' purposes, all without asking permission.',
        'see_also': 'https://creativecommons.org/publicdomain/mark/1.0/',
        'creator': 'https://creativecommons.org',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [{'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
              'ACTIONS': ['Reproduction', 'Derive', 'Distribution']}]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_3_unported():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'label': 'Creative Commons CC-BY 3.0',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'see_also': 'https://creativecommons.org/licenses/by/3.0/',
        'legal_code': 'https://creativecommons.org/licenses/by/3.0/legalcode',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'creator': 'https://creativecommons.org',
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Reproduction', 'Derive', 'Distribution']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_sa_3_unported():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'label': 'Creative Commons CC-BY-SA 3.0 Unported',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'see_also': 'https://creativecommons.org/licenses/by-sa/3.0/',
        'legal_code': 'https://creativecommons.org/licenses/by-sa/3.0/legalcode',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'creator': 'https://creativecommons.org',
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Reproduction', 'Derive', 'Distribution']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nc_nd_3_unported():
    policy_uri = _conf.BASE_URI + '/licence/' + str(uuid4())
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'label': 'Creative Commons Attribution Noncommercial No Derivatives 3.0 Unported Licence',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'see_also': 'https://creativecommons.org/licenses/by-nc-nd/3.0/',
        'legal_code': 'https://creativecommons.org/licenses/by-nc-nd/3.0/legalcode',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'creator': 'https://creativecommons.org',
    }
    rules = [
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Reproduction', 'Distribution']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Commercial Use', 'Derivative Works']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


if __name__ == '__main__':
    seed()
