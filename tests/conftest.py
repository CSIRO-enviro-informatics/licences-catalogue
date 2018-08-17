import pytest
import _conf
import create_database
import sqlite3
from controller import db_access


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    # We want to use test.db to avoid changing the real database
    # Close the current connection, switch the db path, rebuild the db and make a new connection
    _conf.DATABASE_PATH = _conf.APP_DIR + '/tests/test.db'
    db_access.conn.close()
    create_database.teardown()
    create_database.rebuild()
    db_access.conn = sqlite3.connect(_conf.DATABASE_PATH)
    db_access.conn.execute('PRAGMA foreign_keys = 1')
    db_access.conn.row_factory = sqlite3.Row
    db_access.cursor = db_access.conn.cursor()


@pytest.fixture(autouse=True)
def wipe_database():
    db_access.conn.execute('DELETE FROM RULE_HAS_ASSIGNEE')
    db_access.conn.execute('DELETE FROM RULE_HAS_ASSIGNOR')
    db_access.conn.execute('DELETE FROM PARTY')
    db_access.conn.execute('DELETE FROM RULE_HAS_ACTION')
    db_access.conn.execute('DELETE FROM POLICY_HAS_RULE')
    db_access.conn.execute('DELETE FROM RULE')
    db_access.conn.execute('DELETE FROM ASSET')
    db_access.conn.execute('DELETE FROM POLICY')
    db_access.conn.commit()
