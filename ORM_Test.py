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
        DB.Core.init('test')
        DB.Core.instance().execute('drop table if exists Person')
        DB.Core.instance().execute('create table Person (id int primary key, name text, email text, passwd text)')

    def tearDown(self):
        DB.Core.instance().execute('drop table if exists Person')
        DB.Core.instance().close()

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
        assert Person.select_one(12345) is None


if __name__ == '__main__':
    unittest.main()
