from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

Base = declarative_base()
Engine = create_engine('sqlite:///bot.db', echo=False)
Session = scoped_session(sessionmaker(bind=Engine))
#session = Session()


from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime


class bot_users(Base):
    __tablename__ = 'bot_USERS'

    id = Column(name='ID', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    viber_id = Column(name='VIBER_ID', type_=String(length=20), unique=True, nullable=False)
    name = Column(name='NAME', type_=String(length=40), nullable=False)
    repeats_number = Column(name='REPEATS_NUMBER', type_=Integer)
    is_difficulty_need = Column(name='IS_DIFFICULTY_NEED', type_=Boolean, nullable=False, default=1)

    bot_users_answers = relationship("bot_users_answers", back_populates="bot_users")

    def __repr__(self):
        return "<User(id='{}, viber id={}, name={}, repeats number={}, is difficulty need ={})>".format(self.id,
                                                                                                        self.viber_id,
                                                                                                        self.name,
                                                                                                        self.repeats_number,
                                                                                                        self.is_difficulty_need)


class bot_words(Base):
    __tablename__ = 'bot_WORDS'

    id = Column(name='ID', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    word = Column(name='WORD', type_=String, unique=True, nullable=False)
    translation = Column(name='TRANSLATION', type_=String, nullable=False)
    bot_examples = relationship("bot_examples", back_populates="bot_words")
    bot_users_answers = relationship("bot_users_answers", back_populates="bot_words")

    def __repr__(self):
        if len(self.bot_examples) != 0:
            sentences = list()
            for i in range(0, len(self.bot_examples)):
                sentences.append(self.bot_examples[i].sentence)
            return "<Words(id={}, word={}, translation={}, examples={})>".format(self.id, self.word,
                                                                                 self.translation, sentences)
        else:
            return "<Words(id={}, word={}, translation={}, examples={})>".format(self.id, self.word,
                                                                                 self.translation, self.bot_examples)


class bot_examples(Base):
    __tablename__ = 'bot_EXAMPLES'

    id = Column(name='ID', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_word = Column(ForeignKey('bot_WORDS.ID'), name='ID_WORD', type_=Integer, nullable=False)
    sentence = Column(name='SENTENCE', type_=String, nullable=False)
    bot_words = relationship("bot_words", back_populates="bot_examples")

    def __repr__(self):
        return "<Examples(id={}, word={}, sentence={})>".format(self.id, self.bot_words,
                                                                self.sentence)


class bot_users_answers(Base):
    __tablename__ = 'bot_USERS_ANSWERS'

    id = Column(name='ID', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_user = Column(ForeignKey('bot_USERS.ID'), name='ID_USER', type_=Integer, nullable=False)
    id_word = Column(ForeignKey('bot_WORDS.ID'), name='ID_WORD', type_=Integer, nullable=False)
    is_right = Column(name='IS_RIGHT', type_=Boolean)
    answer_date = Column(name='ANSWER_DATE', type_=DateTime)
    id_difficulty = Column(ForeignKey('bot_DIFFICULTY.ID'), name='ID_DIFFICULTY', type_=Integer, nullable=False)

    bot_users = relationship("bot_users", back_populates="bot_users_answers")
    bot_words = relationship("bot_words", back_populates="bot_users_answers")
    bot_difficulty = relationship("bot_difficulty", back_populates="bot_users_answers")
    def __repr__(self):
        return "<Answers(id={}, word={}, sentence={}, id_word={}, is_right={}, is_right={}, answer_date={}, id_difficulty={})>"\
            .format(self.id, self.id_user, self.id_word, self.is_right, self.answer_date, self.id_difficulty)

class bot_difficulty(Base):
    __tablename__ = 'bot_DIFFICULTY'

    id = Column(name='ID', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    interpretation = Column(name='INTERPRETATION', type_=String, nullable=False)

    bot_users_answers = relationship("bot_users_answers", back_populates="bot_difficulty")
    def __repr__(self):
        return "<Difficulty(id={}, interpretation={})>".format(self.id, self.interpretation)
        pass



