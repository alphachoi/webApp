# -*-coding:utf-8 -*-
import sqlite3

from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('www', 'templates'))
signed_cookie = dict()


def create_db():
    conn = sqlite3.connect('web_app.db')
    c = conn.cursor()
    c.execute('''create table users (
    id char(50) primary key not null,
    password char(50) not null,
    admin bool not null,
    name char(50) unique not null)''')
    c.execute('''create table blog (
    id char(50) primary key not null,
    name char(50) not null,
    title char(50) not null,
    content text not null)''')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    pass
