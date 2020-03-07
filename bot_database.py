from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import psycopg2
Base = declarative_base()
Engine = create_engine('postgres://qapondokdkboga:4f7270b7d921454f8950f9ceaaf72dea525ec869544e916fca3898b27ecbac28@ec2-46-137-177-160.eu-west-1.compute.amazonaws.com:5432/d5qbacliastonp', )
Session = scoped_session(sessionmaker(bind=Engine))
#session = Session()


from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime


class bot_users(Base):
    __tablename__ = 'bot_users'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    viber_id = Column(name='viber_id', type_=String(length=20), unique=True, nullable=False)
    name = Column(name='name', type_=String(length=40), nullable=False)
    repeats_number = Column(name='repeats_number', type_=Integer)
    is_difficulty_need = Column(name='is_difficulty_need', type_=Boolean, nullable=False, default=1)

    bot_users_answers = relationship("bot_users_answers", back_populates="bot_users")

    def __repr__(self):
        return "<User(id='{}, viber id={}, name={}, repeats number={}, is difficulty need ={})>".format(self.id,
                                                                                                        self.viber_id,
                                                                                                        self.name,
                                                                                                        self.repeats_number,
                                                                                                        self.is_difficulty_need)


class bot_words(Base):
    __tablename__ = 'bot_words'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    word = Column(name='word', type_=String, unique=True, nullable=False)
    translation = Column(name='translation', type_=String, nullable=False)
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
    __tablename__ = 'bot_examples'

    id = Column(name='ID', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_word = Column(ForeignKey('bot_words.id'), name='id_word', type_=Integer, nullable=False)
    sentence = Column(name='sentence', type_=String, nullable=False)
    bot_words = relationship("bot_words", back_populates="bot_examples")

    def __repr__(self):
        return "<Examples(id={}, word={}, sentence={})>".format(self.id, self.bot_words,
                                                                self.sentence)


class bot_users_answers(Base):
    __tablename__ = 'bot_users_answers'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_user = Column(ForeignKey('bot_users.id'), name='id_user', type_=Integer, nullable=False)
    id_word = Column(ForeignKey('bot_words.id'), name='id_word', type_=Integer, nullable=False)
    is_right = Column(name='is_right', type_=Boolean)
    answer_date = Column(name='answer_date', type_=DateTime)
    id_difficulty = Column(ForeignKey('bot_difficulty.id'), name='id_difficulty', type_=Integer, nullable=False)

    bot_users = relationship("bot_users", back_populates="bot_users_answers")
    bot_words = relationship("bot_words", back_populates="bot_users_answers")
    bot_difficulty = relationship("bot_difficulty", back_populates="bot_users_answers")
    def __repr__(self):
        return "<Answers(id={}, word={}, sentence={}, id_word={}, is_right={}, is_right={}, answer_date={}, id_difficulty={})>"\
            .format(self.id, self.id_user, self.id_word, self.is_right, self.answer_date, self.id_difficulty)

class bot_difficulty(Base):
    __tablename__ = 'bot_difficulty'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    interpretation = Column(name='interpretation', type_=String, nullable=False)

    bot_users_answers = relationship("bot_users_answers", back_populates="bot_difficulty")
    def __repr__(self):
        return "<Difficulty(id={}, interpretation={})>".format(self.id, self.interpretation)



