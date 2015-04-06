from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.graphics import *
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty

import numpy

import wop.level



Builder.load_string("""
<LevelWidget>:
    size_hint: (1, 1)
    levelCanvasWidget: levelCanvasWidget
    zoom_outButton: zoom_outButton
    zoom_inButton: zoom_inButton
    createAndSelectWidget: createAndSelectWidget
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
                        id: levelCanvasWidget
                        

            BoxLayout:
                size_hint: (1,0.1)
                orientation: "horizontal"
                Button:
                    id: zoom_outButton
                    text: "-"
                    on_release: root.zoom_out()
                Button:
                    id: zoom_inButton
                    text: "+"
                    on_release: root.zoom_in()

                Button:
                    id: menuButton
                    text: "menu"
                    on_press: root.screen_manager.current = 'main_menu_screen'
""")

class LevelWidget(BoxLayout):
    levelCanvasWidget = ObjectProperty(None)
    createAndSelectWidget = ObjectProperty(None)
    screen_manager = ObjectProperty(None)
    def __init__(self,*arg,**kwarg):
        super(LevelWidget,self).__init__(*arg, **kwarg)
        self.level = None


    def on_pre_leave(self):
        self.levelCanvasWidget.on_pre_leave()
        self._kill_level()
    def on_leave(self):
        self.levelCanvasWidget.on_leave()
    def on_pre_enter(self):
        self.levelCanvasWidget.on_pre_enter()
        self._init_level()
    def on_enter(self):
        self.levelCanvasWidget.on_enter()
        #self._init_level()


    def zoom_in(self):
        s = self.get_scale()
        self.set_scale(s*1.25)
    def zoom_out(self):
        s = self.get_scale()
        ns = s/1.25
        if ns > 1.0:
            self.set_scale(ns)

    def set_scale(self, scale):
        self.levelCanvasWidget.set_scale(scale)
        
    def get_scale(self):
        print self.pos,self.size
        return self.levelCanvasWidget.get_scale()

    def get_offset(self):
        return self.levelCanvasWidget.get_offset()

    def set_offset(self, offset):
        return self.levelCanvasWidget.set_offset(offset)

    def render(self):
        self.levelCanvasWidget.render()

    def add_render_item(self, renderItem, z):
        self.levelCanvasWidget.add_render_item(renderItem,z)


    def set_level(self, level):
        assert  self.level is None
        self.level = level

    def _init_level(self):
        # load level
        #self.level = wop.level.SimpleLevel(gameRender=self.levelCanvasWidget)
        
        assert self.level is not None
        self.level.initPhysics()
        # pass the level  to the levelCanvasWidget
        self.levelCanvasWidget.set_level(self.level)

        wmManager = self.createAndSelectWidget.wmManager
        #
        self.level.set_wm_manager(wmManager)
        wmManager.setLevel(level = self.level)
        # start the level (start physic simulation)
        # will schedule level.updateCaller
        self.level.start_level()

    def _kill_level(self):
        self.level.stop_level()
        self.level = None


