import DB


class Field(object):
    def __init__(self, name, pk=False):
        self.name = name
        self.pk = pk

    def __str__(self):
        s = '<%s:%s' % (self.__class__.__name__, self.name)
        if self.pk:
            s += ':Primary Key'
        s += '>'
        return s


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
        if self.has_key(key):
            return self[key]
        else:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def attributes(self):
        args = []
        for k, v in self.__mappings__.items():
            args.append(self.__getattr__(k))
        return args

    def insert(self):
        DB.Core.instance().execute(self.__insert_sql__, self.attributes())

    def update(self):
        import logging

        logging.warn(self.__update_sql__)
        logging.warn(self.attributes())
        DB.Core.instance().execute(self.__update_sql__, self.attributes())

    def delete(self):
        DB.Core.instance().execute(self.__delete_sql__, [self.get(self.__pk__.name)])

    @classmethod
    def select(cls, **kwargs):
        sql = 'select %s from %s where %s' % (
            ",".join(cls.__fields__), cls.__table__, ' and '.join("%s = '%s'" % (x, y) for x, y in kwargs.items()))
        rs = DB.Core.instance().execute(sql)
        return [cls(**d) for d in rs]

    @classmethod
    def select_one(cls, val):
        r = DB.Core.instance().execute(cls.__select_one_sql__, [val], one=True)
        return cls(**r) if r else None
