import json

from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy import func, types, and_
from sqlalchemy.sql.functions import coalesce
from viberbot.api.messages import TextMessage, KeyboardMessage

from bot_database import *
from main import viber

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=1)
def notice_job():
    session = Session()
    us = session.query(bot_users) \
        .outerjoin(bot_users.bot_users_answers) \
        .group_by(bot_users) \
        .having(and_(func.current_timestamp(type_=types.DateTime) - func.max(bot_users_answers.answer_date) > coalesce(
        bot_users.notice_time, '00:30:00'), bot_users.notice_time != '00:00:00')) \
        .all()
    for u in us:
        message = [TextMessage(text="Тест 1. Сообщение отправлено автоматически"),
                   KeyboardMessage(keyboard=json.load(open('notice_keyboard.json', encoding='utf-8')))]
        viber.send_messages(u.viber_id, message)


sched.start()
