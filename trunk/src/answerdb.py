#!/usr/bin/env python
#
#   answerdb.py
#   Educational toolkit
#

"""
Instructor database for student results.
"""

from cStringIO import StringIO
import csv

from sqlalchemy import (Table, Column, MetaData, create_engine,
                        Integer, String, Unicode, ForeignKey)
from sqlalchemy.orm import mapper, relation, sessionmaker, synonym

import model

__author__ = "Ross Light"
__date__ = "April 2, 2008"
__docformat__ = "JavaDoc"
__all__ = ['create_session',
           'TestRecord',
           'PersistentResults',]

create_session = sessionmaker(autoflush=True, transactional=True)

### TABLES ###

metadata = MetaData()
tests_table = Table('tests', metadata,
    Column('test_oid', Integer, primary_key=True),
    Column('test_real_id', String(255), unique=True),
)
results_table = Table('results', metadata,
    Column('result_id', Integer, primary_key=True),
    Column('test_id', Integer, ForeignKey('tests.test_oid')),
    Column('student_name', Unicode(255)),
    Column('correct_list', String(2047)),
    Column('correct_count', Integer),
    Column('incorrect_list', String(2047)),
    Column('incorrect_count', Integer),
    Column('pending_list', String(2047)),
    Column('pending_count', Integer),
)

### CLASSES ###

class TestRecord(object):
    """
    A test in the database.
    
    Mostly used to group results, not actually to store test information.
    
    @ivar real_id The test's ID (same as {@link model.Test.id Test.id})
    @type real_id str
    @ivar results The student results for this test
    @type results list of {@link PersistentResults PersistentResults}
    """
    def __init__(self, real_id):
        self.real_id = real_id

class PersistentResults(model.Results):
    """
    Results from a set of {@link Answer Answers}.
    
    @ivar test The test these results are for
    @type test {@link TestRecord TestRecord}
    @ivar student_name The student's name
    @type student_name unicode
    @ivar correct_count (Read-only) The number of correct questions
    @type correct_count int
    @ivar incorrect_count (Read-only) The number of incorrect questions
    @type incorrect_count int
    @ivar pending_count (Read-only) The number of questions needing human
                        grading
    @type pending_count int
    """
    @staticmethod
    def _parse_list_data(data):
        if data is None:
            return None
        reader = csv.reader(data.splitlines())
        list_data = []
        for (value,) in reader:
            list_data.append(value)
        return tuple(list_data)
    
    @staticmethod
    def _encode_list_data(list_data):
        if list_data is None:
            return None
        fake_file = StringIO()
        writer = csv.writer(fake_file)
        for value in list_data:
            writer.writerow([value])
        del writer
        return fake_file.getvalue()
    
    def _get_correct(self):
        return self._parse_list_data(self._correct_list)
    def _set_correct(self, value):
        self._correct_list = self._encode_list_data(value)
        self._correct_count = len(value) if value is not None else 0
    correct = property(_get_correct, _set_correct)
    @property
    def correct_count(self):
        return self._correct_count
    
    def _get_incorrect(self):
        return self._parse_list_data(self._incorrect_list)
    def _set_incorrect(self, value):
        self._incorrect_list = self._encode_list_data(value)
        self._incorrect_count = len(value) if value is not None else 0
    incorrect = property(_get_incorrect, _set_incorrect)
    @property
    def incorrect_count(self):
        return self._incorrect_count
    
    def _get_pending(self):
        return self._parse_list_data(self._pending_list)
    def _set_pending(self, value):
        self._pending_list = self._encode_list_data(value)
        self._pending_count = len(value) if value is not None else 0
    pending = property(_get_pending, _set_pending)
    @property
    def pending_count(self):
        return self._pending_count

### MAPPERS ###

mapper(TestRecord, tests_table, properties=dict(
    real_id=tests_table.c.test_real_id,
))
mapper(PersistentResults, results_table, properties=dict(
    test=relation(TestRecord, backref='results'),
    _correct_list=results_table.c.correct_list,
    correct=synonym('_correct_list'),
    correct_count=synonym('_correct_count', map_column=True),
    _incorrect_list=results_table.c.incorrect_list,
    incorrect=synonym('_incorrect_list'),
    incorrect_count=synonym('_incorrect_count', map_column=True),
    _pending_list=results_table.c.pending_list,
    pending=synonym('_pending_list'),
    pending_count=synonym('_pending_count', map_column=True),
))
