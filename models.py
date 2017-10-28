from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy import (Column, Integer, Boolean, String, Text,
                        DateTime)


Base = declarative_base()


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

    hw_id = Column('hw_id', Integer,
                   primary_key=True, nullable=False)
    owner = Column('chat_id', Integer, nullable=False)
    class_id = Column('class', String(length=50))
    assignment = Column('assignment', Text, nullable=False)
    due_date = Column('due_date', DateTime(timezone=True))
    complete = Column('complete', Boolean, default=False)
    time_created = Column(DateTime(timezone=True),
                          server_default=func.statement_timestamp(),
                          nullable=False)
    time_updated = Column(DateTime(timezone=True),
                          onupdate=func.clock_timestamp())
