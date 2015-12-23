from DB import *
import logging
import unittest


class DBTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_transaction(self):
        pass

    def test_sqlite3(self):
        Core.init("test.db")
        ins = Core.instance()
        ins.execute("select 1 + 1 ")
        ins.execute("drop table if exists test")
        ins.execute("create table test (id int)")
        ins.execute("insert into test values (1)")
        ins.execute("select * from test")
        ins.execute("drop table if exists test")

    def test_mysql(self):
        pass

if __name__ == '__main__':
    unittest.main()
