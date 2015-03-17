# coding: utf-8
import sys
import tornado.web
import tornado.auth
from tornado import gen
from tornado.web import asynchronous
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
import requests
from jinja2 import Template, Environment, FileSystemLoader
from bson.objectid import ObjectId
import simplejson

import filter, utils, session
from forms import *
# from models import *
from settings import githubapi
from libs.githubpy import GitHub
import json
from tornado.httputil import url_concat

# gh = GitHub(client_id=githubapi['CLIENT_ID'], client_secret=githubapi['CLIENT_SECRET'],
#             redirect_uri=githubapi['REDIRECT_URL'], scope='read:repo_hook,write:repo_hook,user:follow')
# giturl = gh.authorize_url(state=githubapi['STATE'])
# giturl = '/callback'

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

class BaseHandler(tornado.web.RequestHandler):

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        self.session = session.TornadoSession(application.session_manager, self)
        self._title = self.settings['app_name']
        self.db = self.settings['db']

    def render_string(self,template,**args):
        env = Environment(loader=FileSystemLoader(self.settings['template_path']))
        env.filters['tags_name_tag'] = filter.tags_name_tag
        env.filters['user_name_tag'] = filter.user_name_tag
        env.filters['strftime'] = filter.strftime
        env.filters['strfdate'] = filter.strfdate
        env.filters['avatar'] = filter.avatar
        env.filters['truncate_lines'] = utils.truncate_lines
        template = env.get_template(template)
        return template.render(settings=self.settings,
                               title=self._title,
                               notice_message=self.notice_message,
                               current_user=self.current_user,
                               static_url=self.static_url,
                               modules=self.ui['modules'],
                               xsrf_form_html=self.xsrf_form_html,
                               **args)

    def render(self, template, **args):
        self.finish(self.render_string(template, **args))

    # @gen.coroutine
    def get_current_user(self):
        return self.get_secure_cookie("username")

    def notice(self,msg,type = "success"):
        type = type.lower()
        if ['error','success','warring'].count(type) == 0:
            type = "success"
        self.session["notice_%s" % type] = msg 
        self.session.save()

    @property
    def notice_message(self):
        try:
          msg = self.session['notice_error']
          self.session['notice_error'] = None
          self.session['notice_success'] = None
          self.session['notice_warring'] = None
          self.session.save()
          if not msg:
            return ""
          else:
            return msg
        except:
          return ""

    def render_404(self):
        raise tornado.web.HTTPError(404)

    def set_title(self, str):
        self._title = u"%s - %s" % (str,self.settings['app_name'])

class WebhookHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        pass

    def post(self):
        print self.get_argument('action')
        self.write('ooooo')

class HomeHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        # current_user = self.get_current_user()
        avatar_url = self.get_secure_cookie('avatar_url')
        giturl = 'https://github.com/login/oauth/authorize?scope=read:repo_hook,write:repo_hook,user:follow&state=a-random-string&redirect_uri=http://127.0.0.1:8888/callback&client_id=ba0466e711d7acc1e6b7'
        self.render("home.html", giturl=giturl, avatar_url=avatar_url)

    @gen.coroutine
    def post(self):
        webhook = self.get_argument('webhook', None)
        token = self.get_secure_cookie('token')
        req_url = "https://api.github.com/repos/%s/%s/hooks?access_token=%s" % (self.get_secure_cookie('username'), 'redispapa', token)
        client = AsyncHTTPClient()
        # get all of hooks
        all_hooks_resp = yield client.fetch(req_url)
        all_hooks_json = json.loads(all_hooks_resp.body)
        hook_res = [i['id'] for i in all_hooks_json if i['config']['url']==webhook]
        # print hook_res
        if hook_res:
            hook_id = hook_res[0]
            print hook_id
            req_url_hook = "https://api.github.com/repos/%s/%s/hooks/%s?access_token=%s" % (self.get_secure_cookie('username'), 'redispapa', hook_id, token)
            data = {
                "active": True,
                "events": [
                "push",
                "pull_request",
                "watch",
                "fork"
                ]
            }
            print req_url_hook
            req = HTTPRequest(url=req_url_hook, method="PATCH", body=json.dumps(data))
            res = yield client.fetch(req)
        else:
            data = {
                "name": "web",
                "active": True,
                "events": [
                "push",
                "pull_request",
                "watch",
                "fork"
                ],
                "config": {
                "url": webhook,
                "content_type": "json"
                }
            }
            req = HTTPRequest(url=req_url, method="POST", body=json.dumps(data))
            res = yield client.fetch(req)

        print res.body

        self.write('pppp')


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.set_secure_cookie("username","")
        self.set_secure_cookie("avatar_url","")
        self.set_secure_cookie("token","")
        self.redirect("/")


class LoginHandler(BaseHandler):
    @gen.coroutine
    def get(self):
        code = self.get_argument('code')
        client = AsyncHTTPClient()
        # https://api.github.com/users/no13bus
        params = {
            'client_id': githubapi['CLIENT_ID'],
            'redirect_uri': githubapi['REDIRECT_URL'],
            'client_secret': githubapi['CLIENT_SECRET'],
            'code': code
        }
        url = url_concat("https://github.com/login/oauth/access_token", params)
        req = HTTPRequest(url=url, method="POST",headers={"Accept": "application/json"}, body='')
        res = yield client.fetch(req)
        resp_json = json.loads(res.body)
        token = resp_json['access_token']
        req_url = url_concat("https://api.github.com/user", {'access_token': token})
        req_user = HTTPRequest(url=req_url, method="GET")
        res_user = yield client.fetch(req_user)

        user_info = json.loads(res_user.body)
        username = user_info['login']
        avatar_url = user_info['avatar_url']
        user = yield self.db.user.find_one({'username': username})
        if not user:
            user_id = yield self.db.user.insert({'username': username, 'token': token, 'avatar_url': avatar_url})
            print user_id

        self.set_secure_cookie("token",token)
        self.set_secure_cookie("username",username)
        self.set_secure_cookie("avatar_url",avatar_url)
        self.redirect('/')


class RegisterHandler(BaseHandler):
    pass
#     def get(self):
#         self.set_title(u"注册")
#         user = User()
#         self.render("register.html", user=user)
#
#     def post(self):
#         self.set_title(u"注册")
#         frm = RegisterForm(self)
#         if not frm.validate():
#             frm.render("register.html")
#             return
#
#         user = User(name=frm.name,
#                     login=frm.login,
#                     email=frm.email,
#                     password=utils.md5(frm.password))
#         try:
#           user.save()
#           self.set_secure_cookie("user_id",str(user.id))
#           self.redirect("/")
#         except Exception,exc:
#           self.notice(exc,"error")
#           frm.render("register.html")

