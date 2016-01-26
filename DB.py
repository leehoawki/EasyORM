import sqlite3
import mysql.connector
import inspect
import time
import logging
import threading
import functools


class DBException(Exception):
    pass


def logger(fn):
    @functools.wraps(fn)
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
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        with _TransactionCtx():
            return fn(*args, **kwargs)

    return wrapper


class _TransactionCtx(object):
    def __enter__(self):
        global core
        self.temp = False
        if core.connection is None:
            core.connection = get_connection()
            self.temp = True
        return self

    def __exit__(self, exctype, excvalue, traceback):
        conn = core.connection
        try:
            if exctype is None:
                conn.commit()
            else:
                conn.rollback()
        finally:
            if self.temp:
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
            raise AttributeError("Dict object has no attribute %s" % key)

    def __setattr__(self, key, value):
        self[key] = value


class Connection(object):
    def __init__(self, conn):
        self.conn = conn

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def cursor(self):
        return self.conn.cursor()

    def close(self):
        global pool
        pool.recycle(self.conn)


def get_connection():
    global pool
    if pool is None:
        raise DBException("DB needs to get initialized first.")
    return pool.get_connection()


def init(**kwargs):
    global pool
    if pool is not None:
        raise DBException("DB can only not initialized once.")
    database = kwargs.get("database")
    if database == "sqlite3":
        path = kwargs.get("path")
        pool = Pool(lambda: Connection(sqlite3.connect(path)))
    elif database == "mysql":
        host = kwargs.get("host")
        port = kwargs.get("port")
        username = kwargs.get("username")
        password = kwargs.get("password")
        dbname = kwargs.get("dbname")
        pool = Pool(lambda: Connection(
                mysql.connector.connect(user=username, password=password, database=dbname, host=host, port=port)))
    else:
        raise DBException("Unsupported database Type : " + database + ".")


def destroy():
    global pool
    pool.destroy()
    pool = None


@logger
def _execute(sql, one, *args):
    global core
    temp = False
    if core.connection is None:
        core.connection = get_connection()
        temp = True
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
        if temp:
            core.connection = None
            conn.close()


def execute(sql, *args):
    return _execute(sql, False, *args)


def execute_query_one(sql, *args):
    return _execute(sql, True, *args)


class Core(threading.local):
    def __init__(self):
        super(Core, self).__init__()
        self.connection = None


class Pool(object):
    def __init__(self, connector, number=3):
        self.queue = []
        self.lock = threading.Lock()
        self.connector = connector
        self.number = number
        for i in range(0, number):
            self.queue.append(self.connector())

    def destroy(self):
        for c in self.queue:
            c.close()

    def get_connection(self):
        with self.lock:
            if self.queue:
                conn = self.queue.pop()
            else:
                conn = self.connector()
            return conn

    def recycle(self, conn):
        with self.lock:
            if len(self.queue) > self.number:
                conn.close()
            else:
                self.queue.append(conn)


core = Core()
pool = None
