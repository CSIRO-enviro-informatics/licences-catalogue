import sqlite3
import os
import _conf

'''
Beware:
This script completely wipes the database and starts over!
'''

try:
    os.remove('model/policies.db')
except FileNotFoundError:
    pass

conn = sqlite3.connect(_conf.DATABASE_PATH)
conn.execute('PRAGMA foreign_keys = 1')
conn.execute('''
    CREATE TABLE POLICY (
        ID              INT     NOT NULL    PRIMARY KEY,
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
        STATUS          TEXT
    );
''')
conn.execute('''
    CREATE TABLE ASSET (
        ID          INT     NOT NULL    PRIMARY KEY,
        URI         TEXT    NOT NULL,
        POLICY_ID   INT     NOT NULL,
        FOREIGN KEY (POLICY_ID) REFERENCES POLICY (ID)
    );
''')
conn.execute('''
    CREATE TABLE RULE_TYPE (
        TYPE    TEXT    NOT NULL    PRIMARY KEY
    );
''')
conn.execute('''
    CREATE TABLE RULE (
        ID      INT     NOT NULL    PRIMARY KEY,
        TYPE    TEXT    NOT NULL,
        FOREIGN KEY (TYPE) REFERENCES RULE_TYPE(TYPE)
    );
''')
conn.execute('''
    CREATE TABLE POLICY_HAS_RULE (
        POLICY_ID   INT NOT NULL,
        RULE_ID     INT NOT NULL,
        FOREIGN KEY (POLICY_ID) REFERENCES POLICY (ID),
        FOREIGN KEY (RULE_ID) REFERENCES RULE (ID),
        PRIMARY KEY (POLICY_ID, RULE_ID)
    );
''')
conn.execute('''
    CREATE TABLE ACTION (
        TYPE    TEXT    NOT NULL    PRIMARY KEY
    );
''')
conn.execute('''
    CREATE TABLE RULE_HAS_ACTION (
        RULE_ID INT NOT NULL,
        ACTION  TEXT NOT NULL,
        FOREIGN KEY (RULE_ID) REFERENCES RULE (ID),
        FOREIGN KEY (ACTION) REFERENCES ACTION (TYPE),
        PRIMARY KEY (RULE_ID, ACTION)
    );
''')
conn.execute('''
    CREATE TABLE PARTY (
        ID  INT NOT NULL PRIMARY KEY,
        URI INT NOT NULL
    );
''')
conn.execute('''
    CREATE TABLE RULE_HAS_ASSIGNOR (
        PARTY_ID    INT NOT NULL,
        RULE_ID     INT NOT NULL,
        FOREIGN KEY (PARTY_ID) REFERENCES PARTY (ID),
        FOREIGN KEY (RULE_ID) REFERENCES RULE (ID),
        PRIMARY KEY (PARTY_ID, RULE_ID)
    );
''')
conn.execute('''
    CREATE TABLE RULE_HAS_ASSIGNEE (
        PARTY_ID    INT NOT NULL,
        RULE_ID     INT NOT NULL,
        FOREIGN KEY (PARTY_ID) REFERENCES PARTY (ID),
        FOREIGN KEY (RULE_ID) REFERENCES RULE (ID),
        PRIMARY KEY (PARTY_ID, RULE_ID)
    );
''')
conn.execute('''
    INSERT INTO RULE_TYPE (TYPE) VALUES ('http://www.w3.org/ns/odrl/2/permission'),
                                        ('http://www.w3.org/ns/odrl/2/prohibition'),
                                        ('http://www.w3.org/ns/odrl/2/duty');
''')
conn.execute('''
    INSERT INTO ACTION (TYPE) VALUES    ('http://www.w3.org/ns/odrl/2/acceptTracking'),
                                        ('http://www.w3.org/ns/odrl/2/aggregate'),
                                        ('http://www.w3.org/ns/odrl/2/annotate'),
                                        ('http://www.w3.org/ns/odrl/2/anonymize'),
                                        ('http://www.w3.org/ns/odrl/2/archive'),
                                        ('http://www.w3.org/ns/odrl/2/attribute'),
                                        ('http://creativecommons.org/ns#Attribution'),
                                        ('http://creativecommons.org/ns#CommericalUse'),
                                        ('http://www.w3.org/ns/odrl/2/compensate'),
                                        ('http://www.w3.org/ns/odrl/2/concurrentUse'),
                                        ('http://www.w3.org/ns/odrl/2/delete'),
                                        ('http://www.w3.org/ns/odrl/2/derive'),
                                        ('http://creativecommons.org/ns#DerivativeWorks'),
                                        ('http://www.w3.org/ns/odrl/2/digitize'),
                                        ('http://www.w3.org/ns/odrl/2/display'),
                                        ('http://www.w3.org/ns/odrl/2/distribute'),
                                        ('http://creativecommons.org/ns#Distribution'),
                                        ('http://www.w3.org/ns/odrl/2/ensureExclusivity'),
                                        ('http://www.w3.org/ns/odrl/2/execute'),
                                        ('http://www.w3.org/ns/odrl/2/extract'),
                                        ('http://www.w3.org/ns/odrl/2/give'),
                                        ('http://www.w3.org/ns/odrl/2/grantUse'),
                                        ('http://www.w3.org/ns/odrl/2/include'),
                                        ('http://www.w3.org/ns/odrl/2/index'),
                                        ('http://www.w3.org/ns/odrl/2/inform'),
                                        ('http://www.w3.org/ns/odrl/2/install'),
                                        ('http://www.w3.org/ns/odrl/2/modify'),
                                        ('http://www.w3.org/ns/odrl/2/move'),
                                        ('http://www.w3.org/ns/odrl/2/nextPolicy'),
                                        ('http://creativecommons.org/ns#Notice'),
                                        ('http://www.w3.org/ns/odrl/2/obtainConsent'),
                                        ('http://www.w3.org/ns/odrl/2/play'),
                                        ('http://www.w3.org/ns/odrl/2/present'),
                                        ('http://www.w3.org/ns/odrl/2/print'),
                                        ('http://www.w3.org/ns/odrl/2/read'),
                                        ('http://www.w3.org/ns/odrl/2/reproduce'),
                                        ('http://creativecommons.org/ns#Reproduction'),
                                        ('http://www.w3.org/ns/odrl/2/reviewPolicy'),
                                        ('http://www.w3.org/ns/odrl/2/sell'),
                                        ('http://creativecommons.org/ns#ShareAlike'),
                                        ('http://creativecommons.org/ns#Sharing'),
                                        ('http://creativecommons.org/ns#SourceCode'),
                                        ('http://www.w3.org/ns/odrl/2/stream'),
                                        ('http://www.w3.org/ns/odrl/2/synchronize'),
                                        ('http://www.w3.org/ns/odrl/2/textToSpeech'),
                                        ('http://www.w3.org/ns/odrl/2/transform'),
                                        ('http://www.w3.org/ns/odrl/2/translate'),
                                        ('http://www.w3.org/ns/odrl/2/uninstall'),
                                        ('http://www.w3.org/ns/odrl/2/watermark');
''')
conn.commit()
conn.close()
