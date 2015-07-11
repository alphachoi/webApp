# -*-coding:utf-8 -*-
import re
from urllib.parse import parse_qs
from http.cookies import SimpleCookie

from www.views import urls


class NotFound(Exception):
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return '<h1>404! Not Found This Page:{}</h1>'.format(self.value)


class Request:
    def __init__(self, env):
        self.env = env
        self.status = '200 OK'
        self.header = [('Content-type', 'text/html')]
        self.path = self.env['PATH_INFO']
        self.content = ''
        self.file = None
        self.cookie = self.get_cookie()

    @property
    def method(self):
        return self.env['REQUEST_METHOD']

    @property
    def referer(self):
        try:
            return self.env['HTTP_REFERER']
        except ValueError:
            return self.path

    @property
    def form(self):
        try:
            size = int(self.env.get('CONTENT_LENGTH'))
        except ValueError:
            size = 0
        body = self.env['wsgi.input'].read(size)
        dic = parse_qs(body.decode('utf-8'))
        dic = {k: v[0] for k, v in dic.items() if v}
        return dic

    def get_cookie(self):
        try:
            return SimpleCookie(self.env['HTTP_COOKIE'])
        except KeyError:
            return SimpleCookie()

    def set_cookie(self, dic=None, **kwargs):
        if dic:
            self.cookie.load(dic)
        if kwargs:
            self.cookie.load(kwargs)
        out = self.cookie.output(header='', sep=' ')
        for i in out.split():
            self.header.append(('Set-Cookie', i))


class Application:
    def __init__(self, environ, start_response):
        self.environ = environ
        self.start = start_response

    def delegate(self):
        path = self.environ['PATH_INFO']
        for pattern, func in urls:
            pattern = '^{}$'.format(pattern)
            m = re.match(pattern, path)
            if m:
                return func(Request(self.environ))
        raise NotFound(path)

    def __iter__(self):
        try:
            response = self.delegate()
            assert isinstance(response, Request) is True, 'Invalid Response'
            self.start(response.status, response.header)
            if response.file:
                return response.file
            yield response.content.encode()
        except NotFound as e:
            yield self.not_found(str(e)).encode()
        except AssertionError as e:
            print(e)

    def not_found(self, message):
        status = '404 Not Found'
        self.start(status, [('Content-type', 'text/html')])
        return message


if __name__ == '__main__':
    pass
