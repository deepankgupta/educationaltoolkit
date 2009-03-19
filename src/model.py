#!/usr/bin/env python
#
#   model.py
#   Educational toolkit
#

"""Model objects"""

from shutil import copyfileobj
from tempfile import TemporaryFile
from urllib2 import urlopen

__author__ = "Ross Light"
__date__ = "April 2, 2008"
__docformat__ = "JavaDoc"
__all__ = ['get_sugar_name',
           'Blank',
           'QuestionText',
           'Image',
           'ImagePage',
           'Test',
           'Question',
           'TrueFalseQuestion',
           'MultipleChoiceQuestion',
           'ShortAnswerQuestion',
           'MatchingQuestion',
           'FlashCard',
           'AnswerList',
           'Answer',
           'Results',]

def get_sugar_name():
    """
    Obtains the name of the current user from the Sugar profile.
    
    @return The Sugar nickname
    @returntype unicode
    """
    from sugar import profile
    return profile.get_nick_name()

class Blank(object):
    """
    Renders a blank (usually an underline) in the Question's text.
    
    @ivar length The length of the blank
    @type length int
    """
    def __init__(self, length=10):
        self.length = length
    
    def __repr__(self):
        return "Blank(%r)" % self.length
    
    def __str__(self):
        return unicode(self).encode()
    
    def __unicode__(self):
        return u"_" * self.length

class QuestionText(object):
    """
    Renders a blank (usually an underline) in the Question's text.
    
    <code>QuestionText</code> objects can be used sequence-like to access its
    children.
    
    @ivar content The content of the tree
    @type content list
    """
    def __init__(self, content=None):
        if content is None:
            self.content = []
        else:
            self.content = list(content)
    
    # STRING REPRESENTATION #
    
    def __repr__(self):
        return "QuestionText(%r)" % (self.content)
    
    def __str__(self):
        return unicode(self).encode()
    
    def __unicode__(self):
        return u''.join(unicode(child) for child in self.content)
    
    # PUBLIC METHODS #
    
    def append(self, item):
        self.content.append(item)
    
    def insert(self, index, item):
        self.content.insert(index, item)
    
    def remove(self, item):
        self.content.remove(item)
    
    # SEQUENCE ACCESS #
    
    def __nonzero__(self):
        return len(self.content) != 0
    
    def __iter__(self):
        return iter(self.content)
    
    def __len__(self):
        return len(self.content)
    
    def __getitem__(self, item):
        return self.content[item]
    
    def __setitem__(self, item, value):
        self.content[item] = value
    
    def __delitem__(self, item):
        del self.content[item]
    
    def __contains__(self, item):
        return item in self.content

class Image(object):
    """
    An image for a question.
    
    @ivar mime_type The suggested MIME type of the image
    @type str
    @ivar title The human-readable description of the image
    @type title unicode
    @ivar position The horizontal alignment (i.e. left, center, or right)
    @type position str
    @ivar link A URL to the image.  May be <code>None</code> if data was
               given (via {@link set_data set_data}).
    @type link str
    @ivar size The width and height of the image (in pixels)
    @type size tuple of int
    """
    def __init__(self, mime_type, title=None, size=None, position='left'):
        assert position in ('left', 'center', 'right')
        self.mime_type = mime_type
        self.title = title
        self.link = None
        self._data_file = None
        self.size = size
        self.position = position
    
    def get_source(self):
        """
        Retrieves the image's source file.
        
        If this image is fetched from HTTP, then the
        {@link mime_type MIME type} will be updated to reflect the server's
        reported MIME type.
        
        @raises ValueError if the image does not yet have a source
        @return The image's source
        @returntype file-like object
        """
        if self.link is not None:
            f = urlopen(self.link)
            new_type = f.headers.get('Content-Type', self.mime_type)
            new_type = new_type.split(';')[0]
            self.mime_type = new_type
            return f
        elif self._data_file is not None:
            self._data_file.seek(0)
            return self._data_file
        else:
            raise ValueError("This image has not been given a source")
    
    def set_link(self, link):
        """
        Sets the image's source to an external URL.
        
        @param link The image's location
        @type link str
        """
        self.link = link
    
    def set_data(self, raw_data):
        """
        Sets the image's source to binary data.
        
        @param raw_data The data source
        @type raw_data str or file-link object
        """
        if self._data_file is None:
            self._data_file = TemporaryFile()
        self._data_file.seek(0)
        self._data_file.truncate()
        if isinstance(raw_data, basestring):
            self._data_file.write(raw_data)
        else:
            copyfileobj(raw_data, self._data_file)
        self._data_file.flush()
    
    def __repr__(self):
        return "model.Image(%r, %r, %r, %r)" % (self.mime_type, self.title,
                                                self.size, self.position)
    
    def __str__(self):
        if self.link:
            return "Image \"%s\" src='%s'" % (self.title, self.link)
        else:
            return "Image \"%s\" src=<data>" % (self.title)

