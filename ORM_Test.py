from ORM import *
import logging


class Person(Model):
    id = Field("id", pk=True)
    name = Field("name")
    email = Field("email")
    password = Field("password")


logging.basicConfig(level=logging.DEBUG)

print Person.select(id=12345)
print Person.select_one(12345)
u = Person(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
u.insert()
print Person.select(id=12345)
print Person.select_one(12345)

u.password = "WhatTheFuck"
u.update()
print Person.select(password="WhatTheFuck")
print Person.select(password="my-pwd")
print Person.select_one(12345)

Person.delete(u)
print Person.select(id=12345)
print Person.select_one(12345)
print dir(Person)
