# coding: utf-8
import sys
import tornado
import tornado.web
import tornado.auth
from tornado import gen
from tornado.web import asynchronous, HTTPError
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.escape import utf8, _unicode
import requests
from jinja2 import Template, Environment, FileSystemLoader
from bson.objectid import ObjectId
import simplejson
from dateutil import parser
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


# http://www.geonames.org/
    def check_xsrf_cookie(self):
        # token = (self.get_argument("_xsrf", None) or
        #          self.request.headers.get("X-Xsrftoken") or
        #          self.request.headers.get("X-Csrftoken"))
        header = self.request.headers
        # print header
        if not 'GitHub-Hookshot' in header['User-Agent']:
            super(BaseHandler, self).check_xsrf_cookie()
            # if not token:
            #     raise HTTPError(403, "'_xsrf' argument missing from POST")
            # _, token, _ = self._decode_xsrf_token(token)
            # _, expected_token, _ = self._get_raw_xsrf_token()
            # if not _time_independent_equals(utf8(token), utf8(expected_token)):
            #     raise HTTPError(403, "XSRF cookie does not match POST argument")
class WebhookHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        pass

    @gen.coroutine
    def post(self):
        res = self.request.body

        # print res
        res_json = json.loads(res)

        # only star fork will triger this webhook!!!! watch(may be can not get by webhook) do not!
        if 'action' in res_json and res_json['action'] == 'started':
            username, reponame = res_json['repository']['full_name'].split('/')

            # self.redirect('/') # gen.coroutine can not support redirect!!!! wtf here is webhook. can not redirect!!
            print res_json['action'], res_json['repository']['full_name'], res_json['sender']['login'], res_json['sender']['avatar_url']
            user = yield self.db.user.find_one({'username':username})
            if user:
                token = user['token']
            else:
                token = None
                self.write('no token')

            repo_bool = yield self.db.event.find_one({'username':username, 'reponame':reponame})
            client = AsyncHTTPClient()
            if repo_bool:
                sender_info = yield client.fetch('https://api.github.com/users/%s?access_token=%s' % (res_json['sender']['login'], token))
                sender_info_json = json.loads(sender_info.body)
                sender = {
                    'followers': sender_info_json['followers'],
                    'sender_name': res_json['sender']['login'],
                    'avatar_url': sender_info_json['avatar_url'],
                    'location': sender_info_json['location'] if 'location' in sender_info_json else ""
                    }
                yield self.db.event.insert({
                    'username': username,
                    'reponame':reponame,
                    'sender': sender,
                    'star_count': res_json['repository']['stargazers_count'],
                    'time': parser.parse(res_json['repository']['updated_at'])
                })
                print 'book false'
            else:
                # stars_user_url = 'https://api.github.com/repos/no13bus/redispapa/stargazers?page=%s&per_page=100&access_token=%s'
                # stars_num = res_json['repository']['stargazers_count'] # it's important
                # page_num = (stars_num / 100 + 2) if stars_num % 100 else (stars_num / 100 + 1)
                # for x in xrange(1,page_num):
                #     star_info = yield client.fetch(stars_user_url % (x, token))
                #     star_info_json = json.loads(star_info.body)
                #     for one in star_info_json:
                #         one_user_url = 'https://api.github.com/users/%s?access_token=%s' % (one['login'] ,token)
                #         sender_info = yield client.fetch(one_user_url)
                #         sender_info_json = json.loads(sender_info.body)
                #         print sender_info_json
                #         sender = {
                #             'followers': sender_info_json['followers'],
                #             'sender_name': one['login'],
                #             'avatar_url': sender_info_json['avatar_url'],
                #             'location': sender_info_json['location'] if 'location' in sender_info_json else ""
                #             }
                #         yield self.db.event.insert({
                #             'username': username,
                #             'reponame':reponame,
                #             'sender': sender # here is no time
                #         })
                event_user_url = 'https://api.github.com/repos/no13bus/redispapa/events?page=%s&per_page=100&access_token=%s'

                i = 1
                while True:

                    event_info = yield client.fetch(event_user_url % (i, token), raise_error=False)
                    if event_info.code != 200:
                        break
                    event_info_json = json.loads(event_info.body)

                    for one in event_info_json:
                        if one['type'] == 'WatchEvent':
                            one_user_url = 'https://api.github.com/users/%s?access_token=%s' % (one['actor']['login'] ,token)
                            print one_user_url
                            sender_info = yield client.fetch(one_user_url, raise_error=False) # no argument raise_error why?
                            if sender_info.code != 200:
                                continue
                            sender_info_json = json.loads(sender_info.body)
                            sender = {
                                'followers': sender_info_json['followers'],
                                'sender_name': one['actor']['login'],
                                'avatar_url': sender_info_json['avatar_url'],
                                'location': sender_info_json['location'] if 'location' in sender_info_json else ""
                            }
                            yield self.db.event.insert({
                                'username': username,
                                'reponame':reponame,
                                'sender': sender, # here is no time
                                'time': parser.parse(one['created_at'])
                            })
                    i = i + 1
                    print event_user_url % (i, token)
                print 'book true'

        # elif 'forkee' in res_json:
        #     print res_json['forkee']['full_name'], res_json['sender']['login'], res_json['sender']['avatar_url']
        self.write('done')

class HomeHandler(BaseHandler):
    # @tornado.web.authenticated
    def get(self):
        # current_user = self.get_current_user()
        avatar_url = self.get_secure_cookie('avatar_url')
        giturl = 'https://github.com/login/oauth/authorize?scope=read:repo_hook,write:repo_hook,user:follow&state=a-random-string&redirect_uri=http://106.186.117.185:8888/callback&client_id=ba0466e711d7acc1e6b7'
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
                    "*"
                ],
                "config": {
                "url": webhook,
                "content_type": "json"
                }
            }
            req = HTTPRequest(url=req_url, method="POST", body=json.dumps(data))
            res = yield client.fetch(req)

        # print res.body

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

