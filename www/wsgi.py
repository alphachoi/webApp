# -*-coding:utf-8 -*-
import re
from urllib.parse import parse_qs
from http.cookies import SimpleCookie

from jinja2 import Environment, PackageLoader

jinja_env = Environment(loader=PackageLoader('www', 'templates'))


class Request:
    def __call__(self, env):
        self.env = env
        self.status = '200 OK'
        self.header = [('Content-type', 'text/html')]
        self.content = ''
        self.file = None
        self._form = None

    @property
    def method(self):
        return self.env['REQUEST_METHOD']

    @property
    def path(self):
        return self.env['PATH_INFO']

    @property
    def referer(self):
        return self.env.get('HTTP_REFERER')

    @property
    def form(self):
        if self._form:
            return self._form
        try:
            size = int(self.env.get('CONTENT_LENGTH'))
        except ValueError:
            size = 0
        body = self.env['wsgi.input'].read(size)
        dic = parse_qs(body.decode())
        dic = {k: v[0] for k, v in dic.items() if v}
        self._form = dic
        return dic

    def _cookie(self):
        try:
            return SimpleCookie(self.env['HTTP_COOKIE'])
        except KeyError:
            return SimpleCookie()

    @property
    def cookie(self):
        return {k: v.value for k, v in self._cookie().items() if v.value}

    def set_cookie(self, dic=None, **kwargs):
        cookie = self._cookie()
        if dic:
            cookie.load(dic)
        if kwargs:
            cookie.load(kwargs)
        out = cookie.output(header='', sep=' ')
        for i in out.split():
            self.header.append(('Set-Cookie', i))


class NotFound(Exception):
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return '<h1>404! Not Found This Page:{}</h1>'.format(self.value)


request = Request()


def render(html, dic=None, **kwargs):
    template = jinja_env.get_template(html)
    dic and kwargs.update(dic)
    request.content = template.render(**kwargs)
    return request


def redirect(path):
    request.status = '303 See Other'
    request.header.append(('Location', path))
    return request


class Application:
    def __init__(self):
        self.urls = dict()
        self.signed_cookie = dict()

    def __call__(self, environ, start_response):
        request(environ)
        try:
            response = self.delegate()
            assert isinstance(response, Request) is True, 'Invalid Response'
            start_response(response.status, response.header)
            if response.file:
                yield response.file
                return
            yield response.content.encode()
        except NotFound as e:
            start_response('404 Not Found', [('Content-type', 'text/plain')])
            yield (str(e)).encode()
        except AssertionError as e:
            print(e)

    def delegate(self):
        for pattern, func in self.urls.items():
            m = re.match(pattern, request.path)
            if m:
                groups = m.groups()
                if groups:
                    return func(*groups)
                return func()
        raise NotFound(request.path)

    def route(self, pattern):
        pattern = '^{}$'.format(pattern)

        def decorator(func):
            self.urls[pattern] = func
            return func

        return decorator
