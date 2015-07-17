# -*-coding:utf-8 -*-
import os
import sys

path = '/root/webApp'
if path not in sys.path:
    sys.path.append(path)

try:
    os.mkdir(os.path.join(path, 'file'))
except FileExistsError:
    pass

try:
    from www import create_db

    create_db()
except sqlite3.OperationalError as e:
    pass

from www.wsgi import Application as application

if __name__ == '__main__':
    import sqlite3
    from www import create_db

    try:
        create_db()
    except sqlite3.OperationalError as e:
        print(e)
    from wsgiref.simple_server import make_server

    server = make_server('', 8080, application)
    print('Serving HTTP on port 8080...')
    server.serve_forever()
