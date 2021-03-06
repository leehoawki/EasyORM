from ORM import *
import DB
import logging
import unittest


class Person(Model):
    id = NumberField("id", pk=True)
    name = StringField("name")
    email = StringField("email")
    passwd = StringField("passwd")
    online = BooleanField("online")


class ORMTest(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        DB.init(database='sqlite3', path='test.db')
        DB.execute('drop table if exists Person')
        DB.execute('create table Person (id int primary key, name text, email text, passwd text,online bool)')

    def tearDown(self):
        DB.execute('drop table if exists Person')
        DB.destroy()

    @DB.transaction
    def test_person(self):
        assert len(Person.select("id=12345")) == 0
        assert Person.select_one(12345) is None
        u = Person(id=12345, name='Michael', email='test@orm.org', passwd='my-pwd', online=True)
        u.insert()
        assert len(Person.select("id=?", 12345)) == 1
        assert Person.select_one(12345) == u
        u.passwd = "WhatTheFuck"
        u.update()
        assert len(Person.select("passwd=?", "WhatTheFuck")) == 1
        assert len(Person.select("passwd=?", "my-pwd")) == 0
        assert Person.select_one(12345) == u

        Person.delete(u)
        assert len(Person.select("id=12345")) == 0
        assert len(Person.select()) == 0
        assert Person.select_one(12345) is None

    @DB.transaction
    def test_group_function(self):
        assert Person.count() == 0
        u1 = Person(id=0, name='Michael', email='test@orm.org', passwd='my-pwd', online=True)
        u1.insert()
        assert Person.count() == 1
        assert Person.count("id=1") == 0
        assert Person.count("id=0") == 1
        u2 = Person(id=1, name='Tom', email='test@orm.org', passwd='my-pwd', online=True)
        u2.insert()
        assert Person.count() == 2
        assert Person.count("id=1") == 1
        assert Person.count("id=0") == 1
        assert Person.count("id>0") == 1
        assert Person.count("id>=0") == 2
        assert Person.count("id>=0 and id<2") == 2
        assert Person.count("id>=0 and id<1") == 1
        assert Person.count("name like 'Mic%'") == 1
        assert Person.count("name like 'Tom'") == 1
        assert Person.count("name = 'Tom'") == 1

    @DB.transaction
    def test_default_value(self):
        u = Person(email='test@orm.org', passwd='my-pwd')
        u.insert()
        v = Person.select_one(0)
        assert v.id == 0
        assert v.name == ""
        assert not v.online
        v.online = True
        v.update()
        w = Person.select_one(0)
        assert w.online


if __name__ == '__main__':
    unittest.main()
