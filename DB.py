import sqlite3
import mysql.connector
import inspect
import time
import logging
from functools import wraps


def logger(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        logging.debug("function   = " + fn.__name__)
        logging.debug("    arguments = {0} {1}".format(args, kwargs))
        ts = time.time()
        result = fn(*args, **kwargs)
        te = time.time()
        logging.debug("    return    = {0}".format(result))
        logging.debug("    time      = %.6f sec" % (te - ts))
        logging.debug("    called_from_line : " + str(inspect.currentframe().f_back.f_lineno))
        return result

    return wrapper


def transaction(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        with _TransactionCtx():
            return fn(*args, **kwargs)
        return result

    return wrapper


class _TransactionCtx(object):
    def __enter__(self):
        return self

    def __exit__(self, exctype, excvalue, traceback):
        ins = Core.instance()
        if exctype is None:
            ins.commit()
        else:
            ins.rollback()


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
    def init(cls, **kwargs):
        if hasattr(Core, "_instance"):
            raise Exception("DB can only not initialized once.")
        database = kwargs.get("database")
        if database == "sqlite3":
            path = kwargs.get("path")
            cls._instance = Core(sqlite3.connect(path))
        elif database == "mysql":
            host = kwargs.get("host")
            port = kwargs.get("port")
            username = kwargs.get("username")
            password = kwargs.get("password")
            dbname = kwargs.get("dbname")
            cls._instance = Core(
                mysql.connector.connect(user=username, password=password, database=dbname, host=host, port=port))
        else:
            raise Exception("Unsupported database Type : " + database + ".")

    @classmethod
    def destroy(cls):
        cls._instance.close()
        delattr(cls, "_instance")

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    @logger
    def execute(self, sql, args=[], one=False, query=False):
        try:
            c = self.conn.cursor()
            c.execute(sql, args)
            if not query:
                return
            if c.description:
                names = [x[0] for x in c.description]
                if one:
                    values = c.fetchone()
                    if not values:
                        return None
                    return Dict(names, values)
                return [Dict(names, x) for x in c.fetchall()]
        finally:
            c.close()
