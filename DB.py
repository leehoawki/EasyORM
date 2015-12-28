import sqlite3
import mysql.connector
import inspect
import time
import logging
import threading
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
        global core
        self.adhoc = False
        if core.connection is None:
            core.connection = get_connection()
            self.adhoc = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        conn = core.connection
        try:
            if exctype is None:
                conn.commit()
            else:
                conn.rollback()
        finally:
            if self.adhoc:
                core.connection = None
                conn.close()


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


class Connection(object):
    def __init__(self, conn):
        self.conn = conn

    def commit(self):
        return self.conn.commit()

    def rollback(self):
        return self.conn.rollback()

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        return self.conn.close()


def get_connection():
    global connector
    if connector is None:
        raise Exception("DB needs to get initialized first.")
    return Connection(connector())


def init(**kwargs):
    global connector
    if connector is not None:
        raise Exception("DB can only not initialized once.")
    database = kwargs.get("database")
    if database == "sqlite3":
        path = kwargs.get("path")
        connector = lambda: sqlite3.connect(path)
    elif database == "mysql":
        host = kwargs.get("host")
        port = kwargs.get("port")
        username = kwargs.get("username")
        password = kwargs.get("password")
        dbname = kwargs.get("dbname")
        connector = lambda: mysql.connector.connect(user=username, password=password, database=dbname, host=host,
                                                    port=port)
    else:
        raise Exception("Unsupported database Type : " + database + ".")


def destroy():
    global connector
    connector = None


@logger
def execute(sql, args=[], one=False):
    global core
    adhoc = False
    if core.connection is None:
        core.connection = get_connection()
        adhoc = True
    conn = core.connection
    c = conn.cursor()
    try:
        c.execute(sql, args)
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
        if adhoc:
            core.connection = None
            conn.close()


class Core(threading.local):
    def __init__(self):
        self.connection = None


connector = None
core = Core()
