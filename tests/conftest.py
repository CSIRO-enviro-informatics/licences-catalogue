import pytest
import _conf
import create_database
import sqlite3
from seed_database import get_db


@pytest.fixture(scope='session', autouse=True)
def setup_database():
    # We want to use test.db to avoid changing the real database
    _conf.DATABASE_PATH = _conf.APP_DIR + '/tests/test.db'
    create_database.teardown()
    create_database.rebuild()


@pytest.fixture(autouse=True)
def wipe_database():
    conn = get_db()
    conn.execute('DELETE FROM ASSIGNEE')
    conn.execute('DELETE FROM ASSIGNOR')
    conn.execute('DELETE FROM RULE_HAS_ACTION')
    conn.execute('DELETE FROM POLICY_HAS_RULE')
    conn.execute('DELETE FROM PARTY')
    conn.execute('DELETE FROM RULE')
    conn.execute('DELETE FROM ASSET')
    conn.execute('DELETE FROM POLICY')
    conn.commit()
