# Бот
import json
import random
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.sql.elements import Null
from viberbot.api.messages import PictureMessage, KeyboardMessage, FileMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest

from bot_database import *
from yandex_dictionary import YandexDictionary

KeysStart = dict()
KeysWords = dict()

translater = YandexDictionary('dict.1.1.20200220T183914Z.ad078cb041516bce.6b3e7e48c087bb3b3f18013a1f8e0a05acbf9ac4')


class viber_bot:
    __unknown_messages_collection = ['Не понимаю о чем ты говоришь', 'Данная информация не может быть мною распознана',
                                     'Критическая ошибка в программе. Соощение ошибки: "Убить всех человеков"']
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
                elif word.split(' ')[0].lower() == 'hint':
                    self.__response_message = self.__hints_message__()
                elif word.split(' ')[0].lower() == 'backhint':
                    self.__response_message = self.__backhints_message__()
                elif word.split(' ')[0].lower() == 'example':
                    self.__response_message = self.__example_message__()
                elif word.split(' ')[0].lower() == 'syn':
                    self.__response_message = self.__sym_message__()
                elif word.split(' ')[0].lower() == 'taside':
                    self.__response_message = self.__get__aside__()
                elif word.split(' ')[0].lower() == 'tdisable':
                    self.__response_message = self.__get__disable__()
                elif word.split(' ')[0].lower() == 'tts':
                    self.__response_message = self.__get__tts__()
                else:
                    self.__response_message = self.__unknown__message__()
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
                        text='Надеюсь ты не забыл, что я создан для того, чтобы помогать людям в изучение новых слов '
                             'на английском языке')]
        return messages + self.__help__message__()

    # сообщение помощи
    def __help__message__(self):
        self.session.commit()
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
        if self.session.query(bot_users_answers).count() % 10 == 0 and not is_start:
            answers = self.session.query(bot_users_answers).order_by(bot_users_answers.id.desc()).limit(10).all()
            score = 0
            for answer in answers:
                if answer.is_right:
                    score = score + 1
            message = [TextMessage(
                text='Раунд закончился. Ваш результат: ' + str(score) + ' из 10'),
                          TextMessage(text='Спасибо за игру! (like)')] + self.__help__message__()
            return message

        KeysNewWord = json.load(open('word_keyboard.json', encoding='utf-8'))

        # получаем слова
        words = self.session.query(bot_words) \
            .outerjoin(bot_words.bot_users_answers) \
            .group_by(bot_words) \
            .having(func.count_(bot_words.bot_users_answers) < 20) \
            .order_by(func.random()) \
            .limit(4) \
            .all()

        # выбираем индекс правильного ответа
        right_answer_index = random.choice(range(0, 4))
        right_word_info = json.loads(translater.lookup(words[right_answer_index].word, 'en', 'ru'))['def'][0]

        # создаем клавиатуру
        for i in range(0, 4):
            if i == right_answer_index:
                KeysNewWord['Buttons'][right_answer_index]['Text'] = right_word_info['tr'][0]['text'].capitalize()
            else:
                KeysNewWord['Buttons'][i]['Text'] = \
                    json.loads(translater.lookup(words[i].word, 'en', 'ru'))['def'][0]['tr'][0]['text'].capitalize()

        sentence = []
        for ex in right_word_info['tr'][0]['ex']:
            sentence.append(ex['text'].capitalize())

        syms = []
        for sym in right_word_info['tr'][0]['mean']:
            syms.append(sym['text'].capitalize())

        # сохраняем данные о текущем вопросе
        KeysWords[self.current_user.id] = dict(right_answer=words[right_answer_index],
                                               right_translation=right_word_info['tr'][0]['text'].capitalize(),
                                               right_transcription=right_word_info['ts'],
                                               right_answer_index=right_answer_index, keyboard=KeysNewWord,
                                               syms=syms,
                                               examples=sentence, is_right=False)

        # обрабокта законена. подтверждаем транзакцию
        self.session.commit()
        # задаем вопрос
        return [TextMessage(text='Ваше слово: ' + words[right_answer_index].word),
                TextMessage(text='Вариатны перевода представлены на клавиатуре'),
                TextMessage(text='Удачи!(moa)'),
                KeyboardMessage(keyboard=KeysNewWord)]

    def __answer_message__(self, answer_index):
        if self.current_user.id not in KeysWords:
            return self.__unknown__message__()

        print(self.current_user)
        self.current_user.notice_time = None
        self.session.add(self.current_user)
        self.session.commit()
        print(self.current_user)

        # Правильный ответ?
        KeysWords[self.current_user.id]['is_right'] = \
            KeysWords[self.current_user.id]['right_answer_index'] == int(answer_index) - 1

        # Формируем сообщение
        if KeysWords[self.current_user.id]['is_right']:
            message = [TextMessage(text='И это правильный ответ! Вы получаете плюс один балл (smiley)')]
        else:
            message = [TextMessage(text='К сожалению вы ошиблись! Баллов не будет, но вы держитесь(ugh)'),
                       TextMessage(text='Правильный ответ "' + KeysWords[self.current_user.id][
                           'right_translation'] + '"')]

        self.__save__answer__()
        message = message + self.__new__word__message__()
        return message

    def __example_message__(self):
        # Если примеры кончились
        if len(KeysWords[self.current_user.id]['examples']) == 0:
            return [TextMessage(
                text='Примеры кончились (sad)')] + self.__hints_message__()

        # Выбираем случайный пример
        message_text = random.choice(KeysWords[self.current_user.id]['examples'])

        # Удаляем полученный пример
        KeysWords[self.current_user.id]['examples'].remove(message_text)

        # Возвращаем сообщение с примеров
        return [TextMessage(
            text=message_text)] + self.__hints_message__()

    def __save__answer__(self):
        # Добавляем ответ в базу
        self.session = Session()
        user_answer = bot_users_answers(id_user=self.current_user.id,
                                        id_word=KeysWords[self.current_user.id]['right_answer'].id,
                                        is_right=KeysWords[self.current_user.id]['is_right'],
                                        answer_date=self.session.query(func.current_timestamp(type_=types.DateTime)))
        self.session.add(user_answer)
        self.session.commit()

    def __get__keys_start__(self):
        if self.current_user.id not in KeysStart:
            KeysStart[self.current_user.id] = json.load(open('start_keyboard.json', encoding='utf-8'))

        if not self.current_user.is_notice_need:
            KeysStart[self.current_user.id]['Buttons'][1]['Text'] = \
                KeysStart[self.current_user.id]['Buttons'][1]['Text'].replace('ОТКАЗАТЬСЯ ОТ НАПОМИНАНИЙ',
                                                                              'ВКЛЮЧИТЬ НАПОМИНАНИЯ')
        else:
            KeysStart[self.current_user.id]['Buttons'][1]['Text'] = \
                KeysStart[self.current_user.id]['Buttons'][1]['Text'].replace('ВКЛЮЧИТЬ НАПОМИНАНИЯ',
                                                                              'ОТКАЗАТЬСЯ ОТ НАПОМИНАНИЙ')

        return KeysStart[self.current_user.id]

    def __get__aside__(self):
        if self.session.query(bot_users_answers).count() % 10 == 0 or self.current_user.id not in KeysWords:
            keyboard = self.__get__keys_start__()
        else:
            keyboard = KeysWords[self.current_user.id]['keyboard']
        print(self.current_user)
        if self.current_user.notice_time is None:
            self.current_user.notice_time = timedelta(minutes=30)
        self.current_user.notice_time = self.current_user.notice_time + timedelta(minutes=30)
        self.session.add(self.current_user)
        self.session.commit()
        print(self.current_user)
        return [TextMessage(text="Будет сделано (eyes)"),
                KeyboardMessage(keyboard=keyboard)]

    def __get__disable__(self):

        self.current_user.is_notice_need = not self.current_user.is_notice_need
        keyboard = self.__get__keys_start__()

        if not self.current_user.is_notice_need:
            message = \
                [TextMessage(text="Включить напоминание можно будет в конце каждого раунда"),
                 KeyboardMessage(keyboard=keyboard)]
        else:
            message = \
                [TextMessage(text="Мы обязательно вам напомним!"),
                 KeyboardMessage(keyboard=keyboard)]
        self.session.commit()
        return message

    def __get__tts__(self):
        return [
            TextMessage(text='Транскрипция этого слова - ' + KeysWords[self.current_user.id]['right_transcription']),
            TextMessage(text='Загрузка воспроизведения слова может занять какое-то время. Пожалуйста ожидайте.'),
            FileMessage(
                media='https://translate.google.com.vn/translate_tts?ie=UTF-8&q={}&tl=en&client=tw-ob'.format(
                    KeysWords[self.current_user.id]['right_answer'].word),
                file_name='{}.mp3'.format(KeysWords[self.current_user.id]['right_answer'].word),
                size=5120
            )
            ] + self.__hints_message__()

    def __hints_message__(self):
        keyboard = json.load(open('hint_keyboard.json', encoding='utf-8'))
        return [KeyboardMessage(keyboard=keyboard), ]

    def __backhints_message__(self):
        return [KeyboardMessage(keyboard=KeysWords[self.current_user.id]['keyboard'])]

    def __sym_message__(self):
        # Если примеры кончились
        if len(KeysWords[self.current_user.id]['syms']) == 0:
            return [TextMessage(
                text='Синонимы кончились (sad)')] + self.__hints_message__()

        # Выбираем случайный пример
        message_text = random.choice(KeysWords[self.current_user.id]['syms'])

        # Удаляем полученный пример
        KeysWords[self.current_user.id]['syms'].remove(message_text)

        # Возвращаем сообщение с примеров
        return [TextMessage(
            text=message_text)
            ] + self.__hints_message__()
