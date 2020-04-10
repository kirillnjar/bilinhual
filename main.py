from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
import os
from viber_bot import viber_bot

app = Flask(__name__)
viber = Api(BotConfiguration(
    name='EngShibe',
    avatar='https://previews.123rf.com/images/greenoptix/greenoptix1904/greenoptix190400022/123442578-illustration-shiba-inu-for-all-dog-owners-what-you-love-about-his-dog-puppy-dog-%C3%A2%E2%82%AC%E2%80%B9%C3%A2%E2%82%AC%E2%80%B9eyes-wagging-t.jpg',
    auth_token='4ac7d72339e7d0b5-f614c0688c0c27e9-a6bb05e7fe56834b',
))



@app.route('/', methods=['POST'])
def incoming():
    viber_request = viber.parse_request(request.get_data())

    bot = viber_bot()
    bot.set_request(viber_request)
    messages = bot.get_response()
    if messages is not None:
        print(messages)
        viber.send_messages(bot.current_user.viber_id, messages)
        pass
    return Response(status=200)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
