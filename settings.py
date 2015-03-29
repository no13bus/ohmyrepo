#coding: utf-8
import os
import motor

settings = {}
settings['debug'] = False
settings['app_name'] = u'App website'
settings['template_path'] = os.path.join(os.path.dirname(__file__), "templates")
settings['static_path'] = os.path.join(os.path.dirname(__file__), "static")
settings['xsrf_cookies'] = True
settings['cookie_secret'] = "&Vo="
settings['login_url'] = '/login'
settings['session_secret'] = '9988&^(01'
settings['session_dir'] = '/home/ohmyrepo/tmp/session'
settings['db'] = motor.MotorClient('localhost', 27017).ohmyrepo

# github application settings. change it to your app settings
githubapi = {}
githubapi['CLIENT_ID'] =''
githubapi['CLIENT_SECRET'] = ''
githubapi['REDIRECT_URL'] = ''
githubapi['ACCESS_TOKEN_URL'] = ''
githubapi['STATE'] = ''
githubapi['WEBHOOK_URL'] = ''
githubapi['OAUTH_URL'] = ''

