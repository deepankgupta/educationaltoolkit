#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
from parse import *
import model

# File informations
__author__="Deepank Gupta"
__date__="March 25, 2008"
__version__="0.1"

class Testbook:
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
        else:    
            inn_table = gtk.Table(3,6,False)
            label = gtk.Label(question.text)
            inn_table.attach(label,0,6,0,1)
            entry = gtk.Entry(0)
            inn_table.attach(entry,0,6,1,2)
            label.show()
            entry.show()
        return inn_table
    
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.connect("delete_event", self.submit)
        window.set_border_width(10)
        table = gtk.Table(3, 6, False)
        window.add(table)
        # Create a new notebook, place the position of the tabs
        notebook = gtk.Notebook()
        notebook.set_tab_pos(gtk.POS_LEFT)
        table.attach(notebook, 0, 6, 0, 1)
        notebook.show()
        
        
        # Let's append a bunch of pages to the notebook
        
        test = parse_test("../data/sample.xml")
        i = 1
        for question in test.questions:
            bufferf = "%s    %d credits    %s Difficulty" % (question.question_id, question.credits, question.difficulty)
            bufferl = "Question %d" % i
            frame = gtk.Frame(bufferf)
            frame.set_border_width(10)
            frame.set_size_request(600, 450)
            frame.show()
            inn_table = self.draw(question)
            frame.set_label(bufferf)
            frame.add(inn_table)
            inn_table.show()
            label = gtk.Label(bufferl)
            notebook.append_page(frame, label)
            i = i + 1
        # Set what page to start at 
        notebook.set_current_page(1)
        # Create a bunch of buttons to do common tasks. 
        button = gtk.Button("Next Question")
        button.connect("clicked", lambda w: notebook.next_page())
        table.attach(button, 0, 1, 1, 2)
        button.show()
        button = gtk.Button("Previous Question")
        button.connect("clicked", lambda w: notebook.prev_page())
        table.attach(button, 1, 2, 1, 2)
        button.show()
        button = gtk.Button("Submit Paper")
        button.connect("clicked", self.submit)
        table.attach(button, 2, 3, 1, 2)
        button.show()
        table.show()
        window.show()

def main():
    gtk.main()
    return 0

if __name__ == "__main__":
   Testbook()
   main()
