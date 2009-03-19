#!/usr/bin/env python
#
#   parse.py
#   Educational toolkit
#

"""Parser for test files"""

from base64 import b64decode
from cStringIO import StringIO
from gzip import GzipFile
import os
import sys
from textwrap import dedent
from xml.dom import minidom

import model

__author__ = "Ross Light"
__date__ = "March 25, 2008"
__docformat__ = "JavaDoc"
__all__ = ['TestParser',
           'AnswersParser',
           'parse_test',
           'parse_answers',
           'serialize_answers',]

_bool2xml = {False: u"false", True: u"true"}
_xml2bool = {u"false": False,
             u"0": False,
             u"true": True,
             u"1": True,}

def _get_text(elem, post=True):
    """
    Retrieve text from a DOM node, stripping indents, if asked.
    
    <p>This function does honor the <code>xml:space</code> attribute, and if
    <code>xml:space="preserve"</code> is specified, it takes precendence over
    the <code>post</code> argument.</p>
    
    @param elem The element to get text from
    @type elem DOM element
    @keyword post Whether to strip indents
    @type post bool
    @return The element's text, or <code>None</code> if the element is
            <code>None</code>
    @returntype unicode
    """
    xmlNS = 'http://www.w3.org/XML/1998/namespace'
    if elem is None:
        return None
    text = ''
    for child in elem.childNodes:
        if child.nodeType == minidom.Node.TEXT_NODE:
            text += child.wholeText
    preserve = (elem.hasAttributeNS(xmlNS, 'space') and
                elem.getAttributeNS(xmlNS, 'space') == 'preserve')
    if post and not preserve:
        text = dedent(text)
        if text.startswith('\n'):
            text = text[1:]
            if text.endswith('\n'):
                text = text[:-1]
    return text

def _get_first_child_named(parent, name):
    """
    Finds the first child element with a given name.
    
    @param parent The element to search in
    @type parent DOM element
    @param name The name of the tag to search for
    @type name unicode
    @return The first child with the given tag, or <code>None</code> if not
            found
    @returntype DOM element
    """
    results = parent.getElementsByTagName(name)
    if results:
        return results[0]
    else:
        return None

def _get_child_text(parent, name):
    """
    Obtain the text of the first child element with a given name.
    
    This is equivalent to
    <code>_get_text(_get_first_child_named(parent, name))</code>.
    
    @param parent The element to search in
    @type parent DOM element
    @param name The name of the tag to search for
    @type name unicode
    @return The text of the first child with the given tag, or
            <code>None</code> if not found
    @returntype unicode
    """
    return _get_text(_get_first_child_named(parent, name))

