from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

import settings

from models import *

Session = sessionmaker()
"""
Session must be bound to an engine when one is declared
Instance variables of session are used to query the database 
and commit changes
"""


class Database:
    """Data Access Abstraction layer"""

    def __init__(self):
        """
        Initializes a connection with the database
        Makes sure the database matches our schema (doesn't do migrations yet) 2/5/16
        Defines any missing tables
        Starts a session
        """
        engine = self.connect()
        self.initialize_schema(engine)
        Session.configure(bind=engine)
        self.session = Session()

    def connect(self):
        """
        The engine is what sends SQL requests to the database api (DBAPI)
        The connection string is hard-coded right now. If the database later
        contains sensitive info we need to find a way to secure the password
        :return:
        """
        return create_engine(URL(**settings.DATABASE), echo=True)

    def initialize_schema(self, engine):
        Base.metadata.create_all(engine)

    def add_new_assignment(self, student, homework):
        new_homework = Assignment(owner=student, assignment=homework)
        self.session.add(new_homework)
        self.session.commit()
        self.session.close()

    def complete_student_assignment(self, homework):
        homework.complete = True
        self.session.commit()
        self.session.close()

    def due_assignments(self, student):
        open_assignments = (self.session.query(Assignment).filter(
            Assignment.owner == student).filter(
            Assignment.complete.is_(False)).all())
        self.session.close()
        return open_assignments

    def process_homework(self, student, homework):
        match = (self.session.query(Assignment).filter(
            Assignment.owner == student,
            Assignment.assignment == homework).one_or_none())
        if match:
            self.complete_student_assignment(match)
            return True
        else:
            self.add_new_assignment(student, homework)
            return None

    def get_all_assignments(self, student):
        all_assignments = (self.session.query(Assignment).filter(
            Assignment.owner == student))
        self.session.close()
        return all_assignments
