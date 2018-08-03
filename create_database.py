import sqlite3
import os
import _conf

'''
Beware:
This script completely wipes the database and starts over!
'''


def teardown():
    try:
        os.remove(_conf.DATABASE_PATH)
    except FileNotFoundError:
        pass


def rebuild():
    conn = sqlite3.connect(_conf.DATABASE_PATH)
    conn.execute('PRAGMA foreign_keys = 1')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS POLICY_TYPE (
            TYPE    TEXT    NOT NULL    PRIMARY KEY
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS POLICY (
            ID              INTEGER NOT NULL    PRIMARY KEY AUTOINCREMENT,
            URI             TEXT    NOT NULL    UNIQUE,
            TYPE            TEXT,
            LABEL           TEXT,
            JURISDICTION    TEXT,
            LEGAL_CODE      TEXT,
            HAS_VERSION     TEXT,
            LANGUAGE        TEXT,
            SEE_ALSO        TEXT,
            SAME_AS         TEXT,
            COMMENT         TEXT,
            LOGO            TEXT,
            CREATED         INT,
            STATUS          TEXT,
            FOREIGN KEY (TYPE) REFERENCES POLICY_TYPE (TYPE)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ASSET (
            ID          INTEGER NOT NULL    PRIMARY KEY AUTOINCREMENT,
            URI         TEXT    NOT NULL    UNIQUE,
            POLICY_ID   INT     NOT NULL,
            FOREIGN KEY (POLICY_ID) REFERENCES POLICY (ID) ON DELETE CASCADE
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS RULE_TYPE (
            TYPE    TEXT    NOT NULL    PRIMARY KEY
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS RULE (
            ID      INTEGER NOT NULL    PRIMARY KEY AUTOINCREMENT,
            TYPE    TEXT    NOT NULL,
            FOREIGN KEY (TYPE) REFERENCES RULE_TYPE(TYPE)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS POLICY_HAS_RULE (
            POLICY_ID   INT NOT NULL,
            RULE_ID     INT NOT NULL,
            FOREIGN KEY (POLICY_ID) REFERENCES POLICY (ID) ON DELETE CASCADE,
            FOREIGN KEY (RULE_ID) REFERENCES RULE (ID),
            PRIMARY KEY (POLICY_ID, RULE_ID)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS ACTION (
            ID          INTEGER NOT NULL    PRIMARY KEY AUTOINCREMENT,
            LABEL       TEXT    NOT NULL,
            URI         TEXT    NOT NULL,
            DEFINITION  TEXT    NOT NULL
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS RULE_HAS_ACTION (
            RULE_ID     INT NOT NULL,
            ACTION_ID   INT NOT NULL,
            FOREIGN KEY (RULE_ID) REFERENCES RULE (ID),
            FOREIGN KEY (ACTION_ID) REFERENCES ACTION (ID),
            PRIMARY KEY (RULE_ID, ACTION_ID)
        );
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS PARTY (
            ID  INTEGER NOT NULL PRIMARY KEY    AUTOINCREMENT,
            URI INT     NOT NULL
        );
    ''')
    conn.execute('''
        CREATE TABLE RULE_HAS_ASSIGNOR (
            PARTY_ID    INT NOT NULL,
            RULE_ID     INT NOT NULL,
            FOREIGN KEY (PARTY_ID) REFERENCES PARTY (ID),
            FOREIGN KEY (RULE_ID) REFERENCES RULE (ID) ON DELETE CASCADE,
            PRIMARY KEY (PARTY_ID, RULE_ID)
        );
    ''')
    conn.execute('''
        CREATE TABLE RULE_HAS_ASSIGNEE (
            PARTY_ID    INT NOT NULL,
            RULE_ID     INT NOT NULL,
            FOREIGN KEY (PARTY_ID) REFERENCES PARTY (ID),
            FOREIGN KEY (RULE_ID) REFERENCES RULE (ID) ON DELETE CASCADE,
            PRIMARY KEY (PARTY_ID, RULE_ID)
        );
    ''')
    conn.execute('''
        INSERT INTO POLICY_TYPE (TYPE) VALUES ('http://creativecommons.org/ns#License');
    ''')
    conn.execute('''
        INSERT INTO RULE_TYPE (TYPE) VALUES ('http://www.w3.org/ns/odrl/2/permission'),
                                            ('http://www.w3.org/ns/odrl/2/prohibition'),
                                            ('http://www.w3.org/ns/odrl/2/duty');
    ''')
    conn.execute('''
        INSERT INTO ACTION (LABEL, URI, DEFINITION) 
        VALUES  ('Accept Tracking', 'http://www.w3.org/ns/odrl/2/acceptTracking', 
                    'To accept that the use of the Asset may be tracked.'),
                ('Aggregate', 'http://www.w3.org/ns/odrl/2/aggregate', 
                    'To use the Asset or parts of it as part of a composite collection.'),
                ('Annotate', 'http://www.w3.org/ns/odrl/2/annotate', 
                    'To add explanatory notations/commentaries to the Asset without modifying the Asset in any other 
                    way.'),
                ('Anonymize', 'http://www.w3.org/ns/odrl/2/anonymize', 
                    'To anonymize all or parts of the Asset.'),
                ('Archive', 'http://www.w3.org/ns/odrl/2/archive', 
                    'To store the Asset (in a non-transient form).'),
                ('Attribute', 'http://www.w3.org/ns/odrl/2/attribute', 
                    'To attribute the use of the Asset.'),
                ('Attribution', 'http://creativecommons.org/ns#Attribution', 
                    'Credit be given to copyright holder and/or author.'),
                ('Commercial Use', 'http://creativecommons.org/ns#CommericalUse', 
                    'Exercising rights for commercial purposes.'),
                ('Compensate', 'http://www.w3.org/ns/odrl/2/compensate', 
                    'To compensate by transfer of some amount of value, if defined, for using or selling the Asset.'),
                ('Concurrent Use', 'http://www.w3.org/ns/odrl/2/concurrentUse', 
                    'To create multiple copies of the Asset that are being concurrently used.'),
                ('Delete', 'http://www.w3.org/ns/odrl/2/delete', 
                    'To permanently remove all copies of the Asset after it has been used.'),
                ('Derive', 'http://www.w3.org/ns/odrl/2/derive', 
                    'To create a new derivative Asset from this Asset and to edit or modify the derivative.'),
                ('Derivative Works', 'http://creativecommons.org/ns#DerivativeWorks', 
                    'Distribution of derivative works.'),
                ('Digitize', 'http://www.w3.org/ns/odrl/2/digitize', 
                    'To produce a digital copy of (or otherwise digitize) the Asset from its analogue form.'),
                ('Display', 'http://www.w3.org/ns/odrl/2/display', 
                    'To create a static and transient rendition of an Asset.'),
                ('Distribute', 'http://www.w3.org/ns/odrl/2/distribute', 
                    'To supply the Asset to third-parties.'),
                ('Distribution', 'http://creativecommons.org/ns#Distribution', 
                    'Distribution, public display, and publicly performance.'),
                ('Ensure Exclusivity', 'http://www.w3.org/ns/odrl/2/ensureExclusivity', 
                    'To ensure that the Rule on the Asset is exclusive.'),
                ('Execute', 'http://www.w3.org/ns/odrl/2/execute', 
                    'To run the computer program Asset.'),
                ('Extract', 'http://www.w3.org/ns/odrl/2/extract', 
                    'To extract parts of the Asset and to use it as a new Asset.'),
                ('Give', 'http://www.w3.org/ns/odrl/2/give', 
                    'To transfer the ownership of the Asset to a third party without compensation and while deleting the 
                    original asset.'),
                ('Grant Use', 'http://www.w3.org/ns/odrl/2/grantUse', 
                    'To grant the use of the Asset to third parties.'),
                ('Include', 'http://www.w3.org/ns/odrl/2/include', 
                    'To include other related assets in the Asset.'),
                ('Index', 'http://www.w3.org/ns/odrl/2/index', 
                    'To record the Asset in an index.'),
                ('Inform', 'http://www.w3.org/ns/odrl/2/inform', 
                    'To inform that an action has been performed on or in relation to the Asset.'),
                ('Install', 'http://www.w3.org/ns/odrl/2/install', 
                    'To load the computer program Asset onto a storage device which allows operating or running the 
                    Asset.'),
                ('Modify', 'http://www.w3.org/ns/odrl/2/modify', 
                    'To change existing content of the Asset. A new asset is not created by this action.'),
                ('Move', 'http://www.w3.org/ns/odrl/2/move', 
                    'To move the Asset from one digital location to another including deleting the original copy.'),
                ('Next Policy', 'http://www.w3.org/ns/odrl/2/nextPolicy', 
                    'To grant the specified Policy to a third party for their use of the Asset.'),
                ('Notice', 'http://creativecommons.org/ns#Notice', 
                    'Copyright and license notices be kept intact.'),
                ('Obtain Consent', 'http://www.w3.org/ns/odrl/2/obtainConsent', 
                    'To obtain verifiable consent to perform the requested action in relation to the Asset.'),
                ('Play', 'http://www.w3.org/ns/odrl/2/play', 
                    'To create a sequential and transient rendition of an Asset.'),
                ('Present', 'http://www.w3.org/ns/odrl/2/present', 
                    'To publicly perform the Asset.'),
                ('Print', 'http://www.w3.org/ns/odrl/2/print', 
                    'To create a tangible and permanent rendition of an Asset.'),
                ('Read', 'http://www.w3.org/ns/odrl/2/read', 
                    'To obtain data from the Asset.'),
                ('Reproduce', 'http://www.w3.org/ns/odrl/2/reproduce', 
                    'To make duplicate copies the Asset in any material form.'),
                ('Reproduction', 'http://creativecommons.org/ns#Reproduction', 
                    'Making multiple copies.'),
                ('Review Policy', 'http://www.w3.org/ns/odrl/2/reviewPolicy', 
                    'To review the Policy applicable to the Asset.'),
                ('Sell', 'http://www.w3.org/ns/odrl/2/sell', 
                    'To transfer the ownership of the Asset to a third party with compensation and while deleting the 
                    original asset.'),
                ('Share Alike', 'http://creativecommons.org/ns#ShareAlike', 
                    'Derivative works be licensed under the same terms or compatible terms as the original work.'),
                ('Sharing', 'http://creativecommons.org/ns#Sharing', 
                    'Permits commercial derivatives, but only non-commercial distribution.'),
                ('Source Code', 'http://creativecommons.org/ns#SourceCode', 
                    'Source code (the preferred form for making modifications) must be provided when exercising some 
                    rights granted by the license.'),
                ('Stream', 'http://www.w3.org/ns/odrl/2/stream', 
                    'To deliver the Asset in real-time.'),
                ('Synchronize', 'http://www.w3.org/ns/odrl/2/synchronize', 
                    'To use the Asset in timed relations with media (audio/visual) elements of another Asset.'),
                ('Text-to-speech', 'http://www.w3.org/ns/odrl/2/textToSpeech', 
                    'To have a text Asset read out loud.'),
                ('Transform', 'http://www.w3.org/ns/odrl/2/transform', 
                    'To convert the Asset into a different format.'),
                ('Translate', 'http://www.w3.org/ns/odrl/2/translate', 
                    'To translate the original natural language of an Asset into another natural language.'),
                ('Uninstall', 'http://www.w3.org/ns/odrl/2/uninstall', 
                    'To unload and delete the computer program Asset from a storage device and disable its readiness for 
                    operation.'),
                ('Watermark', 'http://www.w3.org/ns/odrl/2/watermark', 'To apply a watermark to the Asset.');
    ''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    teardown()
    rebuild()
