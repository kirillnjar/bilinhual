import datetime
import json
import random

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func, types, and_
from sqlalchemy.sql.functions import coalesce
from viberbot.api.messages import TextMessage, KeyboardMessage

from bot_database import *
from main import viber

sched = BlockingScheduler()

hello_messages = ['Привет,', 'И снова здравствуйте,', 'Доброго времени суток,']

@sched.scheduled_job('interval', minutes=10)
def notice_job():
    session = Session()
    us = session.query(bot_users) \
        .outerjoin(bot_users.bot_users_answers) \
        .group_by(bot_users) \
        .having(and_(func.current_timestamp(type_=types.DateTime) - func.max(bot_users_answers.answer_date) > coalesce(
        bot_users.notice_time, '00:30:00'), bot_users.is_notice_need)) \
        .all()
    for u in us:
        message = [TextMessage(text=random.choice(hello_messages) + " " + u.name + "! Вы не забыли об обучении? (hmm)"),
                   KeyboardMessage(keyboard=__get__keys_notice__(u))]
        viber.send_messages(u.viber_id, message)


def __get__keys_notice__(user):
    NoticeKeys = json.load(open('notice_keyboard.json', encoding='utf-8'))

    if not user.is_notice_need:
        NoticeKeys['Buttons'][2]['Text'] = \
            NoticeKeys['Buttons'][2]['Text'].replace('ОТКАЗАТЬСЯ ОТ НАПОМИНАНИЙ', 'ВКЛЮЧИТЬ НАПОМИНАНИЯ')
    else:
        NoticeKeys['Buttons'][2]['Text'] = \
            NoticeKeys['Buttons'][2]['Text'].replace('ВКЛЮЧИТЬ НАПОМИНАНИЯ', 'ОТКАЗАТЬСЯ ОТ НАПОМИНАНИЙ')

    return NoticeKeys


sched.start()
