# coding: utf-8
import re
from jinja2.utils import urlize, escape
import urllib, hashlib

def tags_name_tag(tags,limit = 0):
    html = []
    if not tags: return ""
    if limit > 0:
      tags = tags[0:limit]
    for tag in tags:
        html.append('<a class="tag" href="/tag/%s">%s</a>' % (tag,tag))
    return ",".join(html)

def user_name_tag(user):
    return '<a href="/%s" class="user">%s</a>' % (user.login,user.name)
        
def strftime(value, type='normal'):
    if type == 'normal':
        format="%Y-%m-%d %H:%M"
    elif type == 'long':
        format="%Y-%m-%d %H:%M:%S"
    else:
        format="%m-%d %H:%M"
    return value.strftime(format)

def strfdate(value,type='normal'):
    if type == 'normal':
        format="%Y-%m-%d"
    elif type == "long":
        format="%Y-%m-%d"
    else:
        format="%m-%d"
    return value.strftime(format)

# check value is in list
def inlist(value,list):
    if list.count(value) > 0:
        return True
    return False

def avatar(user, size = 40):
    gravatar_url = "http://www.gravatar.com/avatar/" + hashlib.md5(user.email).hexdigest() +  "?" 
    gravatar_url += urllib.urlencode({'s':str(size)})
    return "<a href=\"/%s\" class=\"avatar\"><img src=\"%s\" style=\"width:%dpx;\" title=\"%s\" /></a>" % (user.login,gravatar_url,size,user.name)

    
