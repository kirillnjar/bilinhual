import sqlite3

import json


class sqlite_database:

    def __init__(self, database_name):
        self.conn = sqlite3.connect(database_name)
        self.conn.row_factory = sqlite3.Row

    def close(self):
        self.conn.close()

    def add_user(self, user):
        query = """
            INSERT INTO bot_USERS(VIBER_ID, NAME) 
            SELECT :id, :name 
            WHERE NOT EXISTS(SELECT 1 FROM bot_USERS WHERE VIBER_ID = :id AND NAME = :name);
        """
        try:
            self.conn.execute(query, ({'id': user.id, 'name': user.name}))
            self.conn.commit()
        except:
            print('Ошибка добавления нового пользователя')
            self.conn.rollback()

    def find_user(self, viber_id):
        query = """
                SELECT * FROM bot_USERS WHERE VIBER_ID = ?
            """
        res_value = None
        try:
            res_value = self.conn.execute(query, (viber_id,)).fetchone()
            self.conn.commit()
        except:
            print('Ошибка поиска нового опльзователя')
            self.conn.rollback()
        return res_value['ID']

    def get_user_count(self):
        query = 'SELECT COUNT(*) FROM bot_USERS'
        return self.conn.execute(query).fetchone()[0]

    def print_all_user(self):
        query = 'SELECT * FROM bot_USERS'
        for user in self.conn.execute(query):
            print(tuple(user))

    def get_words_for_user(self):
        query_words = """
                SELECT ID, WORD, TRANSLATION FROM bot_WORDS
                WHERE _ROWID_ >= (abs(random()) % (SELECT max(_ROWID_) FROM bot_WORDS))
                LIMIT 1;
        """
        query_examples = """
                SELECT SENTENCE FROM bot_EXAMPLES
                WHERE ID_WORD = ?;
        """
        words = list()
        for i in range(0, 4):
            word = self.conn.execute(query_words).fetchone()
            examples = []
            for example in self.conn.execute(query_examples, (word['ID'],)).fetchall():
                examples.append(example['SENTENCE'])
            words.append({'word': word['WORD'], 'translation': word['TRANSLATION'], 'examples': examples})
            print( words[i])
        return words




    def __enter__(self):
        print('we in enter')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('exit')
        self.close()