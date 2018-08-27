import sqlite3
import _conf
from unittest import mock
from controller import db_access

db = None


def get_db():
    global db
    if db:
        return db
    else:
        db = sqlite3.connect(_conf.DATABASE_PATH)
        db.execute('PRAGMA foreign_keys = 1')
        db.row_factory = sqlite3.Row
        return db


@mock.patch('controller.db_access.get_db', side_effect=get_db)
def seed(mock):
    # Mocks out get_db() so this can be run independently of the Flask application
    action = 'http://www.w3.org/ns/odrl/2/acceptTracking'
    rule_type = 'http://www.w3.org/ns/odrl/2/permission'
    rule1 = _conf.BASE_URI + 'rule/1'
    rule2 = _conf.BASE_URI + 'rule/2'
    rule3 = _conf.BASE_URI + 'rule/3'
    db_access.create_rule(rule1, rule_type, 'Rule1')
    db_access.create_rule(rule2, rule_type, 'Rule2')
    db_access.create_rule(rule3, rule_type, 'Rule3')
    db_access.add_action_to_rule(action, rule1)
    db_access.add_action_to_rule(action, rule2)
    db_access.add_action_to_rule(action, rule3)
    assignor_uri = _conf.BASE_URI + 'assignor/1'
    assignee_uri = _conf.BASE_URI + 'assignee/1'
    db_access.add_assignor_to_rule(assignor_uri, rule1)
    db_access.add_assignee_to_rule(assignee_uri, rule1)


if __name__ == '__main__':
    seed()
