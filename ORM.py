import DB


class Field(object):
    def __init__(self, name, **kwargs):
        if not name:
            raise Exception("Empty field name is not allowed.")
        self.name = name
        self.pk = kwargs.get("pk", False)

    def __str__(self):
        s = '<%s:%s' % (self.__class__.__name__, self.name)
        if self.pk:
            s += ':Primary Key'
        s += '>'
        return s


class StringField(Field):
    def __init__(self, name, **kwargs):
        self.default = ""
        super(StringField, self).__init__(name, **kwargs)


class NumberField(Field):
    def __init__(self, name, **kwargs):
        self.default = 0
        super(NumberField, self).__init__(name, **kwargs)


class Meta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return super(Meta, cls).__new__(cls, name, bases, attrs)

        mappings = {}
        fields = []
        pk = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                if v.pk:
                    if pk:
                        raise Exception('You can not define more than 1 primary key in Class: %s' % name)
                    else:
                        pk = v
                mappings[v.name] = v
                attrs.pop(k)
        if not pk:
            raise Exception('You need to define 1 primary key in Class: %s' % name)
        for k, v in mappings.items():
            fields.append(k)
        attrs['__mappings__'] = mappings
        attrs['__table__'] = name
        attrs['__fields__'] = fields
        attrs['__pk__'] = pk
        attrs['__insert_sql__'] = 'insert into %s (%s) values (%s)' % (
            name, ','.join(fields), ','.join(['?'] * len(fields)))
        attrs['__update_sql__'] = 'update %s set %s  where %s = %s' % (
            name, ','.join('%s = ?' % x for x in fields if x != pk.name), pk.name, '?')
        attrs['__delete_sql__'] = 'delete from %s where %s = %s' % (name, pk.name, '?')
        attrs['__select_one_sql__'] = 'select %s from %s where %s = %s' % (",".join(fields), name, pk.name, '?')
        return super(Meta, cls).__new__(cls, name, bases, attrs)


class Model(dict):
    __metaclass__ = Meta

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise Exception("This attribute %s is not found " % key)

    def __setattr__(self, key, value):
        self[key] = value

    def attributes(self):
        args = []
        for k, v in self.__mappings__.items():
            if hasattr(self, k):
                arg = getattr(self, k)
            else:
                arg = v.default
            args.append(arg)
        return args

    def insert(self):
        DB.execute(self.__insert_sql__, self.attributes())

    def update(self):
        DB.execute(self.__update_sql__, self.attributes())

    def delete(self):
        DB.execute(self.__delete_sql__, [self.get(self.__pk__.name)])

    @classmethod
    def select(cls, **kwargs):
        if kwargs:
            sql = 'select %s from %s where %s' % (
                ",".join(cls.__fields__), cls.__table__, ' and '.join("%s = ?" % x for x, y in kwargs.items()))
            args = [y for x, y in kwargs.items()]
            rs = DB.execute(sql, args)
        else:
            sql = 'select %s from %s' % (",".join(cls.__fields__), cls.__table__)
            rs = DB.execute(sql)
        return [cls(**d) for d in rs]

    @classmethod
    def count(cls, **kwargs):
        if kwargs:
            sql = 'select count(1) from %s where %s' % (
                cls.__table__, ' and '.join("%s = ?" % x for x, y in kwargs.items()))
            args = [y for x, y in kwargs.items()]
            rs = DB.execute_query_one(sql, args)
        else:
            sql = 'select count(1) from %s' % cls.__table__
            rs = DB.execute_query_one(sql)
        return rs.values()[0]

    @classmethod
    def select_one(cls, val):
        r = DB.execute_query_one(cls.__select_one_sql__, [val])
        return cls(**r) if r else None
