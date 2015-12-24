from DB import *
import logging
import unittest


class DBTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_transaction(self):
        Core.init(database="sqlite3", path="test.db")
        ins = Core.instance()
        ins.execute("drop table if exists test")
        ins.execute("create table test (id int)")

        @transaction
        def test_commit(ins):
            ins.execute("insert into test values (1)")

        @transaction
        def test_rollback(ins):
            ins.execute("insert into test values (2)")
            raise Exception("Transaction Rollback")

        test_commit(ins)
        ex = False
        try:
            test_rollback(ins)
        except:
            ex = True
        assert ex == True
        assert len(ins.execute("select * from test where id = 1", query=True)) == 1
        assert len(ins.execute("select * from test where id = 2", query=True)) == 0

        ins.execute("drop table if exists test")
        ins.close()
        Core.destroy()

    def test_sqlite3(self):
        Core.init(database="sqlite3", path="test.db")
        ins = Core.instance()
        ins.execute("select 1 + 1 ")
        ins.execute("drop table if exists test")
        ins.execute("create table test (id int)")
        ins.execute("insert into test values (1)")
        ins.execute("select * from test")
        ins.execute("drop table if exists test")
        Core.destroy()

    def test_mysql(self):
        Core.init(database="mysql", host="127.0.0.1", username="test", password="test", port=3306)
        ins = Core.instance()
        ins.execute("select 1 + 1 ")
        ins.execute("drop table if exists test")
        ins.execute("create table test (id int)")
        ins.execute("insert into test values (1)")
        ins.execute("select * from test")
        ins.execute("drop table if exists test")
        Core.destroy()


if __name__ == '__main__':
    unittest.main()
