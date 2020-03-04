from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='Bilinhual',
    avatar='https://dl-media.viber.com/1/share/2/long/vibes/icon/image/0x0/f09b'
           '/fc477e80d5306023ccf92a07170886fee98bba96aca04959700207a62cc6f09b.jpg',
    auth_token='4ac9ce371e67d30e-9dc412b2061eb971-fb15ec32858c9525'
))
viber.set_webhook('https://17831b1f.ngrok.io')