class TestParser(object):
    """
    Parses test XML files.
    
    Generally, this class will not need to be used directly; instead, use
    {@link parse_test parse_test}.
    
    @ivar document The document currently being parsed
    @type document DOM document
    @ivar test The test being constructed
    @type test {@link model.Test Test}
    @see parse_test
    """
    @staticmethod
    def _parse_question_text(elem):
        text = model.QuestionText()
        for node in elem.childNodes:
            if node.nodeType == minidom.Node.ELEMENT_NODE:
                if node.tagName == 'blank':
                    blank_length = node.getAttribute('length')
                    if blank_length is None:
                        blank_length = 10
                    else:
                        blank_length = int(blank_length)
                    text.append(model.Blank(blank_length))
            elif node.nodeType == minidom.Node.TEXT_NODE:
                text.append(node.wholeText)
        return text
    
    def parse(self, doc):
        """
        Parses a test file.
        
        @param doc The XML DOM of the file to parse
        @type doc DOM document
        @return The test that the file represents
        @returntype {@link model.Test Test}
        """
        self.document = doc
        root = doc.documentElement
        test_id = root.getAttribute('id')
        instructions = _get_child_text(root, 'instructions')
        self.test = model.Test(test_id, instructions)
        for node in root.childNodes:
            if node.nodeType == minidom.Node.ELEMENT_NODE:
                name = node.tagName
                if name == 'question':
                    self._handle_question(node)
                else:
                    # TODO: Raise error for undetected element
                    pass
        return self.test
    
    def _handle_question(self, elem):
        """
        Handles a single question element and adds the question to the test.
        
        @param elem The question element to process
        @type elem DOM element
        """
        qtypes = {'short_answer': model.ShortAnswerQuestion,
                  'multiple_choice': model.MultipleChoiceQuestion,
                  'true_false': model.TrueFalseQuestion,
                  'matching': model.MatchingQuestion,
                  'flashcard': model.FlashCard,}
        # Find all common elements
        question_id = elem.getAttribute('id')
        question_type = elem.getAttribute('type')
        credits = _get_child_text(elem, 'credits')
        if credits is not None:
            credits = int(credits)
        text = self._parse_question_text(_get_first_child_named(elem, 'text'))
        difficulty = _get_child_text(elem, 'difficulty')
        advice = _get_child_text(elem, 'advice')
        hint = _get_child_text(elem, 'hint')
        average_time = _get_child_text(elem, 'average-time')
        if average_time is not None:
            average_time = float(average_time)
        stipulated_time = _get_child_text(elem, 'stipulated-time')
        if stipulated_time is not None:
            stipulated_time = float(stipulated_time)
        # Determine question type and get additional data
        question_type = qtypes[question_type]
        if issubclass(question_type, model.MultipleChoiceQuestion):
            choice_elems = elem.getElementsByTagName('choice')
            choices = []
            for child_elem in choice_elems:
                choice_name = child_elem.getAttribute('name')
                choice_text = _get_text(child_elem)
                choices.append((choice_name, choice_text))
        elif issubclass(question_type, model.ShortAnswerQuestion):
            expected_length = int(_get_child_text(elem, 'expected-length'))
        elif issubclass(question_type, model.MatchingQuestion):
            keys = [_get_text(e) for e in elem.getElementsByTagName('key')]
            answers = [_get_text(e) for e in
                       elem.getElementsByTagName('answer')]
        elif issubclass(question_type, model.FlashCard):
            back_text = _get_child_text(elem, 'back-text')
        # Create question
        if issubclass(question_type, model.MultipleChoiceQuestion):
            newQuestion = question_type(question_id, text, choices,
                                        credits, difficulty)
        elif issubclass(question_type, model.ShortAnswerQuestion):
            newQuestion = question_type(question_id, text, expected_length,
                                        credits, difficulty)
        elif issubclass(question_type, model.MatchingQuestion):
            newQuestion = question_type(question_id, text, keys, answers,
                                        credits, difficulty)
        elif issubclass(question_type, model.FlashCard):
            newQuestion = question_type(question_id, text, back_text,
                                        credits, difficulty)
        else:
            newQuestion = question_type(question_id, text, credits, difficulty)
        newQuestion.advice = advice
        newQuestion.hint = hint
        newQuestion.average_time = average_time
        newQuestion.stipulated_time = stipulated_time
        # Get images
        for child in elem.childNodes:
            if child.nodeType == minidom.Node.ELEMENT_NODE:
                new_image = None
                if child.tagName == 'img':
                    new_image = self._handle_image(child)
                elif child.tagName == 'image-page':
                    new_image = self._handle_image_page(child)
                if new_image is not None:
                    newQuestion.images.append(new_image)
        # Add question to test
        self.test.add_question(newQuestion)
        return newQuestion
    
    def _handle_image_page(self, elem):
        page = model.ImagePage(title=elem.getAttribute('title'))
        for child in elem.childNodes:
            if child.nodeType == minidom.Node.ELEMENT_NODE and \
               child.tagName == 'img':
                page.images.append(self._handle_image(child))
        return page
    
    def _handle_image(self, elem):
        # Get necessary information
        mime_type = elem.getAttribute('type')
        title = elem.getAttribute('title')
        position = elem.getAttribute('position')
        if not position:
            position = 'left'
        link = elem.getAttribute('src')
        # Determine size
        width = elem.getAttribute('width')
        if width:
            width = int(width)
        height = elem.getAttribute('height')
        if height:
            height = int(height)
        if not width or not height:
            # TODO: Do a proportional scaling trick
            size = None
        else:
            size = (width, height)
        # Get data
        data = _get_text(elem, post=False)
        if data:
            data = b64decode(data)
            data = GzipFile(fileobj=StringIO(data))
        # Construct image
        image = model.Image(mime_type, title, size, position)
        image.set_link(link)
        if data is not None:
            image.set_data(data)
        return image

class AnswersParser(object):
    """
    Parses answer XML files.
    
    Generally, this class will not need to be used directly; instead, use
    {@link parse_answers parse_answers}.
    
    @ivar document The document currently being parsed
    @type document DOM document
    @ivar answer_list The answers being constructed
    @type answer_list {@link model.AnswerList AnswerList}
    @see parse_answers
    """
    def parse(self, doc):
        """
        Parses an answer file.
        
        @param doc The XML DOM of the file to parse
        @type doc DOM document
        @return The answers that the file represents
        @returntype list of {@link model.Answer Answer objects}
        """
        self.document = doc
        root = doc.documentElement
        self.answer_list = model.AnswerList()
        for node in root.childNodes:
            if node.nodeType == minidom.Node.ELEMENT_NODE:
                name = node.tagName
                if name == 'answer':
                    self._handle_answer(node)
                elif name == 'student-name':
                    self.answer_list.student_name = _get_text(node)
                else:
                    # TODO: Raise error for undetected element
                    pass
        return self.answer_list
    
    def _handle_answer(self, elem):
        """
        Handles a single answer element and adds the answer to the list.
        
        @param elem The answer element to process
        @type elem DOM element
        """
        # Find all necessary elements
        question_id = elem.getAttribute('id')
        time_taken = float(elem.getAttribute('time-taken'))
        hint_used = elem.getAttribute('hint-used')
        if hint_used is None:
            hint_used = False
        else:
            hint_used = _xml2bool.get(hint_used, False)
        answer = _get_text(elem)
        # Create answer
        newAnswer = model.Answer(question_id, answer, time_taken, hint_used)
        # Add answer to list
        self.answer_list.answers.append(newAnswer)
        return newAnswer

