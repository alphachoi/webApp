# -*-coding:utf-8 -*-
import sqlite3


class Field:
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<{}, {}:{}>'.format(
            self.__class__.__name__, self.column_type, self.name)


class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None,
                 ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class Meta(type):
    def __new__(mcs, name, bases, attributes):
        if name == 'Model':
            return type.__new__(mcs, name, bases, attributes)

        table_name = attributes.get('__table__', name)
        mappings = dict()
        fields = []
        primary_key = None
        for k, v in attributes.items():
            if not isinstance(v, Field):
                continue
            mappings[k] = v
            if v.primary_key:
                assert primary_key is None, 'Found duplicate primary key.'
                primary_key = k
            fields.append(k)
        assert primary_key is not None, 'Primary key not found.'
        for k in mappings:
            del attributes[k]
        attributes['__mappings__'] = mappings
        attributes['__table__'] = table_name
        attributes['__primary_key__'] = primary_key
        attributes['__fields__'] = fields

        return type.__new__(mcs, name, bases, attributes)


cursor = None


def connect_db(func):
    def wrap(*args, **kwargs):
        global cursor
        conn = sqlite3.connect('web_app.db')
        if func.__name__ == 'get':
            conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        with conn:
            try:
                return func(*args, **kwargs)
            except sqlite3.IntegrityError as e:
                print(e)

    return wrap


class Model(metaclass=Meta):
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    @connect_db
    def insert(self):
        global cursor
        for k, v in self.__mappings__.items():
            default = v.default() if callable(v.default) else v.default
            v.name = getattr(self, k, default)
            self.__dict__[k] = v.name
        columns = self.__fields__
        values = [self.__dict__[k] for k in columns]
        sql = 'INSERT INTO {} ({}) VALUES (?,?,?,?)'.format(
            self.__table__, ','.join(columns))
        cursor.execute(sql, values)

    @connect_db
    def update(self, **kwargs):
        global cursor
        columns = (k + "='{}'".format(v) for k, v in kwargs.items())
        value = getattr(self, self.__primary_key__)
        sql = 'UPDATE {} SET {} WHERE {}=?'.format(
            self.__table__, ','.join(columns), self.__primary_key__
        )
        cursor.execute(sql, (value,))

    @classmethod
    @connect_db
    def get(cls, *value, **kwargs):
        if value:
            key = cls.__primary_key__
        else:
            key, value = kwargs.popitem()
            value = (value,)
        global cursor
        sql = 'SELECT * FROM {} WHERE {}=?'.format(cls.__table__, key)
        cursor.execute(sql, value)
        row = cursor.fetchone()
        return cls(**row) if row else None

    @classmethod
    @connect_db
    def delete(cls, key):
        global cursor
        sql = 'DELETE FROM {} WHERE {}=?'.format(
            cls.__table__, cls.__primary_key__
        )
        cursor.execute(sql, (key,))

    @classmethod
    @connect_db
    def get_all(cls, **kwargs):
        global cursor
        if kwargs:
            key, value = kwargs.popitem()
            sql = 'SELECT * FROM {} WHERE {}=?'.format(cls.__table__, key)
            cursor.execute(sql, (value,))
        else:
            sql = 'SELECT * FROM {}'.format(cls.__table__)
            cursor.execute(sql)
        return (cls.get(i[0]) for i in cursor.fetchall())


if __name__ == '__main__':
    pass
