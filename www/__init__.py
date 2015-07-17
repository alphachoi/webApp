# -*-coding:utf-8 -*-
import sqlite3

from jinja2 import Environment, PackageLoader

from www.wsgi import Application as application

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
    try:
        create_db()
    except sqlite3.OperationalError as e:
        print(e)
    from wsgiref.simple_server import make_server

    from www.wsgi import Application

    server = make_server('', 8080, application)
    print('Serving HTTP on port 8080...')
    server.serve_forever()
