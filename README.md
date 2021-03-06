# EasyORM

The EasyORM Database Object Relationship Mapping Framework allows you to manipulate objects without SQL and manage transactions using decorator,

    class Person(Model):
        id = NumberField("id", pk=True)
        name = StringField("name")
        email = StringField("email")
        passwd = StringField("passwd")
    
    DB.init(database="mysql", host="127.0.0.1", username="root", password="toor", dbname='test', port=3306) 
    # Pool is created when initialized. sqlite3 is also supported
    
    @DB.transaction
    def test():
        Person.select("id=12345")
        Person.select("id=?",12345)
        Person.select_one(12345)
        u = Person(id=12345, name='Mr.Test', email='test@test.org', passwd='test_password')
        u.insert()
        u.passwd = "new_password2"
        u.update()
        Person.select("passwd like '%password'")
        Person.delete(u)
  
    DB.destroy()
    # Pool destroyed

Groups functions are also supported,

    Person.count("name like 'Mr%'")
    Person.count("id=12345")
    Person.count("id>10000 and id<20000")

More Features are comming...
