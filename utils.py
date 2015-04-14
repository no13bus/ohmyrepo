#coding: utf-8
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from tornado import gen
import json
from dateutil import parser
import logging
from libs.geoname import get_geo_name

# logger = logging.getLogger()
# hdlr = logging.FileHandler(logfile)
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# hdlr.setFormatter(formatter)
# logger.addHandler(hdlr)
# logger.setLevel(logging.ERROR)

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

@gen.coroutine
def webhook_init(username, reponame, client, token, db, add_username):
    event_user_url = 'https://api.github.com/repos/%s/%s/events?page=%s&per_page=100&access_token=%s'
    i = 1
    while True:
        print event_user_url % (username, reponame, i, token)
        event_info = yield client.fetch(event_user_url % (username, reponame, i, token), raise_error=False)
        if event_info.code != 200:
            print event_info.code
            print 'it is done!'
            break
        print 'ooop'
        event_info_json = json.loads(event_info.body)
        for one in event_info_json:
            if one['type'] == 'WatchEvent':
                one_user_url = 'https://api.github.com/users/%s?access_token=%s' % (one['actor']['login'] ,token)
                print one_user_url
                sender_info = yield client.fetch(one_user_url, raise_error=False)
                if sender_info.code != 200:
                    print 'it can not get this user infomation: %s!' % one['actor']['login']
                    continue
                sender_info_json = json.loads(sender_info.body)
                if 'location' in sender_info_json and sender_info_json['location']:
                    location = yield get_geo_name(sender_info_json['location'])
                    if not location:
                        print 'it can not get location by geonames.org!'
                        continue
                    city = location['city']
                    country = location['country']
                    location_str = sender_info_json['location']
                    countrycode = location['countrycode']
                    company = sender_info_json['company']
                else:
                    city = ''
                    country = ''
                    location_str = ''
                    countrycode = ''
                    company = ''
                print 'location: %s' % city
                sender = {
                    'followers': sender_info_json['followers'],
                    'sender_name': one['actor']['login'],
                    'avatar_url': sender_info_json['avatar_url'],
                    'public_repos': sender_info_json['public_repos'],
                    'city': city,
                    'country': country,
                    'location': location_str,
                    'countrycode': countrycode,
                    'company': company
                }
                yield db.event.insert({
                    'username': username,
                    'reponame':reponame,
                    'add_username':add_username,
                    'sender': sender,
                    'time': parser.parse(one['created_at'])
                })
        i = i + 1
    raise gen.Return(True)

@gen.coroutine
def add_webhook(username, reponame, client, token, webhook):
    req_url = "https://api.github.com/repos/%s/%s/hooks?access_token=%s" % (username, reponame, token)
    print 'req_url=%s' % req_url
    all_hooks_resp = yield client.fetch(req_url, raise_error=False)
    print all_hooks_resp.code
    if all_hooks_resp.code != 200:
        print 'all_hooks_resp.code is not 200'
        raise gen.Return(False)
    all_hooks_json = json.loads(all_hooks_resp.body)
    print '******all_hooks_json******'
    print all_hooks_json
    print '******all_hooks_json******'
    if not all_hooks_json:
        hook_res = []
    else:
        hook_res = [i['id'] for i in all_hooks_json if 'url' in i['config'] and i['config']['url']==webhook]

    if not hook_res:
        data = {
            "name": "web",
            "active": True,
            "events": [
                "watch",
                "fork"
            ],
            "config": {
                "url": webhook,
                "content_type": "json"
            }
        }
        req = HTTPRequest(url=req_url, method="POST", body=json.dumps(data))
        res = yield client.fetch(req, raise_error=False)
        print res.code
        if res.code != 201 and res.code != 200:
            print "res.code is %s. it's wrong" % res.code
            raise gen.Return(False)
    raise gen.Return(True)

@gen.coroutine
def add_webhook_event(username, repo_json, reponame, client, token, db):
    sender_info = yield client.fetch('https://api.github.com/users/%s?access_token=%s' % (repo_json['sender']['login'], token), raise_error=False)
    if sender_info.code != 200:
        raise gen.Return(False)
    sender_info_json = json.loads(sender_info.body)
    if 'location' in sender_info_json and sender_info_json['location']:
        location = yield get_geo_name(sender_info_json['location'])
        if not location:
            raise gen.Return(False)
        city = location['city']
        country = location['country']
        countrycode = location['countrycode']
        location_str = sender_info_json['location']
        company = sender_info_json['company']
    else:
        city = ''
        country = ''
        location_str = ''
        countrycode = ''
        company= ''
    print 'city:%s' % city
    sender = {
        'followers': sender_info_json['followers'],
        'sender_name': repo_json['sender']['login'],
        'avatar_url': sender_info_json['avatar_url'],
        'public_repos': sender_info_json['avatar_url'],
        'city': city,
        'country': country,
        'countrycode': countrycode,
        'location': location_str,
        'company': company
        }
    insert_res = yield db.event.insert({
        'username': username,
        'reponame':reponame,
        'sender': sender,
        'star_count': repo_json['repository']['stargazers_count'],
        'time': parser.parse(repo_json['repository']['updated_at'])
    })
    raise gen.Return(insert_res)
