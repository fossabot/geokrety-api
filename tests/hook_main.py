import dredd_hooks as hooks

import sys
import os.path as path
import requests
from flask import Flask

# DO NOT REMOVE THIS. This adds the project root for successful imports. Imports from the project directory should be
# placed only below this
sys.path.insert(1, path.abspath(path.join(__file__, "../..")))

from app.models import db

from app.models.user import User
from app.models.news import News
from app.models.news_comment import NewsComment
from app.models.news_subscription import NewsSubscription
from mixer.backend.flask import mixer


stash = {}
api_username = "someone"
api_password = "strong password"
api_uri = "http://localhost:5000/auth/session"


def obtain_token():
    data = {
        "username": api_username,
        "password": api_password
    }
    url = api_uri
    response = requests.post(url, json=data)
    response.raise_for_status()
    parsed_body = response.json()
    token = parsed_body["access_token"]
    return token


@hooks.before_all
def before_all(transaction):
    app = Flask(__name__)
    app.config.from_object('config.TestingConfig')
    db.init_app(app)

    stash['app'] = app
    stash['db'] = db


@hooks.before_each
def before_each(transaction):
    with stash['app'].app_context():
        db.engine.execute("drop database geokrety_unittest")
        db.engine.execute("create database geokrety_unittest")
        db.engine.execute("use geokrety_unittest")
        db.create_all()

        with stash['app'].test_request_context():
            mixer.init_app(stash['app'])
            with mixer.ctx(commit=False):
                user = mixer.blend(User, name=api_username)
                user.password = api_password
                news = mixer.blend(News, author=user)
                news2 = mixer.blend(News, author=None)
                news_comment = mixer.blend(NewsComment, author=user, news=news)
                new_subscription1 = mixer.blend(NewsSubscription, user=user, news=news)

                user2 = mixer.blend(User)
        db.session.add(user)
        db.session.add(user2)
        db.session.add(news)
        db.session.add(news2)
        db.session.add(news_comment)
        db.session.add(new_subscription1)
        db.session.commit()

    if 'token' not in stash:
        stash['token'] = obtain_token()

    transaction['request']['headers']['Authorization'] = "JWT " + stash['token']


@hooks.after_each
def after_each(transaction):
    with stash['app'].app_context():
        db.session.remove()
