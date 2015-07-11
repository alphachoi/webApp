# -*-coding:utf-8 -*-
from hashlib import md5
import os

from www.models import User, Blog
from www import env, signed_cookie


def render_for_response(request, html, dic=None, **kwargs):
    template = env.get_template(html)
    if dic:
        kwargs.update(dic)
    request.content = template.render(**kwargs)
    return request


def md5_hash(value, salt=''):
    return md5((value + salt).encode()).hexdigest()


def login(request):
    if request.method == 'GET':
        return render_for_response(request, 'log_in.html')
    dic = request.form
    user = User.get(name=dic.get('name'))
    password = md5_hash(dic.get('password', ''), salt=dic.get('name', ''))
    if user is None or user.password != password:
        error = 'UserName or Password Is Incorrect'
        return render_for_response(request, 'log_in.html', error=error)
    request.status = '303 See Other'
    request.header.append(('Location', '/hello'))
    dic['sign'] = md5_hash(user.id + user.password)
    del dic['password']
    signed_cookie[user.name] = dic['sign']
    request.set_cookie(dic)
    return request


def hello(request):
    try:
        name = request.cookie['name'].value
        sign = request.cookie['sign'].value
        assert name in signed_cookie and signed_cookie[name] == sign
        if request.path == '/hello':
            blog = Blog.get(name=name)
            if blog is None:
                return render_for_response(request, 'hello.html', name=name)
            request.status = '303 See Other'
            request.header.append(('Location', '/hello/' + blog.id))
            return request

        blog = Blog.get(id=request.path.replace('/hello/', ''))
        blogs = Blog.get_all(name=name)
        return render_for_response(request, 'hello.html',
                                   name=name, blog=blog, blogs=blogs)
    except (KeyError, AssertionError):
        request.status = '303 See Other'
        request.header.append(('Location', '/'))
        return request


def register(request):
    dic = request.form
    name = dic.get('name')
    user = User.get(name=name)
    password = dic.get('password')
    error = ''
    if request.method == 'GET':
        return render_for_response(request, 'register.html')
    elif user is not None:
        error = 'UserName Is Registered'
    elif not password or not name:
        error = 'User Name or Password Is empty'
    if error:
        return render_for_response(request, 'register.html', error=error)
    dic['password'] = md5_hash(password, salt=name)
    user = User(**dic)
    user.insert()
    request.status = '303 See Other'
    request.header.append(('Location', '/hello'))
    dic['sign'] = md5_hash(user.id + user.password)
    del dic['password']
    signed_cookie[user.name] = dic['sign']
    request.set_cookie(dic)
    return request


def do_with_static(request):
    path = os.path.join(os.getcwd(), request.path.lstrip('/'))
    mime = 'css' if path.endswith('.css') else 'javascript'
    request.header = [('Content-Type', 'text/' + mime)]
    with open(path) as f:
        request.content = f.read()
    return request


def add_blog(request):
    name = request.cookie['name'].value
    return render_for_response(request, 'add_blog.html', name=name)


def delete_blog(request):
    Blog.delete(request.referer[-32:])
    request.path = '/hello'
    return hello(request)


def update_blog(request):
    blog = Blog.get(id=request.referer[-32:])
    return render_for_response(request, 'update_blog.html', blog=blog)


def post_blog(request):
    dic = request.form
    if 'id' in dic:
        Blog.delete(dic['id'])
    dic['name'] = request.cookie['name'].value
    blog = Blog(**dic)
    blog.insert()
    request.status = '303 See Other'
    request.header.append(('Location', '/hello/' + blog.id))
    return request


urls = [(r'/', login), (r'/hello.*', hello), (r'/register', register),
        (r'/static/.+', do_with_static), (r'/add', add_blog),
        (r'/post', post_blog), (r'/delete', delete_blog),
        (r'/update', update_blog)]
