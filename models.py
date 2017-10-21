from sqlalchemy import create_engine, Column, Integer, Boolean, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL

import settings

Base = declarative_base()


def db_connect():
    return create_engine(URL(**settings.DATABASE), echo=True)


def map_tables(engine):
    Base.metadata.create_all(engine)


class User(Base):
    __tablename__ = 'users'

    id = Column('id', Integer,
                primary_key=True, autoincrement=False, nullable=False)
    is_bot = Column('is_bot', Boolean, nullable=False)
    first_name = Column('first_name', String(length=50))
    last_name = Column('last_name', String(length=50))
    username = Column('username', String(length=50))
    language_code = Column('language_code', String(length=35))

    def __repr__(self):
        return 'User:{} - {}, {}'.format(self.username,
                                         self.last_name,
                                         self.first_name)


class Assignment(Base):
    __tablename__ = 'assignments'

    assignment = Column('assignment', Text,
                        primary_key=True, nullable=False)
