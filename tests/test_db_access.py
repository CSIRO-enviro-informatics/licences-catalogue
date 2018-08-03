import pytest
import _conf
import create_database
import sqlite3
from controller import db_access


def setup_module():
    # We want to use test.db to avoid changing the real database
    # Close the current connection, switch the db path, rebuild the db and make a new connection
    _conf.DATABASE_PATH = _conf.APP_DIR + '/tests/test.db'
    db_access.conn.close()
    create_database.teardown()
    create_database.rebuild()
    db_access.conn = sqlite3.connect(_conf.DATABASE_PATH)
    db_access.conn.execute('PRAGMA foreign_keys = 1')
    db_access.cursor = db_access.conn.cursor()


def teardown_function():
    db_access.conn.execute('DELETE FROM RULE_HAS_ASSIGNEE;')
    db_access.conn.execute('DELETE FROM RULE_HAS_ASSIGNOR;')
    db_access.conn.execute('DELETE FROM PARTY;')
    db_access.conn.execute('DELETE FROM RULE_HAS_ACTION;')
    db_access.conn.execute('DELETE FROM POLICY_HAS_RULE;')
    db_access.conn.execute('DELETE FROM RULE;')
    db_access.conn.execute('DELETE FROM ASSET;')
    db_access.conn.execute('DELETE FROM POLICY;')
    db_access.conn.commit()


def test_uri_is_valid():
    assert db_access.is_valid_uri('not a uri') is False
    assert db_access.is_valid_uri('https://example.com#test') is True


def test_create_policy():
    # Should raise an exception when given an invalid uri
    with pytest.raises(ValueError):
        db_access.create_policy('not a uri')

    # Should store a new policy entry in the database and assign an ID
    new_policy_uri = 'https://example.com#test'
    new_policy_id = db_access.create_policy(new_policy_uri)
    assert new_policy_id == 1
    db_access.cursor.execute('SELECT URI FROM POLICY WHERE ID = {id}'.format(id=new_policy_id))
    stored_uri = db_access.cursor.fetchone()[0]
    assert stored_uri == new_policy_uri

    # Should reject duplicate policies
    with pytest.raises(ValueError):
        db_access.create_policy(new_policy_uri)


def test_set_policy_type():
    uri = 'https://example.com#test'
    new_policy_type = 'http://creativecommons.org/ns#License'
    db_access.create_policy(uri)
    db_access.set_policy_type(uri, new_policy_type)
    db_access.cursor.execute('SELECT TYPE FROM POLICY WHERE URI = "{uri}";'.format(uri=uri))
    stored_policy_type = db_access.cursor.fetchone()[0]
    assert stored_policy_type == new_policy_type
