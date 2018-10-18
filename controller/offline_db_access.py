import os
import _conf
import sqlite3

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
