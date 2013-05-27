#-*- coding:utf-8 -*-

import sqlite3
import logging

log = logging.getLogger('Main.db')

class Database(object):
    """define database operations"""
    def __init__(self, db_file):
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread = False, isolation_level = None)     # consider auto-commit's overhead
            self.conn.execute('''CREATE TABLE IF NOT EXISTS wpdb(
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                url TEXT,
                                time TEXT,
                                domain TEXT,
                                html TEXT
                                )''')
        except Exception, e:
            print("Connect database failed : %s" % str(e))
            log.critical("Connect database failed : %s" % str(e))
            self.conn = None

    def save_data(self, data):
        try:
            sql = '''INSERT INTO wpdb (url, time, domain, html) VALUES (?, ?, ?, ?);'''
            self.conn.execute(sql, data)
        except Exception, e:
            print("database save failed: %s" % str(e))
            log.critical("database save failed: %s" % str(e))

    def close(self):
        if self.conn:
            self.conn.close()
        else:
            log.warning("database close failed, check connection.\n")

