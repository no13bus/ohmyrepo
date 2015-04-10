#coding: utf-8
import os
import motor

settings = {}
settings['debug'] = False
settings['app_name'] = u'App website'
settings['template_path'] = os.path.join(os.path.dirname(__file__), "templates")
settings['static_path'] = os.path.join(os.path.dirname(__file__), "static")
settings['xsrf_cookies'] = True
settings['cookie_secret'] = "81o0TzKaPpGtYdkL5gEmGepeuuYi7EPnp2XdTP1o&Vo="
settings['login_url'] = '/login'
settings['session_secret'] = '08091287&^(01'
settings['session_dir'] = '/home/ohmyrepo/tmp/session'
settings['db'] = motor.MotorClient('localhost', 27017).ohmyrepo

# github application settings
githubapi = {}
githubapi['CLIENT_ID'] ='ba0466e711d7acc1e6b7'
githubapi['CLIENT_SECRET'] = 'e097becd5776e1260dc2e7212d7c073458767494'
githubapi['REDIRECT_URL'] = 'http://ohmyrepo.ml/callback'
githubapi['ACCESS_TOKEN_URL'] = 'https://github.com/login/oauth/access_token'
githubapi['STATE'] = 'a-random-string'
githubapi['WEBHOOK_URL'] = 'http://ohmyrepo.ml/webhook'
githubapi['OAUTH_URL'] = 'https://github.com/login/oauth/authorize?scope=read:repo_hook,write:repo_hook,user:follow&state=a-random-string&redirect_uri=%s&client_id=%s' % (githubapi['REDIRECT_URL'], githubapi['CLIENT_ID'])

