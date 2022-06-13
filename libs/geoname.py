# coding: utf-8
from tornado.httpclient import AsyncHTTPClient, HTTPError, HTTPRequest
from tornado import gen
import json
import random
import time

GEO_NAME = ['no13bus', 'no10bus']
GEO_URL = 'http://api.geonames.org/searchJSON?q=%s&maxRows=1&username=%s'
AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")


@gen.coroutine
def get_geo_name(location):
    client = AsyncHTTPClient()
    url = GEO_URL % (location, random.choice(GEO_NAME))
    print(url)
    resp = {}
    res = None
    try:
        res = yield client.fetch(url)
    except Exception as ex:
        print("error message:%s" % ex.message)
        raise gen.Return(resp)
    print(location)
    res_json = json.loads(res.body)
    if res_json and 'geonames' in res_json and res_json['geonames']:
        res_one = res_json['geonames'][0]
        resp['city'] = res_one['adminName1']
        resp['country'] = res_one['countryName']
        resp['countrycode'] = res_one['countryCode']
    else:
        print(res_json)
        resp['city'] = ''
        resp['country'] = ''
        resp['countrycode'] = ''
    raise gen.Return(resp)
