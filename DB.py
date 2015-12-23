import sqlite3
import mysql.connector


class DB(object):
    def __init__(self, **kwargs):
        database = kwargs["database"]
        if database == "sqlite3":
            path = kwargs["path"]
            conn = sqlite3.connect(path)
        elif database == "mysql":
            user = kwargs.get("user")
            password = kwargs.get("password")
            host = kwargs.get("127.0.0.1")
            port = kwargs.get(3306)
            conn = mysql.connector.connect(user=user, password=password, host=host, port=port, autocommit=False)
        else:
            raise Exception("Illegal Database Type:" + database)

    def close(self):
        self.conn.close()

    def commit(self):
        self.conn.commit()
