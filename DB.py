from Decorator import *
import sqlite3


class Dict(dict):
    def __init__(self, names=(), values=(), **kw):
        super(Dict, self).__init__(**kw)
        for k, v in zip(names, values):
            self[k] = v

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("Dict object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value


class Core(object):
    def __init__(self, conn):
        self.conn = conn

    @classmethod
    def instance(cls):
        if not hasattr(Core, "_instance"):
            raise Exception("DB needs to get initialized first.")
        return cls._instance

    @classmethod
    def init(cls, path):
        if hasattr(Core, "_instance"):
            raise Exception("DB can only not initialized once.")
        cls._instance = Core(sqlite3.connect(path))

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    @logger
    def execute(self, sql, args=[]):
        try:
            c = self.conn.cursor()
            c.execute(sql, args)
        finally:
            c.close()

    @logger
    def execute_query(self, sql, args=[]):
        try:
            c = self.conn.cursor()
            c.execute(sql, args)
            if c.description:
                names = [x[0] for x in c.description]
                return [Dict(names, x) for x in c.fetchall()]
        finally:
            c.close()

    @logger
    def execute_query_one(self, sql, args=[]):
        try:
            c = self.conn.cursor()
            c.execute(sql, args)
            if c.description:
                names = [x[0] for x in c.description]
            values = c.fetchone()
            if not values:
                return None
            return Dict(names, values)
        finally:
            c.close()
