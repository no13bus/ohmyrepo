# coding: utf-8
import tornado
import tornado.web
import tornado.auth
from tornado import gen
from libs.github import follow, unfollow, followed_bool
from .base import BaseHandler
from cache import cache
from cache import CacheMixin

class UserStarHandler(CacheMixin, BaseHandler):
    @cache(60*5)
    @gen.coroutine
    def get(self):
        username = self.get_argument('u')
        reponame = self.get_argument('r')
        res = []
        if username and reponame:
            # user = yield self.db.user.find_one({'username': username})
            # if user:
            star_pipe = [
                {'$match': {'username': username, 'reponame': reponame}},
                {'$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$time'}},
                    'num': {'$sum': 1}
                }},
                {'$sort': {'_id': 1}}
            ]
            cursor = yield self.db.event.aggregate(star_pipe, cursor={})
            if cursor:
                while (yield cursor.fetch_next):
                    doc = cursor.next_object()
                    res.append(doc)
                if res:
                    self.write({'status': 1, 'result': res})
                    return
        self.write({'status': 0})

class UserFollowingHandler(CacheMixin, BaseHandler):
    @cache(30)
    @gen.coroutine
    def get(self):
        login_user = self.get_secure_cookie('username', None)
        username = self.get_argument('u', '')
        reponame = self.get_argument('r', '')
        res = []
        if username and reponame:
            # user = yield self.db.user.find_one({'username': username})
            # if user:
            cursor = self.db.event.find(
                {'username': username, 'reponame': reponame},
                {'sender.followers': 1, 'sender.sender_name': 1, 'sender.avatar_url': 1, '_id': 0}
            ).sort('sender.followers', -1).limit(5)
            if cursor:
                while (yield cursor.fetch_next):
                    doc = cursor.next_object()
                    if not login_user:
                        doc['sender']['followed'] = False
                    else:
                        f_bool = yield followed_bool(login_user, doc['sender']['sender_name'])
                        doc['sender']['followed'] = f_bool
                    res.append(doc['sender'])
                if res:
                    self.write({'status': 1, 'result': res})
                    return
        self.write({'status': 0})



class UserCityhandler(CacheMixin, BaseHandler):
    @cache(60*5)
    @gen.coroutine
    def get(self):
        username = self.get_argument('u', '')
        reponame = self.get_argument('r', '')
        res = []
        if username and reponame:
            # user = yield self.db.user.find_one({'username': username})
            # if user:
            city_pipe = [
                {'$match': {'username': username, 'reponame': reponame, 'sender.countrycode': {'$ne': ''}}},
                {'$group': {
                    '_id': '$sender.countrycode',
                    'num': {'$sum': 1},
                }},
                {'$sort': {'_id': 1}},
            ]
            cursor = yield self.db.event.aggregate(city_pipe, cursor={})
            if cursor:
                while (yield cursor.fetch_next):
                    doc = cursor.next_object()
                    res.append(doc)
                if res:
                    self.write({'status': 1, 'result': res})
                    return
        self.write({'status': 0})

class ShowHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        avatar_url = self.get_secure_cookie('avatar_url', None)
        username = self.get_argument('u', '')
        reponame = self.get_argument('r', '')
        chart_filename = '%s_%s' % (username, reponame)
        if username and reponame:
            event = yield self.db.event.find_one({'username': username, 'reponame': reponame})
            if event:
                stars_url = '/stars?u=%s&r=%s' % (username, reponame)
                cities_url = '/cities?u=%s&r=%s' % (username, reponame)
                follows_url = '/follows?u=%s&r=%s' % (username, reponame)
                self.render('show.html', chart_filename=chart_filename, stars_url=stars_url, cities_url=cities_url, follows_url=follows_url, avatar_url=avatar_url)
                return
            else:
                self.error_msg = "<p>We do not have this repo\'s star recodes!</p><p>Please check whether it have any stars,</p><p>or <a href='/add' style='color: #2C3E50'>add it now?</a></p>"
                self.render('show.html', avatar_url=avatar_url)
                return
        self.error_msg = 'We do not have this user or repo!'
        self.render('show.html', avatar_url=avatar_url)


class FollowHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self):
        token = self.get_secure_cookie('token')
        username = self.get_argument('u', '')
        if not username:
            self.write({'status': 0})
            return
        f_bool = follow(username, token)
        if f_bool:
            self.write({'status': 1, 'type': 'follow'})
        else:
            self.write({'status': 0})


# github api "Check if one user follows another" 'GET /users/:username/following/:target_user' do not work.
# so I have to handle it in this way. I do not know why? If you know, pull requests to me.
class UnfollowHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self):
        token = self.get_secure_cookie('token')
        username = self.get_argument('u', '')
        if not username:
            self.write({'status': 0})
            return
        f_bool = unfollow(username, token)
        if f_bool:
            self.write({'status': 1, 'type': 'unfollow'})
        else:
            self.write({'status': 0})