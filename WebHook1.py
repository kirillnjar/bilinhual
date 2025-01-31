from flask import Flask
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from main import *

port = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='Bilinhual',
    avatar='https://dl-media.viber.com/1/share/2/long/vibes/icon/image/0x0/f09b'
           '/fc477e80d5306023ccf92a07170886fee98bba96aca04959700207a62cc6f09b.jpg',
    auth_token='4ac9ce371e67d30e-9dc412b2061eb971-fb15ec32858c9525'
))

viber.set_webhook('https://bilinhual.herokuapp.com/')