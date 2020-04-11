from sqlalchemy import create_engine, types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import psycopg2
Base = declarative_base()
Engine = create_engine('postgres://cageownxibalfw:bbf1748f0608f7adea19d444f3fe1ac24dfdcd6f967b0485cd255338e6be4a8e@ec2-3-234-109-123.compute-1.amazonaws.com:5432/d2i0cse07c5nv9')
Session = scoped_session(sessionmaker(bind=Engine))
#session = Session()


from sqlalchemy import ForeignKey, Column, Integer, String, Boolean, DateTime


class bot_users(Base):
    __tablename__ = 'bot_users'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    viber_id = Column(name='viber_id', type_=String(length=20), unique=True, nullable=False)
    name = Column(name='name', type_=String(length=40), nullable=False)
    is_notice_need = Column(name='is_notice_need', type_=Boolean, nullable=False, default=1)
    notice_time = Column(name='notice_time', type_=types.Interval)

    bot_users_answers = relationship("bot_users_answers", back_populates="bot_users")

    def __repr__(self):
        return "<User(id='{}, viber id={}, name={}, notice_time={}, is_notice_need ={})>".format(self.id,
                                                                                                        self.viber_id,
                                                                                                        self.name,
                                                                                                 self.notice_time,
                                                                                                 self.is_notice_need)

class bot_words(Base):
    __tablename__ = 'bot_words'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    word = Column(name='word', type_=String, unique=True, nullable=False)
    bot_users_answers = relationship("bot_users_answers", back_populates="bot_words")

    def __repr__(self):
            return "<Words(id={}, word={})>".format(self.id, self.word)

class bot_users_answers(Base):
    __tablename__ = 'bot_users_answers'

    id = Column(name='id', type_=Integer, primary_key=True, autoincrement=True, unique=True, nullable=False)
    id_user = Column(ForeignKey('bot_users.id'), name='id_user', type_=Integer, nullable=False)
    id_word = Column(ForeignKey('bot_words.id'), name='id_word', type_=Integer, nullable=False)
    is_right = Column(name='is_right', type_=Boolean)
    answer_date = Column(name='answer_date', type_=DateTime)

    bot_users = relationship("bot_users", back_populates="bot_users_answers")
    bot_words = relationship("bot_words", back_populates="bot_users_answers")
    def __repr__(self):
        return "<Answers(id={}, id_user={}, id_word={}, is_right={}, answer_date={})>"\
            .format(self.id, self.id_user, self.id_word, self.is_right, self.answer_date)




