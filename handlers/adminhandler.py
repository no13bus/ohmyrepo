# coding: utf-8
import tornado
from tornado import gen
from .base import BaseHandler


class StatHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        # username = self.get_secure_cookie('username')
        # if username == 'no13bus':
        users_cursor = self.db.user.find(None, {'username':1, 'avatar_url':1, '_id':0})
        users = []
        if users_cursor:
            while (yield users_cursor.fetch_next):
                doc = users_cursor.next_object()
                users.append({'username': doc['username'], 'avatar_url': doc['avatar_url']})
        if not users:
            self.error_msg = 'no users.'
        repos = yield self.db.event.distinct('reponame')
        self.render('stat.html', users=len(users), repos=len(repos), avatar_url=self.get_secure_cookie('avatar_url'))
        # else:
        #     self.redirect('/')

class StatUserHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        users_cursor = self.db.user.find(None, {'username':1, 'avatar_url':1, '_id':0})
        users = []
        if users_cursor:
            while (yield users_cursor.fetch_next):
                doc = users_cursor.next_object()
                users.append({'username': doc['username'], 'avatar_url': doc['avatar_url']})
        if not users:
            self.error_msg = 'no users.'
        self.render('stat_user.html', users=users, avatar_url=self.get_secure_cookie('avatar_url'))


class StatRepoHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        repos = []
        star_pipe = [
                    {'$group': {
                        '_id': {'username': '$username', 'reponame': '$reponame'}
                    }}
                ]
        cursor = yield self.db.event.aggregate(star_pipe, cursor={})
        if cursor:
            while (yield cursor.fetch_next):
                doc = cursor.next_object()
                one_user = yield self.db.user.find_one({'username':doc['_id']['username']})
                doc['_id']['avatar_url'] = one_user['avatar_url']
                repos.append(doc['_id'])
            if not repos:
                self.error_msg = 'no repos.'
        self.render('stat_repo.html', repos=repos, avatar_url=self.get_secure_cookie('avatar_url'))