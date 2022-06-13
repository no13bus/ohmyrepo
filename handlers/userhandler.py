# coding: utf-8
import cairosvg
import os
import tornado
import tornado.web
import tornado.auth
from tornado import gen
from settings import githubapi
from .base import BaseHandler


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.set_secure_cookie('username', '')
        self.set_secure_cookie('token', '')
        self.set_secure_cookie('avatar_url', '')
        self.clear_cookie('username')
        self.clear_cookie('token')
        self.clear_cookie('avatar_url')
        self.redirect('/login')


class LoginHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        if self.get_secure_cookie('username'):
            self.redirect('/')
        oauth_url = githubapi['OAUTH_URL']
        self.render('login.html', oauth_url=oauth_url)

class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self):
        username = self.get_secure_cookie('username')
        home_pipe = [
            {'$match':{'$or':[{'username':username},{'add_username':username}]}},
            # {'$match': {'username': username}},
            {'$group': {
                '_id': {'username': '$username', 'reponame': '$reponame', 'add_username':'$add_username'}
            }}
        ]
        events_cursor = yield self.db.event.aggregate(home_pipe, cursor={})
        repos = []
        if events_cursor:
            while (yield events_cursor.fetch_next):
                doc = events_cursor.next_object()
                repo_show_url = '/show?u=%s&r=%s' % (doc['_id']['username'], doc['_id']['reponame'])
                repos.append({'reponame': doc['_id']['reponame'], 'url': repo_show_url})
        if not repos:
            self.error_msg = 'You do not record any repo.Please add one.'
        self.render('home.html', repos=repos, avatar_url=self.get_secure_cookie('avatar_url'))

class HowHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        avatar_url = self.get_secure_cookie('avatar_url', None)
        self.render('howitworks.html', avatar_url=avatar_url)

class ExportHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        filename = self.get_argument('filename', None)
        # s_type = self.get_argument('type', None)
        # width = self.get_argument('width', None)
        # scale = self.get_argument('scale', None)
        svg = self.get_argument('svg', None)
        # print filename, s_type, width, scale, svg
        parent_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")), 'static')

        if filename and svg:
            img_path = '%s/chart/%s.png' % (parent_path, filename)
            url_path = '/static/chart/%s.png' % filename
            print('img_path=%s' % img_path)
            try:
                cairosvg.svg2png(svg, write_to=img_path)
                self.write({'status': 1, 'url': url_path})
                return
            except Exception as ex:
                print('error of svg2png is %s' % ex.message)
        self.write({'status': 0})


