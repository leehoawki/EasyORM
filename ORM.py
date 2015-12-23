class Field(object):
    def __init__(self, name, pk=False):
        self.name = name
        self.pk = pk

    def __str__(self):
        s = '<%s:%s:' % (self.__class__.__name__, self.name)
        if self.pk:
            s += 'Primary Key'
        s += '>'
        return s


class ORM(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return super(ORM, cls).__new__(cls, name, bases, attrs)

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
            name, ' and '.join('%s = ?' % x for x in fields if x != pk.name), pk.name, '?')
        attrs['__delete_sql__'] = 'delete from %s where %s = %s' % (name, pk.name, '?')
        attrs['__select_one_sql__'] = 'select %s from %s where %s = %s' % (",".join(fields), name, pk.name, '?')
        return super(ORM, cls).__new__(cls, name, bases, attrs)


class Model(dict):
    __metaclass__ = ORM

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)

    def __getattr__(self, key):
        if self.has_key(key):
            return self[key]
        else:
            return None

    def __setattr__(self, key, value):
        self[key] = value

    def insert(self):
        args = []
        for k, v in self.__mappings__.items():
            args.append(self.__getattr__(k))
        print self.__insert_sql__

    def update(self):
        print self.__update_sql__

    def delete(self):
        print self.__delete_sql__

    @classmethod
    def select(cls, **kwargs):
        sql = 'select %s from %s where %s' % (
            ",".join(cls.__fields__), cls.__table__, ' and '.join('%s = ?' % x for x in kwargs))
        print sql

    @classmethod
    def select_one(cls, val):
        print cls.__select_one_sql__
