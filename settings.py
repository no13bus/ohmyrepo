#coding: utf-8
import os
import motor

settings = {}
settings['app_name'] = u'App website'
settings['template_path'] = os.path.join(os.path.dirname(__file__), "templates")
settings['static_path'] = os.path.join(os.path.dirname(__file__), "static")
settings['xsrf_cookies'] = True
settings['cookie_secret'] = "81o0TzKaPpGtYdkL5gEmGepeuuYi7EPnp2XdTP1o&Vo="
settings['login_url'] = '/login'
settings['session_secret'] = '08091287&^(01'
settings['session_dir'] = os.path.join(os.path.dirname(__file__), "tmp/session")
settings['db'] = motor.MotorClient('localhost', 27017).ohmyrepo


githubapi = {}
githubapi['CLIENT_ID'] ='ba0466e711d7acc1e6b7'
githubapi['CLIENT_SECRET'] = '91c5c7e329eedf2807d1230de224bf7443df7100'
githubapi['REDIRECT_URL'] = 'http://127.0.0.1:8888/callback'
githubapi['ACCESS_TOKEN_URL'] = 'https://github.com/login/oauth/access_token'
githubapi['STATE'] = 'a-random-string'
githubapi['WEBHOOK'] = 'http://127.0.0.1:8888/webhook'
