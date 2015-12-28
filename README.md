# EasyORM

The EasyORM Database Object Relationship Mapping Framework allows you manipulate objects without using SQL and manage transactions using decorator,

    class Person(Model):
        id = Field("id", pk=True)
        name = Field("name")
        email = Field("email")
        passwd = Field("passwd")
    
    @DB.transaction
    def test():
        Person.select(id=12345))
        Person.select_one(12345)
        u = Person(id=12345, name='Michael', email='test@orm.org', passwd='my-pwd')
        u.insert()
        u.passwd = "WhatTheFuck"
        u.update()
        Person.select(passwd="WhatTheFuck")
        Person.delete(u)
  
More Features are comming...