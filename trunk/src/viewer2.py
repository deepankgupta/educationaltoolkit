'''                             Test Taker
It is a part of the Educational Toolkit developed for OLPC.
It has been designed to run on the student laptop and allow him to take
verious types of test developed by the teacher.
'''


VERSION = "0.1"

try:
	import sys
	import random
	import math
	import os
	import getopt
	import pygame
	from socket import *
	from pygame.locals import *
	from xml.dom import minidom
except ImportError, err:
	print "couldn't load module. %s" % (err)
	sys.exit(2)

def load_image(name):
    """ Load image and return image object"""
    fullname = os.path.join('data',name)
    try:
        image = pygame.image.load(fullname)
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except pygame.error, message:
        print 'Cannot load image:', fullname
        raise SystemExit, message
    return image

def load_xml(name):
    filename = os.path.join('data',name)
    try:
        xmldoc = minidom.parse(filename)
    except:
        print 'Problem Loading File'
        raise SystemExit
    return xmldoc

def get_question(xmldoc, no):
    tags = ('Number', 'Type', 'Marks', 'Text', 'Image', 'Difficulty')
    i = 0
    text = []
    for tag in tags:
        question_list = xmldoc.getElementsByTagName(tag)
        text += [question_list[no].toxml()]
        text[i] = text[i].replace('<' + tag + '>', '', 1)
        text[i] = text[i].replace('</' + tag + '>', '', 1)
        i = i + 1
    output_str='Q.' + text[0] + ' ' + text[3]
    return output_str

def get_instructions(xmldoc):
    tag = 'Instructions'
    inst = xmldoc.getElementsByTagName(tag)
    text = inst[0].toxml()
    text = text.replace('<' + tag + '>', '', 1)
    text = text.replace('</' + tag + '>', '', 1)
    return text
        

class Guide(pygame.sprite.Sprite):
    """the animated character"""
    def __init__(self):
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer
        self.image = load_image('teacher.png')
        self.rect = (self.image).get_rect()
    def spin(self):
        "spin the guide image"
        center = self.rect.center
        rotate = pygame.transform.rotate
        self.image = rotate(self.image, 36)
        self.rect = self.image.get_rect(center = center)

class Question(pygame.sprite.Sprite):
    """This is the class which handles all the aspects of a question"""
    def __init__(self):
        self.xmldoc = load_xml('test.xml')
        pygame.sprite.Sprite.__init__(self) #call Sprite initializer

def question_screen(xmldoc, qno):
    font = pygame.font.Font(None,36)
    text = font.render(get_question(xmldoc, qno), 1, (10, 10, 10))
    textpos = text.get_rect()
    textpos.center = (320, 200)
    return text, textpos

def place_true_false_buttons(button_rect, background):
    #Place the True and false button
    button = load_image('true.png')
    button_rect[0] = button.get_rect()
    button_rect[0].center = (150,400)
    background.blit(button,button_rect[0])
    button = load_image('false.png')
    if len(button_rect) > 1 :
        button_rect[1] = button.get_rect()
    else :
        button_rect.append(button.get_rect())
    button_rect[1].center = (450,400)
    background.blit(button,button_rect[1])

def show_instructions(background, xmldoc):
    #Display Instructions regarding the test
    font = pygame.font.Font(None, 36)
    text = font.render("Instructions for the test", 1, (10,10,10))
    textpos = text.get_rect()
    textpos.center = (320, 50)
    background.blit(text, textpos)
    font = pygame.font.Font(None, 18)
    text = font.render(get_instructions(xmldoc), 1, (10,10,10))
    textpos = text.get_rect()
    textpos.center = (320,200)
    background.blit(text, textpos)
        
def main():
    #Initialise the screen
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Test Viewer')
    xmldoc = load_xml('test.xml')
             
    #Fill background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((250, 250, 250))
    show_instructions(background, xmldoc)
    screen_type = 1 #1 is the screen for showing the instructions regarding the test.
    question_number = -1
    
    #Display the guide
    guide = Guide()
    guidesprite = pygame.sprite.RenderPlain(guide)
    button_rect = []
    #Place the Start the test button
    button = load_image('button.png')
    button_rect.append(button.get_rect())
    button_rect[0].center = (320,450)
    background.blit(button,button_rect[0])
    #Blit everything to the screen
    screen.blit(background,(0,0))
    pygame.display.flip()
   
    #Event Loop
    while 1:
        for event in pygame.event.get():
            if event.type == QUIT:
                sys.exit(0)
            elif event.type == MOUSEBUTTONDOWN:
                print "Mouse button down"
                for rect in button_rect:
                    if event.pos >= rect.topleft and event.pos <= rect.bottomright :
                        if screen_type == 1 :
                            background.fill((250,250,250))
                            question_number = 0
                            text, textpos = question_screen(xmldoc, question_number)
                            background.blit(text, textpos)
                            place_true_false_buttons(button_rect, background)
                            screen_type = 2 # 2 is the screen type that means that the screen is displaying questions.
                        elif screen_type == 2 :
                            background.fill((250,250,250))
                            question_number = question_number + 1
                            text, textpos = question_screen(xmldoc, question_number)
                            background.blit(text, textpos)
                            place_true_false_buttons(button_rect, background)
                            screen_type = 2
                        else :
                            #TODO:Get the answer and store it into a file. 
                            question_number = question_number + 1
                            background.fill((250,250,250))
                            text, textpos = question_screen(xmldoc, question_number)
                            background.blit(text, textpos)                            
        screen.blit(background, guide)
        guidesprite.update()
        guidesprite.draw(screen)
        pygame.display.flip()

if __name__=='__main__':main()     