class ImagePage(object):
    """
    A page of images.
    
    @ivar images The list of images to show on the page
    @type images list of Image
    @ivar title The human-readable description of the image page
    @type title unicode
    """
    def __init__(self, images=None, title=None):
        if images is None:
            self.images = []
        else:
            self.images = list(images)
        self.title = title

class Test(object):
    """
    An individual test that contains questions.
    
    @ivar id A unique identifier for the test
    @type id str
    @ivar instructions A set of instructions given at the start of the test
    @type instructions unicode
    @ivar questions All of the questions on the test in order of appearance
    @type questions list of {@link Question Question}
    """
    def __init__(self, id, instructions=None):
        self.id = id
        self.questions = []
        self.instructions = instructions
    
    def add_question(self, question):
        """
        Add a question to the end of the test.
        
        @param question The question to add
        @type question {@link Question Question}
        """
        self.questions.append(question)

class Question(object):
    """
    Base class for a question on a test.
    
    @ivar id A unique identifier for the question
    @type id str
    @ivar credits The number of credits the question is worth if correctly
                  answered
    @type credits int
    @ivar images Images and image pages associated with the question
    @type images list
    @ivar text The question being asked
    @type text {@link QuestionText QuestionText}
    @ivar difficulty The difficulty of finding the question's answer
    @type difficulty unicode
    @ivar average_time The average amount of time (in seconds) that it takes to 
                       answer the question
    @type average_time float
    @ivar stipulated_time The amount of time (in seconds) allocated to
                          answering the question
    @type stipulated_time float
    @ivar advice A short amount of text, displayed along with the question,
                 that helps the student.  If given, this should get the student
                 in the general direction of the answer.
    @type advice unicode
    @ivar hint A hint that the student can view.
    @type hint unicode
    """
    def __init__(self, qid, text, credits, difficulty=u"Easy"):
        self.id = qid
        self.credits = credits
        self.images = []
        self.text = text
        self.difficulty = difficulty
        self.average_time = None
        self.stipulated_time = None
        self.advice = None
        self.hint = None
    
    def answer(self, answer, time, hint=False):
        """
        Creates an {@link Answer Answer object} for the question.
        
        @param answer The student-given answer for the question
        @type answer unicode
        @param time The amount of time it took to answer the question
        @type time float
        @param hint Whether the student viewed the hint
        @type hint bool
        @return An answer for the question
        @returntype {@link Answer Answer}
        """
        return Answer(self.id, answer, time, hint)

class TrueFalseQuestion(Question):
    """A simple true/false question."""

class MultipleChoiceQuestion(Question):
    """
    A multiple choice question.
    
    @ivar choices A list of (choice_name, choice_text) tuples
    @type choices list of tuple
    """
    def __init__(self, qid, text, choices, *args, **kw):
        super(MultipleChoiceQuestion, self).__init__(qid, text, *args, **kw)
        self.choices = choices

class ShortAnswerQuestion(Question):
    """
    A question answered by the student inputting text.

    @ivar expected_length The expected string length of the answer
    @type expected_length int
    """
    def __init__(self, qid, text, expected_length, *args, **kw):
        super(ShortAnswerQuestion, self).__init__(qid, text, *args, **kw)
        self.expected_length = expected_length

class MatchingQuestion(Question):
    """
    A question where several key phrases are matched with answer phrases.
    
    Each key phrase can only have one answer phrase, but multiple key phrases
    can have the same answer phrase.
    
    @ivar keys The phrases to be matched up
    @type keys list of unicode
    @ivar answers The answer phrases to match to
    @type answers list of unicode
    """
    def __init__(self, qid, text, keys, answers, *args, **kw):
        super(MatchingQuestion, self).__init__(qid, text, *args, **kw)
        self.keys = list(keys)
        self.answers = list(answers)
    
    def answer(self, answer, *args, **kw):
        """
        Creates an {@link Answer Answer object} for the question.
        
        The answers for this question must be given as a dictionary.  Each key
        is the index of a key, and each value is the index of an answer.
        
        @param answer The student-given answer for the question
        @type answer dict
        @param time The amount of time it took to answer the question
        @type time float
        @param hint Whether the student viewed the hint
        @type hint bool
        @return An answer for the question
        @returntype {@link Answer Answer}
        """
        items = ('%s:%s' % (key, value) for key, value in answer.iteritems())
        answer = ','.join(items)
        return super(MatchingQuestion, self).answer(answer, *args, **kw)

