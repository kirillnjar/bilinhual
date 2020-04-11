from flask import Flask
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from main import *

port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='EngShibe',
    avatar='https://previews.123rf.com/images/greenoptix/greenoptix1904/greenoptix190400022/123442578-illustration-shiba-inu-for-all-dog-owners-what-you-love-about-his-dog-puppy-dog-%C3%A2%E2%82%AC%E2%80%B9%C3%A2%E2%82%AC%E2%80%B9eyes-wagging-t.jpg',
    auth_token='4ac7d72339e7d0b5-f614c0688c0c27e9-a6bb05e7fe56834b',
))

viber.set_webhook('https://bilinhual.herokuapp.com/')