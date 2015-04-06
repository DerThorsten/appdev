from kivy.logger import Logger
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
from kivy.uix.widget import Widget
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics import *
from kivy.core.image import Image as CoreImage
from kivy.config import Config
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty

import numpy

import wop.level



Builder.load_string("""
<LevelWidget>:
    size_hint: (1, 1)
    viewer: viewer
    zoomOutButton: zoomOutButton
    zoomInButton: zoomInButton
    createAndSelectWidget: createAndSelectWidget
    #screen_manager: screen_manager
    BoxLayout:
        opacity: 1
        size_hint: (1, 1)
        orientation: "horizontal"

        CreateAndSelectWidget:
            id: createAndSelectWidget
            size_hint: (0.15, 1)              
            
        BoxLayout:
            orientation: "vertical"
            size_hint: (1, 1)
            size: (100,200)
            ScrollView:
                do_scroll: False
                size_hint: (1, 1)
                FloatLayout:
                    LevelCanvasWidget:
                        index: -3
                        text: "foo"
                        size_hint: (1,1)
                        id: viewer
                        

            BoxLayout:
                size_hint: (1,0.1)
                orientation: "horizontal"
                Button:
                    id: zoomOutButton
                    text: "-"
                    on_release: root.zoomOut()
                Button:
                    id: zoomInButton
                    text: "+"
                    on_release: root.zoomIn()

                Button:
                    id: menuButton
                    text: "menu"
                    on_press: root.screen_manager.current = 'main_menu_screen'
""")

class LevelWidget(BoxLayout):
    viewer = ObjectProperty(None)
    zoomInButton = ObjectProperty(None)
    zoomIOutButton = ObjectProperty(None)
    createAndSelectWidget = ObjectProperty(None)
    screen_manager = ObjectProperty(None)
    def __init__(self,*arg,**kwarg):
        super(LevelWidget,self).__init__(*arg, **kwarg)
        self.level = None
    def zoomIn(self):
        s = self.getScale()
        self.setScale(s*1.25)
    def zoomOut(self):
        s = self.getScale()
        ns = s/1.25
        if ns > 1.0:
            self.setScale(ns)
    def setScale(self, scale):
        self.viewer.setScale(scale)
        
    def getScale(self):
        print self.pos,self.size
        return self.viewer.getScale()




    def init_level(self):
        # load level
        self.level = wop.level.SimpleLevel(gameRender=self.viewer)
        self.level.initPhysics()
        # pass the level  to the viewer
        self.viewer.set_level(self.level)

        wmManager = self.createAndSelectWidget.wmManager
        #
        self.level.set_wm_manager(wmManager)
        wmManager.setLevel(level = self.level)
        # start the level (start physic simulation)
        # will schedule level.updateCaller
        self.level.start()
