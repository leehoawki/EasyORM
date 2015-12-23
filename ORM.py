class Field(object):
    pass


class ORM(type):
    def __new__(cls, name, bases, attrs):
        mappings = {}
        fields = []
        params = []
        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v

        for k, v in mappings.items():
            fields.append(k)
            params.append('?')
            attrs.pop(k)

        attrs['__mappings__'] = mappings
        attrs['__table__'] = name
        attrs['__insert_sql__'] = 'insert into %s (%s) values (%s)' % (name, ','.join(fields), ','.join(params))
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
        print args

    def update(self):
        pass

    def delete(self):
        pass

    @classmethod
    def select(cls, **kwargs):
        pass
