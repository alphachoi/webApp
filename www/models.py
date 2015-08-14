# -*-coding:utf-8 -*-
from uuid import uuid4

from www.orm import *


def uuid_hex():
    return uuid4().hex


class User(Model):
    __table__ = 'users'

    id = StringField(primary_key=True, default=uuid_hex, ddl='varchar(50)')
    password = StringField(ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')


class Blog(Model):
    __table__ = 'blog'

    id = StringField(primary_key=True, default=uuid_hex, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    content = TextField()
