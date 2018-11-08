import _conf
from unittest import mock
from controller import functions
from uuid import uuid4
from controller import db_access
from controller.offline_db_access import get_db


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
    # nem_513a()
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
    policy_uri = _conf.BASE_URI + 'licence/b7d27814-a9ed-4cda-88d3-b85ea8ec5af0'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'same_as': 'http://test.linked.data.gov.au/license/disco',
        'comment': 'This license only allows for one thing: the assignee may *read* the asset (dataset) for which this '
                   'license is assigned. The intent is for the assignee to be able to assess the dataset for purposes '
                   'such as evaluation for future use but nothing more: no on-publishing, no distribution etc.',
        'label': 'Discovery Read Only License'
    }
    rules = [{'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission', 'ACTIONS': ['Read']}]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_4():
    policy_uri = _conf.BASE_URI + 'licence/19639d3a-1040-43a1-896c-c5efb2e5bb64'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()),
         'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute', 'Reproduce', 'Derivative Works']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nd_4():
    policy_uri = _conf.BASE_URI + 'licence/c0a5884a-b9cc-4df2-be9f-f94554a7e1cd'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-ND 4.0',
        'legal_code': 'https://creativecommons.org/licenses/by-nd/4.0/legalcode',
        'see_also': 'https://creativecommons.org/licenses/by-nd/4.0/',
        'creator': 'https://creativecommons.org',
    }
    rules = [
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()),
         'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute', 'Reproduce']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Notice', 'Derivative Works']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nc_nd_4():
    policy_uri = _conf.BASE_URI + 'licence/8242628b-5a5c-46bb-9a21-2d308a84984a'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'Creative Commons CC-BY-NC-ND 4.0',
        'legal_code': 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode',
        'see_also': 'https://creativecommons.org/licenses/by-nc-nd/4.0/',
        'creator': 'https://creativecommons.org'
    }
    rules = [
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()),
         'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute', 'Reproduction']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Commercial Use', 'Derivative Works']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_sa_3_au():
    policy_uri = _conf.BASE_URI + 'licence/41638ad5-d5a4-42d8-abbd-f36564072efe'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_2_5_au():
    policy_uri = _conf.BASE_URI + 'licence/b33fbf49-4bdf-4d6d-87eb-da1c8b9ba610'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_2_au():
    policy_uri = _conf.BASE_URI + 'licence/a1202e72-02de-4cdb-98ef-65ea32f99a80'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribute', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nc_nd_3_au():
    policy_uri = _conf.BASE_URI + 'licence/27235597-3ac8-4a16-a0d5-93e56269d119'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Derive', 'Commercial Use']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def gpl_3():
    policy_uri = _conf.BASE_URI + 'licence/897eaa75-ef96-4671-b738-ac2822516baf'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice', 'Source Code']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def mit():
    policy_uri = _conf.BASE_URI + 'licence/c0f54d35-48b3-4cb4-bbc8-6a4bac8444d6'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'MIT License',
        'legal_code': 'http://opensource.org/licenses/MIT',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [{'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
              'ACTIONS': ['Distribute', 'Reproduce', 'Derive', 'Sell']}]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_sa_4():
    policy_uri = _conf.BASE_URI + 'licence/33b9a7c8-982b-414c-bcb3-b3bb372a2a5e'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derivative Works']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_zero_1():
    policy_uri = _conf.BASE_URI + 'licence/f6e6e204-6a4d-4b05-aeb5-e37b4ba79e30'
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
    rules = [{'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
              'ACTIONS': ['Distribute', 'Reproduce', 'Derivative Works']}]
    functions.create_policy(policy_uri, attributes, rules)


def gpl_2():
    policy_uri = _conf.BASE_URI + 'licence/8eb9f3e1-4815-4a98-afca-02b38195231d'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + '/rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice', 'Source Code']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def nem_513a():
    db_access.create_party('http://test.linked.data.gov.au/board/B-0068')
    db_access.create_party('http://example.com/group/power-companies', 'Example Power Company', 'This is a Party representing some hypothetical power companies.')
    policy_uri = _conf.BASE_URI + 'licence/8d2f3d11-ec65-4f75-8b4f-6dc621695678'
    attributes = {
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'National Electricity Rules 5.13A Distribution zone substation information',
        'legal_code': 'https://www.aemc.gov.au/sites/default/files/2018-04/NER%20-%20v107%20-%20Chapter%205.PDF',
        'creator': 'http://data.bioregionalassessments.gov.au/person/car587',
        'has_version': '107',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'https://www.aemc.gov.au/sites/default/files/2018-04/NER%20-%20v107%20-%20Chapter%205.PDF'
    }
    rules = [{'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': [],
              'ASSIGNORS': [{'URI': 'http://test.linked.data.gov.au/board/B-0068'}],
              'ASSIGNEES': [{'URI': 'http://example.com/group/power-companies'}]}]
    functions.create_policy(policy_uri, attributes, rules)