class FlashCard(Question):
    """
    A question/answer self-testing device.
    
    @ivar back_text The content of the "back" of the card
    @type back_text unicode
    """
    def __init__(self, qid, text, back_text, *args, **kw):
        super(FlashCard, self).__init__(qid, text, *args, **kw)
        self.back_text = back_text
    
    def answer(self, *args, **kw):
        raise TypeError("Flashcards don't support being answered")

class Answer(object):
    """
    An student-created answer for a {@link Question Question}.
    
    @ivar id The question ID the answer is for
    @type id str
    @ivar answer The text of the answer
    @type answer unicode
    @ivar time_taken The amount of time (in seconds) taken to answer the
                     question
    @type time_taken float
    @ivar hint_used Whether the student viewed the hint
    @type hint_used bool
    """
    def __init__(self, qid, answer, time_taken, hint_used=False):
        assert time_taken > 0
        self.id = qid
        self.answer = answer
        self.time_taken = time_taken
        self.hint_used = hint_used

class AnswerList(object):
    """
    A list of {@link Answer answers}.
    
    @ivar answers All the answers contained by the list
    @type answers list of {@link Answer Answer objects}
    @ivar student_name The name of the student answering
    @type student_name unicode
    """
    def __init__(self, answers=None, name=None):
        self.answers = list(answers) if answers is not None else []
        self.student_name = unicode(name) if name is not None else None
    
    # Operator overloading
    # We want to actually be able to use this as a list
    
    def __len__(self):
        return len(self.answers)
    
    def __iter__(self):
        return iter(self.answers)
    
    def __getitem__(self, item):
        return self.answers[item] # note that this handles slices, too
    
    def __contains__(self, item):
        if isinstance(item, basestring):
            # Searching for answer ID
            return bool(self.get_answer(item) is not None)
        else:
            return item in self.answers
    
    def get_answer(self, qid):
        """
        Finds the answer with a given ID.
        
        @param qid The answer's ID
        @type qid str
        @raises KeyError if there is no answer present with the given ID
        @return The answer with the requested ID
        @returntype {@link Answer Answer}
        """
        for answer in self:
            if answer.id == qid:
                return answer
        else:
            raise KeyError(qid)

class Results(object):
    """
    Results from a set of {@link Answer Answers}.
    
    @ivar correct The IDs of the {@link Question questions} correct
    @type correct list of str
    @ivar incorrect The IDs of the {@link Question questions} incorrect
    @type incorrect list of str
    @ivar pending The IDs of the {@link Question questions} needing human
                  grading
    @type pending list of str
    """
    @classmethod
    def collect(cls, key, answers):
        """
        Collect the results from an answer set.
        
        @param key The machine gradeable answer key
        @type key dict/list of {@link Answer Answers}
        @param answers The student answers
        @type answers list of {@link Answer Answers}
        @return A set of results from the grading
        @returntype {@link Results Results}
        """
        # Make the key usable
        if not isinstance(key, dict):
            new_key = {}
            for answer in key:
                new_key[answer.id] = answer
            key = new_key
        # Grade tirelessly!
        correct = []
        incorrect = []
        pending = []
        for student_answer in answers:
            try:
                correct_answer = key[student_answer.id]
            except KeyError:
                # Not found in answer key, mark for teacher grading
                pending.append(student_answer.id)
            else:
                # Answer key has an answer, let's check it
                if student_answer.answer == correct_answer.answer:
                    correct.append(student_answer.id)
                else:
                    incorrect.append(student_answer.id)
        # Collect and return results
        return cls(correct, incorrect, pending)
    
    def __init__(self, correct, incorrect, pending=None):
        self.correct = list(correct) if correct is not None else None
        self.incorrect = list(incorrect) if incorrect is not None else None
        self.pending = list(pending) if pending is not None else None
    
    def grade(self, qid, correct):
        """
        Grade a pending answer.
        
        @param qid The question ID of the answer
        @type qid str
        @param correct Whether the answer was correct
        @type correct bool
        @raises ValueError if the answer is not pending
        """
        if qid not in self.pending:
            raise ValueError("Question ID not in pending: %r" % qid)
        # Grade
        # Notice we're making copies so that there is no code modification for
        # PersistentResults
        pending = list(self.pending)
        answer_id = pending.pop(pending.index(qid))
        self.pending = pending
        # Add to appropriate list
        if correct:
            self.correct = list(self.correct) + [answer_id]
        else:
            self.incorrect = list(self.incorrect) + [answer_id]
