#coding: utf-8
import os
import motor

settings = {}
settings['debug'] = False
settings['app_name'] = u'App website'
settings['template_path'] = os.path.join(os.path.dirname(__file__), "templates")
settings['static_path'] = os.path.join(os.path.dirname(__file__), "static")
settings['xsrf_cookies'] = True
settings['cookie_secret'] = "81o0T=="
settings['login_url'] = '/login'
settings['session_secret'] = '08091287&^(01'
settings['session_dir'] = '/tmp/session'
settings['db'] = motor.MotorClient('localhost', 27017).ohmyrepo

# github application settings
githubapi = {}
githubapi['CLIENT_ID'] ='Iv1.c8b173e982d40fd4'
githubapi['CLIENT_SECRET'] = 'de38efc439bd65363c6768c6fa6f7c694f746f91'
githubapi['REDIRECT_URL'] = 'https://ohmyrepo.v2j.tech/callback'
githubapi['ACCESS_TOKEN_URL'] = ''
githubapi['STATE'] = ''
githubapi['WEBHOOK_URL'] = 'https://ohmyrepo.v2j.tech/webhook'
githubapi['OAUTH_URL'] = 'https://github.com/login/oauth/authorize'