def _parse(parser, document, *args, **kw):
    """
    Generic function to parse a file.
    
    @param parser Object that provides a <code>parse(doc)</code> method
    @param document Document to parse.  If given a string, it is interpreted as
                    a path.  If given a DOM Document, then it is directly
                    parsed.  Otherwise, it is interpreted as a file-like object
                    attempts to parse it.
    @type document str, DOM document, or file-like object
    @return The parser's result
    """
    # Obtain parse source
    if isinstance(document, basestring):
        # Filename
        document = minidom.parse(document)
    elif isinstance(document, minidom.Document):
        # XML Document
        pass
    else:
        # File-like object
        document = minidom.parse(document)
    # Run parser and return result
    return parser.parse(document)

def parse_test(document):
    """
    Parses a test file.
    
    @param document Document to parse.  If given a string, it is interpreted as
                    a path.  If given a DOM Document, then it is directly
                    parsed.  Otherwise, it is interpreted as a file-like object
                    attempts to parse it.
    @type document str, DOM document, or file-like object
    @return The archived test
    @returntype {@link model.Test Test}
    """
    return _parse(TestParser(), document)

def parse_answers(document):
    """
    Parses an answers file.
    
    @param document Document to parse.  If given a string, it is interpreted as
                    a path.  If given a DOM Document, then it is directly
                    parsed.  Otherwise, it is interpreted as a file-like object
                    attempts to parse it.
    @type document str, DOM document, or file-like object
    @return The answers that the file represents
    @returntype list of {@link model.Answer Answer objects}
    """
    return _parse(AnswersParser(), document)

def serialize_answers(answers):
    """
    Generate an XML document for a list of answers.
    
    @param answers A list of answers to serialize
    @type answers {@link model.AnswerList AnswerList}
    @return The generated XML document
    @returntype DOM document
    """
    doc = minidom.Document()
    root = doc.createElement("answer-list")
    doc.appendChild(root)
    # Add student name
    if getattr(answers, 'student_name', None) is not None:
        elem = doc.createElement("student-name")
        elem.appendChild(doc.createTextNode(answers.student_name))
        root.appendChild(elem)
    # Add answers
    for answer in answers:
        elem = doc.createElement("answer")
        elem.setAttribute("id", answer.id)
        elem.setAttribute("time-taken", unicode(answer.time_taken))
        elem.setAttribute("hint-used", _bool2xml[answer.hint_used])
        elem.appendChild(doc.createTextNode(answer.answer))
        root.appendChild(elem)
    return doc

# Test: Parse data/sample.xml

def main(args=None):
    """Runs a diagnostic on the test parser."""
    indent = ' ' * 4
    # Parse arguments
    if args is None:
        args = sys.argv[1:]
    if len(args) == 0:
        test_path = os.path.join(os.path.pardir, "data", "sample.xml")
    elif len(args) == 1:
        test_path = args[0]
    else:
        print >> sys.stderr, "usage: parse.py [test_file]"
        return 1
    # Parse test
    test = parse_test(test_path)
    # Serialize test
    print "Test id:", test.id
    for question in test.questions:
        # Show question info
        print "[%s] (%s) %s" % (question.id, question.difficulty,
                                question.text)
        # Show images
        for image in question.images:
            if isinstance(image, model.Image):
                print image
            elif isinstance(image, model.ImagePage):
                print "Image page:", image.title
                for subimage in image.images:
                    print indent + str(subimage)
        # Show specific info
        if isinstance(question, model.MultipleChoiceQuestion):
            for choice in question.choices:
                print indent + "(%s) %s" % (choice[0], choice[1])
        elif isinstance(question, model.TrueFalseQuestion):
            print indent + "True/False"
        elif isinstance(question, model.ShortAnswerQuestion):
            print indent + '_' * question.expected_length
        elif isinstance(question, model.MatchingQuestion):
            for key in question.keys:
                print indent + key
            print
            for answer in question.answers:
                print indent + answer
        elif isinstance(question, model.FlashCard):
            print indent + "Answer: %s" % question.back_text
    # Serialize answers
    answers = [q.answer("Hello, World!", 42.0) for q in test.questions
               if not isinstance(q, (model.FlashCard, model.MatchingQuestion))]
    answer_list = model.AnswerList(answers, "Ross Light")
    print serialize_answers(answer_list).toprettyxml(indent='   ')
    return 0

if __name__ == '__main__':
    sys.exit(main())
