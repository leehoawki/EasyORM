from ORM import *
import DB
import logging
import unittest


class Person(Model):
    id = Field("id", pk=True)
    name = Field("name")
    email = Field("email")
    passwd = Field("passwd")


class ORMTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        DB.init(database='sqlite3', path='test.db')
        DB.execute('drop table if exists Person')
        DB.execute('create table Person (id int primary key, name text, email text, passwd text)')

    def tearDown(self):
        DB.execute('drop table if exists Person')
        DB.destroy()

    @DB.transaction
    def test_person(self):
        assert len(Person.select(id=12345)) == 0
        assert Person.select_one(12345) is None
        u = Person(id=12345, name='Michael', email='test@orm.org', passwd='my-pwd')
        u.insert()
        assert len(Person.select(id=12345)) == 1
        assert Person.select_one(12345) == u
        u.passwd = "WhatTheFuck"
        u.update()
        assert len(Person.select(passwd="WhatTheFuck")) == 1
        assert len(Person.select(passwd="my-pwd")) == 0
        assert Person.select_one(12345) == u

        Person.delete(u)
        assert len(Person.select(id=12345)) == 0
        assert len(Person.select()) == 0
        assert Person.select_one(12345) is None

    @DB.transaction
    def test_group_function(self):
        assert Person.count() == 0
        u1 = Person(id=0, name='Michael', email='test@orm.org', passwd='my-pwd')
        u1.insert()
        assert Person.count() == 1
        assert Person.count(id=1) == 0
        assert Person.count(id=0) == 1
        u2 = Person(id=1, name='Michael', email='test@orm.org', passwd='my-pwd')
        u2.insert()
        assert Person.count() == 2
        assert Person.count(id=1) == 1
        assert Person.count(id=0) == 1


if __name__ == '__main__':
    unittest.main()
