import DB
import logging
import unittest


class DBTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)

    def test_transaction(self):
        DB.init(database="sqlite3", path="test.db")
        DB.execute("drop table if exists test")
        DB.execute("create table test (id int)")

        @DB.transaction
        def test_commit():
            DB.execute("insert into test values (1)")

        @DB.transaction
        def test_rollback():
            DB.execute("insert into test values (2)")
            raise Exception("Transaction Rollback")

        test_commit()
        ex = False
        try:
            test_rollback()
        except:
            ex = True
        assert ex == True
        assert len(DB.execute("select * from test where id = 1")) == 1
        assert len(DB.execute("select * from test where id = 2")) == 0

        DB.execute("drop table if exists test")
        DB.destroy()

    def test_sqlite3(self):
        DB.init(database="sqlite3", path="test.db")
        DB.execute("select 1 + 1 ")
        DB.execute("drop table if exists test")
        DB.execute("create table test (id int)")
        DB.execute("select * from test")
        DB.execute("drop table if exists test")
        DB.destroy()

    def test_mysql(self):
        DB.init(database="mysql", host="192.168.1.115", username="root", password="toor", dbname='test', port=3306)
        DB.execute("select 1 + 1 ")
        DB.execute("drop table if exists test")
        DB.execute("create table test (id int)")
        DB.execute("select * from test")
        DB.execute("drop table if exists test")
        DB.destroy()

    def test_pool(self):
        DB.init(database="mysql", host="192.168.1.115", username="root", password="toor", dbname='test', port=3306)
        assert len(DB.pool.queue) == 3
        conn = DB.get_connection()
        assert len(DB.pool.queue) == 2
        conn.close()
        assert len(DB.pool.queue) == 3


if __name__ == '__main__':
    unittest.main()
