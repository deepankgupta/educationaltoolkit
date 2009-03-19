#!/usr/bin/env python


from sugar.activity import activity
import logging
import sys, os
import pygtk
pygtk.require('2.0')
import gtk
from parse import *
import model

# File informations
__author__="Deepank Gupta"
__date__="March 25, 2008"
__version__="0.1"

class EducationalToolkitActivity(activity.Activity):
    """TestBook

	This class provides a viewer application in GTK which allows a student
	to access test questions, submit answers etc. Currently this class is
	a very rough demo which does not contain anything other than displaying 
	the text of the questions. 
	"""
    
    
    def submit(self, widget, event=None):
        #TODO : Send paper over the network using Connection Manager. 
        gtk.main_quit()
        return False
        
    def callback(self, widget, data=None):
        print "%s was toggled %s" % (data, ("OFF", "ON")[widget.get_active()])
    
    def draw(self, question):
        if isinstance(question, model.TrueFalseQuestion):
            inn_table = gtk.Table(3, 6, True)
            label = gtk.Label(question.text)
            inn_table.attach(label, 0, 6, 0, 1)
            label.show()
            button = gtk.RadioButton(None, "True")
            button.connect("toggled", self.callback, "True Button")
            inn_table.attach(button,0, 2, 1, 2)
            button.show()
            button = gtk.RadioButton(button, "False")
            button.connect("toggled", self.callback, "False Button")
            inn_table.attach(button,3, 6, 1, 2)
            button.show()
        elif isinstance(question, model.MultipleChoiceQuestion):
            inn_table = gtk.Table(len(question.choices) + 3, len(question.choices) + 3, True)
            label = gtk.Label(question.text)
            inn_table.attach(label, 0, 6, 0, 1)
            label.show()
            button = None
            i = 1
            for choice in question.choices:
                label = gtk.Label(choice[0])
                inn_table.attach(label, 0, 1, i, i + 1)
                label.show()
                button = gtk.RadioButton(button, choice[1])
                button.connect("toggled", self.callback, choice[0])
                inn_table.attach(button, 2 ,6 ,i ,i + 1)
                button.show()
                i = i + 1
    	elif isinstance(question,model.ShortAnswerQuestion):
    	    inn_table=gtk.Table(3, 6, True)
    	    label=gtk.Label(question.text)
    	    inn_table.attach(label,	0,6,0,1)
    	    entry=gtk.Entry(0)
    	    inn_table.attach(entry,0,6,1,2)
    	    label.show()     
    	    entry.show()
        else :    
            inn_table = gtk.Table(len(question.keys) + 3, len(question.keys) + 6, False)
            col=len(question.keys) + 6
            size=col/2
            label = gtk.Label(question.text)
            inn_table.attach(label,0,col,0,1)
            label.show()
            i = 1
            for key in question.keys:
            	key=str(i) + "." + key
            	label=gtk.Label(key)
            	inn_table.attach(label, 0, size, i, i + 1)
            	entry=gtk.Entry(1)
            	inn_table.attach(entry,size, size+1 ,i,i+1)
            	label.show()
            	entry.show()
            	i = i+1
            i = 1
            for answer in question.answers:
            	answer=str(i) + "." + answer
            	label=gtk.Label(answer);
            	inn_table.attach(label,size + 1, col ,i , i + 1)
            	label.show()
            	i = i+1
        return inn_table
    
    def __init__(self, handle):
        print "Running activity init", handle
        activity.Activity.__init__(self,handle)
        print "running activity"
        # Create a new notebook, place the position of the tabs
        toolbox = activity.ActivityToolbox(self)
        self.set_toolbox(toolbox)
        toolbox.show()
        self.table = gtk.Table(3, 6, False)
        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_LEFT)
        self.table.attach(self.notebook, 0, 6, 0, 1)
        self.set_canvas(self.table)
        self.notebook.show()
        # Let's append a bunch of pages to the notebook
        
        test = parse_test("data/sample.xml")
        i = 1
        for question in test.questions:
            bufferf = "%s    %d credits    %s Difficulty" % (question.id, question.credits, question.difficulty)
            bufferl = "Question %d" % i
            frame = gtk.Frame(bufferf)
            frame.set_border_width(10)
            frame.set_size_request(600, 450)
            self.set_canvas(frame)
            frame.show()
            self.inn_table = self.draw(question)
            frame.set_label(bufferf)
            frame.add(self.inn_table)
            self.set_canvas(self.inn_table)
            self.inn_table.show()
            self.label = gtk.Label(bufferl)
            self.notebook.append_page(frame, self.label)
            i = i + 1
        # Set what page to start at 
        self.notebook.set_current_page(0)
        # Create a bunch of buttons to do common tasks. 
        self.button = gtk.Button("Next Question")
        self.button.connect("clicked", lambda w: self.notebook.next_page())
        self.table.attach(self.button, 0, 1, 1, 2)
        self.set_canvas(self.button)
        self.button.show()
        self.button = gtk.Button("Previous Question")
        self.button.connect("clicked", lambda w: self.notebook.prev_page())
        self.table.attach(self.button, 1, 2, 1, 2)
        self.set_canvas(self.button)
        self.button.show()
        self.button = gtk.Button("Submit Paper")
        self.button.connect("clicked", self.submit)
        self.table.attach(self.button, 2, 3, 1, 2)
        self.set_canvas(self.button)
        self.button.show()
        self.set_canvas(self.table)
        self.table.show()
        


