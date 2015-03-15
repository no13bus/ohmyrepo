# coding: utf-8
from mongoengine import *
import datetime

class User(Document):
    login = StringField(required=True,min_length=4,max_length=20)
    email = EmailField(required=True,unique=True)
    name = StringField(required=True,min_length=2)
    password = StringField(required=True)
    blog = URLField()
    bio = StringField(max_length=1000)
    created_at = DateTimeField(default=datetime.datetime.now)
