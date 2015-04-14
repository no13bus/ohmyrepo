# coding: utf-8
import tornado
from tornado import gen
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from settings import githubapi
import json
from tornado.httputil import url_concat
from utils import add_webhook_event, add_webhook, webhook_init
from .base import BaseHandler


class WebhookHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        res = self.request.body
        res_json = json.loads(res)
        # only star will triger this webhook! watch(may be can not get by webhook) do not!
        if 'action' in res_json and res_json['action'] == 'started':
            username, reponame = res_json['repository']['full_name'].split('/')
            user = yield self.db.user.find_one({'username': username})
            if user:
                token = user['token']
            else:
                # self.redirect('/') is not suited for here because this is webhook, it's not the browser client.
                self.write('ohmyrepo website do not have this user!')
                return
            client = AsyncHTTPClient()
            # repo_bool = yield self.db.event.find_one({'username': username, 'reponame': reponame})
            # if repo_bool:
            insert_res = yield add_webhook_event(username, res_json, reponame, client, token, self.db)
            if insert_res:
                self.write('insert success')
                return
        self.write('failure')

class CallbackHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        code = self.get_argument('code')
        client = AsyncHTTPClient()
        params = {
            'client_id': githubapi['CLIENT_ID'],
            'redirect_uri': githubapi['REDIRECT_URL'],
            'client_secret': githubapi['CLIENT_SECRET'],
            'code': code
        }
        url = url_concat('https://github.com/login/oauth/access_token', params)
        req = HTTPRequest(url=url, method='POST', headers={'Accept': 'application/json'}, body='')
        res = yield client.fetch(req, raise_error=False)
        if res.code != 200:
            self.redirect('/login')
        resp_json = json.loads(res.body)
        # get user token
        token = resp_json['access_token']
        req_url = url_concat('https://api.github.com/user', {'access_token': token})
        req_user = HTTPRequest(url=req_url, method='GET')
        res_user = yield client.fetch(req_user, raise_error=False)
        if res_user.code != 200:
            self.redirect('/login')
        user_info = json.loads(res_user.body)
        # get user info
        username = user_info['login']
        avatar_url = user_info['avatar_url']
        user = yield self.db.user.find_one({'username': username})
        # insert user info
        if not user:
            user_id = yield self.db.user.insert({'username': username, 'token': token, 'avatar_url': avatar_url})
            print user_id
        else:
            res_update = yield self.db.user.update({'username': username}, {'$set': {'token': token}})
            print res_update
        self.set_secure_cookie('token', token)
        self.set_secure_cookie('username', username)
        self.set_secure_cookie('avatar_url', avatar_url)
        # self.session['token'] = token
        # self.session.save()
        self.redirect('/')

class AddWebhookHandler(BaseHandler):
    @tornado.web.authenticated
    @gen.coroutine
    def get(self):
        self.render('add.html', avatar_url=self.get_secure_cookie('avatar_url'))

    @tornado.web.authenticated
    @gen.coroutine
    def post(self):
        repo_url = self.get_argument('webhook_url', '')
        print 'repo_url=%s' % repo_url
        reponame = repo_url.split('/')[-1]
        username = repo_url.split('/')[-2]
        add_username = self.get_secure_cookie('username')
        # if username == self.get_secure_cookie('username'):
        res = yield self.db.event.find_one({'username': username, 'reponame': reponame})
        if res:
            self.error_msg = 'You already add this repo!'
            self.render('add.html', avatar_url=self.get_secure_cookie('avatar_url'))
        else:
            client = AsyncHTTPClient()
            token = self.get_secure_cookie('token')
            set_hook_res = yield add_webhook(username, reponame, client, token, githubapi['WEBHOOK_URL'])
            # database init
            if set_hook_res:
                tornado.ioloop.IOLoop.current().spawn_callback(webhook_init, username, reponame, client, token, self.db, add_username)
                self.set_flash("This repo is initializing. You can refresh after a while. You can see <a href='/repos'>others\'s repos</a>.")
                self.redirect('/show?u=%s&r=%s' % (username, reponame))
            else:
                self.error_msg = 'This repo is not yours or there is some error when it is added. Please add it again.'
                self.render('add.html', avatar_url=self.get_secure_cookie('avatar_url'))
        # else:
        #     self.error_msg = 'This repo is not yours!'
        #     self.render('add.html', avatar_url=self.get_secure_cookie('avatar_url'))