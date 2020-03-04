from database import sqlite_database
from game_round import game_round


class user:
    def get_id_viber(self):
        return self.__id__viber

    def clear(self):
        self.__round.clear()

    def get_name(self):
        return self.__name

    def next_round(self):
        return self.__round.next_round()

    def get_current_word(self):
        return self.__round.get_current_word()

    def get_current_keyboard(self):
        return self.__round.get_current_keyboard()

    def get_score(self):
        return self.game_point

    def set_score(self, game_point):
        self.game_point += game_point

    def __init__(self, raw_user):
        with sqlite_database('bot.db') as db:
            db.add_user(user=raw_user)
            self.__id__db = db.find_user(raw_user.id)
        self.__id__viber = raw_user.id
        self.__name = raw_user.name
        self.__round = game_round()
        self.game_point = 0
        self.__current_word = None



