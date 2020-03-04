from viberbot.api.messages import PictureMessage, KeyboardMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
import random

# Бот
import json

from User import user
from database import sqlite_database


KeysStart = json.load(open('start_keyboard.json', encoding='utf-8'))


class viber_bot:
    __unknown_messages_collection = ['Не понимаю о чем ты говоришь', 'Данная информация не может быть мною распознана',
                                     'Критическая ошибка в программе. Соощение ошибки: "Убить всех человеков"']
    __current_user = None
    __response_message = list()

    # получение ботом запроса
    def set_request(self, viber_request):
        if isinstance(viber_request, ViberSubscribedRequest):
            self.__response_message = self.__hello__message__(viber_request.user.name)
            self.__current_user = user(viber_request.user)
        elif isinstance(viber_request, ViberMessageRequest):
            message = viber_request.message
            self.__current_user = user(viber_request.sender)
            print(viber_request.message)
            if isinstance(message, TextMessage):
                word = viber_request.message.text
                if word[0] == '/':
                    word = word.replace('/', '')
                    if word.split(' ')[0].lower() == 'help':
                        self.__response_message = self.__help__message__()
                        pass
                    elif word.split(' ')[0].lower() == 'start':
                        self.__response_message = self.__new__word__message__()
                        pass
                    elif word.split(' ')[0].lower() == 'example':
                        self.__response_message = self.__example_message__()
                        pass
                    else:
                        self.__response_message = self.__unknown__message__()
                        pass
                elif int(word) in [1, 2, 3, 4]:
                    self.__response_message = self.__answer_message__(word.split(' ')[0].lower())
                else:
                    self.__response_message = self.__unknown__message__()
            elif isinstance(message, PictureMessage):
                self.__response_message = TextMessage(text='Очень красиво, ' + viber_request.sender.name)
        else:
            self.__response_message = None

    # ответ бота
    def get_response(self):
        return self.__response_message

    def __answer_message__(self, word):
        print(self.__current_user.get_current_keyboard())
        print(self.__current_user.get_current_word()['translation'])
        print(word)
        if self.__current_user.get_current_keyboard()['Buttons'][int(word) - 1]['Text'] == \
                self.__current_user.get_current_word()['translation']:
            self.__current_user.set_score(1)
            message = [TextMessage(text='И это правильный ответ! Вы получаете плюс один балл (smiley)')]
            return message + self.__new__word__message__()
        else:
            self.__current_user.set_score(0)
            message = [TextMessage(text='К сожалению вы ошиблись! Баллов не будет, но вы держитесь(ugh)')]
            return message + self.__new__word__message__()

    def __example_message__(self):
        # Если примеры кончились
        if len(self.__current_user.get_current_word()['examples']) == 0:
            return [TextMessage(
                text='Примеры кончились (sad)'),
                KeyboardMessage(keyboard=self.__current_user.get_current_keyboard())]
        # Выбираем случайный пример
        message_text = random.choice(self.__current_user.get_current_word()['examples'])
        # Удаляем полученный пример
        self.__current_user.get_current_word()['examples'].remove(message_text)
        # Возвращаем сообщение с примеров
        return [TextMessage(
            text=message_text),
            KeyboardMessage(keyboard=self.__current_user.get_current_keyboard())]

    # получение ответа на неизвестную команду
    def __unknown__message__(self):
        keyboard = self.__current_user.get_current_keyboard()
        if keyboard is None:
            keyboard = KeysStart

        return [
            TextMessage(text=(
                self.__unknown_messages_collection[random.randint(0, len(self.__unknown_messages_collection) - 1)])),
            KeyboardMessage(keyboard=keyboard)]

    def __new__word__message__(self):
        if not self.__current_user.next_round():
            message = [TextMessage(
                text='Раунд закончился. Ваш результат: ' + str(self.__current_user.get_score()) + ' из 10'),
                       TextMessage(text='Спасибо за игру! (like)')] + self.__help__message__()
            return message
        else:
            return [TextMessage(text='Ваше слово: ' + self.__current_user.get_current_word()['word']),
                    TextMessage(text='Вариатны перевода представлены на клавиатуре'),
                    TextMessage(text='Удачи!(moa)'),
                    KeyboardMessage(keyboard=self.__current_user.get_current_keyboard())]

    def get_user(self):
        return self.__current_user

    def __hello__message__(self, sender_name):
        messages = [PictureMessage(text="Поздравляю тебя с подпиской, " + sender_name,
                                   media='https://pngimage.net/wp-content/uploads/2018/06/%D1%87%D0%B5%D0%BB%D0%BE%D0'
                                         '%B2%D0%B5%D1%87%D0%BA%D0%B8-png-%D0%B4%D0%B5%D0%BD%D1%8C%D0%B3%D0%B8-2.png'),
                    TextMessage(
                        text='Я создан для того, чтобы помогать людям в изуение новых слов на английском языке')]
        return messages + self.__help__message__()

    def __help__message__(self):
        return [TextMessage(text='Чтобы начать изучение - напиши /start'),
                KeyboardMessage(keyboard=KeysStart)]
