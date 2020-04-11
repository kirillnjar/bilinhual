from datetime import time, datetime, timedelta

from sqlalchemy import func, types
from viberbot.api.messages import PictureMessage, KeyboardMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
import random

# Бот
import json
from bot_database import *

KeysStart = dict()
KeysWords = dict()


class viber_bot:
    __unknown_messages_collection = ['?', 'Не понял, что вы имеете ввиду?',
                                     '*предсмертный хрип*']
    current_user = None
    __response_message = None

    # получение ботом запроса
    def set_request(self, viber_request):
        self.session = Session()
        if isinstance(viber_request, ViberSubscribedRequest):
            self.__response_message = self.__add__new__user__(viber_request)
            return
        elif isinstance(viber_request, ViberMessageRequest):
            self.current_user = self.__get__user__(viber_request)
            word = viber_request.message.text
            if word[0] == '/':
                word = word.replace('/', '')
                if word.split(' ')[0].lower() == 'help':
                    self.__response_message = self.__help__message__()
                elif word.split(' ')[0].lower() == 'start':
                    self.__response_message = self.__new__word__message__(True)
                elif word.split(' ')[0].lower() == 'difficulty':
                    self.__response_message = self.__change__difficulty__message__()
                elif word.split(' ')[0].lower() == 'example':
                    self.__response_message = self.__example_message__()
                elif word.split(' ')[0].lower() == 'taside':
                    self.__response_message = self.__get__aside__()
                elif word.split(' ')[0].lower() == 'tdisable':
                    self.__response_message = self.__get__disable__()
                else:
                    self.__response_message = self.__unknown__message__()
            elif word[0] == 'd':
                print(word[1])
                KeysWords[self.current_user.id]['difficulty'] = int(word[1])
                self.__save__answer__()
                self.__response_message = self.__new__word__message__()
            elif word in ['1', '2', '3', '4']:
                self.__response_message = self.__answer_message__(word.split(' ')[0].lower())
                pass
            else:
                self.__response_message = self.__unknown__message__()
        else:
            self.__response_message = None

    # ответ бота
    def get_response(self):
        return self.__response_message

    # добавление нового пользователя
    def __add__new__user__(self, viber_request):
        user = self.__get__user__(viber_request)
        self.current_user = user
        if user is None:
            user = bot_users(viber_id=viber_request.user.id, name=viber_request.user.name)
            self.session.add(user)
            self.session.commit()
            messages = self.__hello__message__(user)
        else:
            messages = self.__comeback__message__(user)
        return messages

    # сообщение приветствия 1
    def __hello__message__(self, user):
        messages = [PictureMessage(text="Поздравляю тебя с подпиской, " + user.name,
                                   media='https://pngimage.net/wp-content/uploads/2018/06/%D1%87%D0%B5%D0%BB%D0%BE%D0'
                                         '%B2%D0%B5%D1%87%D0%BA%D0%B8-png-%D0%B4%D0%B5%D0%BD%D1%8C%D0%B3%D0%B8-2.png'),
                    TextMessage(
                        text='Я создан для того, чтобы помогать людям в изучение новых слов на английском языке')]
        return messages + self.__help__message__()

    # сообщение приветствия 2
    def __comeback__message__(self, user):
        messages = [PictureMessage(text="С возвращением, " + user.name,
                                   media='https://static4.depositphotos.com/1000765/349/i/450/depositphotos_3491019'
                                         '-stock-photo-3d-small-empty-product-box.jpg'),
                    TextMessage(
                        text='Надеюсь ты не забыл, что я создан для того, чтобы помогать людям в изуение новых слов '
                             'на английском языке')]
        return messages + self.__help__message__()

    # сообщение помощи
    def __help__message__(self):
        self.current_user.notice_time = None
        return [TextMessage(text='Чтобы начать изучение - нажми на СТАРТ'),
                KeyboardMessage(keyboard=self.__get__keys_start__())]

    # получение данных о пользователе из БД
    def __get__user__(self, viber_request):
        if isinstance(viber_request, ViberMessageRequest):
            users = self.session.query(bot_users).filter(bot_users.viber_id == viber_request.sender.id).all()
        else:
            users = self.session.query(bot_users).filter(bot_users.viber_id == viber_request.user.id).all()
        if len(users) == 0:
            return None
        else:
            return users[0]

    # получение ответа на неизвестную команду
    def __unknown__message__(self):
        self.session = Session()
        if self.current_user.id not in KeysWords:
            keyboard = self.__get__keys_start__()
        else:
            keyboard = KeysWords[self.current_user.id]['keyboard']

        return [
            TextMessage(text=(
                self.__unknown_messages_collection[random.randint(0, len(self.__unknown_messages_collection) - 1)])),
            KeyboardMessage(keyboard=keyboard)]

    # сообщение с новым словом
    def __new__word__message__(self, is_start=False):
        # закончился ли раунд?
        if self.session.query(bot_users_answers).count() % 3 == 0 and not is_start:
            answers = self.session.query(bot_users_answers).order_by(bot_users_answers.id.desc()).limit(3).all()
            score = 0
            for answer in answers:
                if answer.is_right:
                    score = score + 1
            message = [TextMessage(
                text='Раунд завершен. Ваш результат: ' + str(score) + ' из 10'),
                          TextMessage(text='Отлично сыграно!')] + self.__help__message__()
            return message

        KeysNewWord = json.load(open('word_keyboard.json', encoding='utf-8'))

        # Полуаем количество повторов для запоминания
        repeats_number = self.current_user.repeats_number
        if repeats_number is None:
            repeats_number = 20

        # получаем слова
        words = self.session.query(bot_words) \
            .outerjoin(bot_words.bot_users_answers) \
            .group_by(bot_words) \
            .having(func.count_(bot_words.bot_users_answers) < repeats_number) \
            .order_by(func.random()) \
            .limit(4) \
            .all()

        # выбираем индекс правильного ответа
        right_answer_index = random.choice(range(0, 4))

        # создаем клавиатуру
        KeysNewWord['Buttons'][0]['Text'] = words[0].translation
        KeysNewWord['Buttons'][1]['Text'] = words[1].translation
        KeysNewWord['Buttons'][2]['Text'] = words[2].translation
        KeysNewWord['Buttons'][3]['Text'] = words[3].translation

        # сохраняем данные о текущем вопросе
        sentences = list()
        if len(words[right_answer_index].bot_examples) != 0:
            for i in range(0, len(words[right_answer_index].bot_examples)):
                sentences.append(words[right_answer_index].bot_examples[i].sentence)
        print(sentences)
        KeysWords[self.current_user.id] = dict(right_answer=words[right_answer_index],
                                               right_answer_index=right_answer_index, keyboard=KeysNewWord,
                                               examples=sentences, is_right=False)

        # обрабокта законена. подтверждаем транзакцию
        self.session.commit()

        # задаем вопрос
        return [TextMessage(text='Ваше слово: ' + words[right_answer_index].word),
                TextMessage(text='Выберите верный вариант на клавиатуре'),
                KeyboardMessage(keyboard=KeysNewWord)]

    def __answer_message__(self, answer_index):
        # Если нет предыдущего раунда
        if self.current_user.id not in KeysWords:
            return self.__unknown__message__()

        # Правильный ответ?
        KeysWords[self.current_user.id]['is_right'] = \
            KeysWords[self.current_user.id]['right_answer_index'] == int(answer_index) - 1

        # Формируем сообщение
        if KeysWords[self.current_user.id]['is_right']:
            message = [TextMessage(text='Верно! Вы получаете один балл')]
        else:
            message = [TextMessage(text='Ой, вы ошиблись!'),
                       TextMessage(text='Правильный ответ "' + KeysWords[self.current_user.id][
                           'right_answer'].translation + '"')]


        self.__save__answer__()
        message = message + self.__new__word__message__()

        return message

    def __example_message__(self):
        # Если примеры кончились
        if len(KeysWords[self.current_user.id]['examples']) == 0:
            return [TextMessage(
                text='Это все примеры, что у меня есть...'),
                KeyboardMessage(keyboard=KeysWords[self.current_user.id]['keyboard'])]

        # Выбираем случайный пример
        message_text = random.choice(KeysWords[self.current_user.id]['examples'])

        # Удаляем полученный пример
        KeysWords[self.current_user.id]['examples'].remove(message_text)

        # Возвращаем сообщение с примеров
        return [TextMessage(
            text=message_text),
            KeyboardMessage(keyboard=KeysWords[self.current_user.id]['keyboard'])]

    def __save__answer__(self):
        # Добавляем ответ в базу
        self.session = Session()
        id_difficulty = None
        if 'difficulty' in KeysWords[self.current_user.id]:
            id_difficulty = KeysWords[self.current_user.id]['difficulty']
        user_answer = bot_users_answers(id_user=self.current_user.id,
                                        id_word=KeysWords[self.current_user.id]['right_answer'].id,
                                        is_right=KeysWords[self.current_user.id]['is_right'],
                                        answer_date=self.session.query(func.current_timestamp(type_=types.DateTime)),
                                        id_difficulty=id_difficulty)
        self.session.add(user_answer)
        self.session.commit()

    def __change__difficulty__message__(self):
        self.current_user.is_difficulty_need = not self.current_user.is_difficulty_need

        if not self.current_user.is_difficulty_need:
            message = [TextMessage(text='Жаль что вы не хотите помочь улучшить каество предлагаемых слов '),
                       TextMessage(text='Если вы передумаете - нажмите на ОТМЕЧАТЬ СЛОЖНОСТЬ ПОСЛЕ ОТВЕТА. Спасибо!')]
        else:
            message = [TextMessage(text='Спасибо за помощь')]

        message = message + [KeyboardMessage(keyboard=self.__get__keys_start__())]

        self.session.commit()
        return message

    def __get__keys_start__(self):
        if self.current_user.id not in KeysStart:
            KeysStart[self.current_user.id] = json.load(open('start_keyboard.json', encoding='utf-8'))

        if self.current_user.is_difficulty_need:
            KeysStart[self.current_user.id]['Buttons'][1]['Text'] = KeysStart[self.current_user.id]['Buttons'][1][
                'Text']. \
                replace('НЕ ', '').replace('ОТМЕЧАТЬ', 'НЕ ОТМЕЧАТЬ')
        else:
            KeysStart[self.current_user.id]['Buttons'][1]['Text'] = KeysStart[self.current_user.id]['Buttons'][1][
                'Text'].replace('НЕ ', '')

        if self.current_user.is_notice_need:
            KeysStart[self.current_user.id]['Buttons'][2]['Text'] = \
                KeysStart[self.current_user.id]['Buttons'][2]['Text'].replace('Выключить напоминания', 'Включить напоминания')
        else:
            KeysStart[self.current_user.id]['Buttons'][2]['Text'] = \
                KeysStart[self.current_user.id]['Buttons'][2]['Text'].replace('Включить напоминания', 'Выключить напоминания')

        return KeysStart[self.current_user.id]

    def __get__aside__(self):
        if self.current_user.id not in KeysWords:
            keyboard = self.__get__keys_start__()
        else:
            keyboard = KeysWords[self.current_user.id]['keyboard']
        if self.current_user.notice_time is None:
            self.current_user.notice_time = timedelta(minutes=30)
        self.current_user.notice_time = self.current_user.notice_time + timedelta(minutes=30)
        self.session.commit()
        return [TextMessage(text="Оки-доки"),
                KeyboardMessage(keyboard=keyboard)]

    def __get__disable__(self):

        if self.current_user.id not in KeysWords:
            keyboard = self.__get__keys_start__()
        else:
            keyboard = KeysWords[self.current_user.id]['keyboard']
        if self.current_user.is_notice_need:
            message = \
                [TextMessage(text="Включить напоминание можно будет в конце каждого раунда"),
                 KeyboardMessage(keyboard=keyboard)]
        else:
            message = \
                [TextMessage(text="Я о вас не забуду."),
                 KeyboardMessage(keyboard=keyboard)]
        self.current_user.is_notice_need = not self.current_user.is_notice_need
        self.session.commit()
        return message