import json
import random

from database import sqlite_database


class game_round:
    __KeysTask = json.load(open('word_keyboard.json', encoding='utf-8'))
    __current_word = dict()

    def __init__(self):
        self.__words = dict()

    def next_round(self):
        with sqlite_database('bot.db') as db:
            self.english_words = db.get_words_for_user()
        if len(self.__words) == 10:
            return False
        # Выбираем правильный ответ
        new_word = self.__get_new_word()
        # Добавляем основное слово к истории слов
        self.__words[len(self.__words)] = new_word

        # Неправильные ответы
        wrong_answers = self.__get_wrong_answers(new_word['word'])
        for i in range(0, len(wrong_answers)):
            new_word['wrong_answer' + str(i)] = wrong_answers[i]['translation']
        # Сохраняем результаты
        self.__current_word = new_word
        self.__gen_keyboard()
        return True

    def get_current_keyboard(self):
        return self.__KeysTask

    def get_current_word(self):
        return self.__current_word

    def __gen_keyboard(self):
        shuffled = list(range(1, 5))
        random.shuffle(shuffled)
        self.__KeysTask['Buttons'][shuffled[0] - 1]['Text'] = self.__current_word['translation']
        self.__KeysTask['Buttons'][shuffled[1] - 1]['Text'] = self.__current_word['wrong_answer0']
        self.__KeysTask['Buttons'][shuffled[2] - 1]['Text'] = self.__current_word['wrong_answer1']
        self.__KeysTask['Buttons'][shuffled[3] - 1]['Text'] = self.__current_word['wrong_answer2']
        return self.__KeysTask

    def clear(self):
        self.__words.clear()

    def __get_new_word(self):
        word = random.choice(self.english_words)
        self.english_words.remove(word)
        return word

    def __get_wrong_answers(self, right_word):
        wrong_answers = dict()

        for i in range(0, 3):
            wrong_answers[i] = self.english_words[i]
        return wrong_answers
