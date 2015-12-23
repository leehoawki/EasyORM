from ORM import *


class Person(Model):
    id = Field()
    name = Field()
    email = Field()
    password = Field()


print Person.select(id=12345)

u = Person(id=12345, name='Michael', email='test@orm.org', password='my-pwd')
u.insert()
print Person.select(id=12345)

u.password = "wahaha"
u.update()
print Person.select(id=12345)

Person.delete(u)
print Person.select(id=12345)
print dir(Person)