def ogl_uk():
    policy_uri = _conf.BASE_URI + 'licence/43670b28-00b9-4828-854e-e5e99c0b0e5c'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Derive', 'Distribute', 'Reproduce']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition', 'ACTIONS': ['Commercial Use']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def csiro_data_licence():
    policy_uri = _conf.BASE_URI + 'licence/b89b47cc-0f73-49fe-9678-60abf8c4042d'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission', 'ACTIONS': ['Reproduce']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Grant Use', 'Commercial Use', 'Sell', 'Distribute']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def csiro_open_source_software_licence():
    policy_uri = _conf.BASE_URI + 'licence/b4d27e0f-d761-4f3d-8325-b14521f67fed'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'CSIRO Open Source Software Licence',
        'comment': 'Based on MIT/BSD Open Source Licence',
        'creator': 'https://data.csiro.au/dap/',
        'jurisdiction': 'http://dbpedia.org/page/Australian_Capital_Territory',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124838',
        'see_also': 'https://confluence.csiro.au/display/daphelp/CSIRO+Data+Licence',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission', 'ACTIONS': ['Distribute']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def csiro_binary_software_licence():
    policy_uri = _conf.BASE_URI + 'licence/10d5038a-586f-4c89-8e73-52b545f2fe9a'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'CSIRO Binary Software Licence',
        'comment': 'This is a template and further rights and obligations are set out in the Supplementary Licence '
                   'specific to the Software you are licensing from CSIRO.  Both documents together form this '
                   'agreement.',
        'creator': 'https://data.csiro.au/dap/',
        'jurisdiction': 'http://dbpedia.org/page/New_South_Wales',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124802',
        'see_also': 'https://confluence.csiro.au/display/daphelp/CSIRO+Binary+Software+Licence+Agreement',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Install', 'Reproduction']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Concurrent Use', 'Modify', 'Distribute', 'Derive']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def gpl3_csiro():
    policy_uri = _conf.BASE_URI + 'licence/4256402d-c120-48e0-99ef-fe34e300373f'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'label': 'GPL3 with CSIRO Disclaimer',
        'comment': 'Except where otherwise indicated, including in the Supplementary Licence, CSIRO grants you a '
                   'licence to the Software on the terms of the GNU General Public Licence version 3 (GPLv3), '
                   'distributed at: http://www.gnu.org/licenses/gpl.html.',
        'legal_code': 'https://confluence.csiro.au/plugins/viewsource/viewpagesrc.action?pageId=267124793',
        'creator': 'https://data.csiro.au/dap/',
        'has_version': '1.0',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'see_also': 'https://confluence.csiro.au/display/daphelp/GPLv3+Licence+with+CSIRO+Disclaimer',
        'logo': 'http://www.gnu.org/graphics/gplv3-127x51.png'
    }
    rules = [
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Distribute', 'Reproduce', 'Derive']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Notice', 'Source Code']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_public_domain():
    policy_uri = _conf.BASE_URI + 'licence/26f6f853-8e04-4e37-a4ec-9d368242a681'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'label': 'CC Public Domain',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'comment': 'A work with this licence is free of known restrictions under copyright law, including all related '
                   'and neighbouring rights. You can copy, modify, distribute and perform the work, even for commercial'
                   ' purposes, all without asking permission.',
        'see_also': 'https://creativecommons.org/publicdomain/mark/1.0/',
        'creator': 'https://creativecommons.org',
        'language': 'http://www.lexvo.org/page/iso639-3/eng'
    }
    rules = [{'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
              'ACTIONS': ['Reproduction', 'Derive', 'Distribution']}]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_3_unported():
    policy_uri = _conf.BASE_URI + 'licence/1cc336f3-fb44-434e-8597-4b0a31fda0a9'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Reproduction', 'Derive', 'Distribution']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty', 'ACTIONS': ['Attribution', 'Notice']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_sa_3_unported():
    policy_uri = _conf.BASE_URI + 'licence/c51ace58-709b-4564-826a-01ed1031482e'
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
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Reproduction', 'Derive', 'Distribution']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Share Alike']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


def cc_by_nc_nd_3_unported():
    policy_uri = _conf.BASE_URI + 'licence/9235dc35-d678-4d7b-a9af-8e1574751a4f'
    attributes = {
        'type': 'http://creativecommons.org/ns#License',
        'label': 'Creative Commons CC-BY-SA-NC-ND 3.0 Unported',
        'status': 'http://dd.eionet.europa.eu/vocabulary/datadictionary/status/submitted',
        'see_also': 'https://creativecommons.org/licenses/by-nc-nd/3.0/',
        'legal_code': 'https://creativecommons.org/licenses/by-nc-nd/3.0/legalcode',
        'language': 'http://www.lexvo.org/page/iso639-3/eng',
        'creator': 'https://creativecommons.org',
    }
    rules = [
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Permission',
         'ACTIONS': ['Reproduction', 'Distribution']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Duty',
         'ACTIONS': ['Attribution', 'Notice']},
        {'URI': _conf.BASE_URI + 'rule/' + str(uuid4()), 'TYPE_LABEL': 'Prohibition',
         'ACTIONS': ['Commercial Use', 'Derivative Works']}
    ]
    functions.create_policy(policy_uri, attributes, rules)


if __name__ == '__main__':
    seed()
