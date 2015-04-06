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
from Box2D import *
from math import cos,sin,degrees
import functools
from wop.game_items import *
import wop


class WorldManipulator(object):
    def __init__(self):
        self.level = None
    def initAfterSelection(self):
        #Logger.debug("WorldManipulator: init wm after it's selction") 
        pass
    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("WorldManipulator: touch  down %.1f %.1f"%wpos ) 
        pass
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("WorldManipulator: touch  move %.1f %.1f"%wpos ) 
        pass
    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("WorldManipulator: touch  up %.1f %.1f"%wpos ) 
        pass

    def render(self):
        #Logger.debug("WorldManipulator: render" ) 
        pass

class SimpleSelector(WorldManipulator):
    def __init__(self):
        super(SimpleSelector,self).__init__()
        self.hasBody = False
    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("SimpleSelector: touch  down %.1f %.1f"%wpos ) 
        body = wop.body_at_pos(self.level.world, pos=wpos)
        if body is None:
            self.hasBody = False
        else:
            self.hasBody = True
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("SimpleSelector: touch  up   %.1f %.1f"%wpos ) 
        if not self.hasBody :
            d = numpy.array(wpos) - numpy.array(wppos)
            oldOffset = self.level.getOffset()[:]
            self.level.setOffset(oldOffset+d)

    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("SimpleSelector: touch  move %.1f %.1f"%wpos ) 
        self.hasBody = False


class GooCreator(WorldManipulator):
    def __init__(self):
        super(GooCreator,self).__init__()

    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("GooCreator: touch  down %.1f %.1f"%wpos ) 
        pass
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("GooCreator: touch  move %.1f %.1f"%wpos ) 
        pass
    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("GooCreator: touch  up %.1f %.1f"%wpos )
        pass

class RoundGooCreator(GooCreator):
    def __init__(self):
        super(RoundGooCreator,self).__init__()

        self.tentativeGoo = None
        self.wpos = None

    def _canBeAdded(self):
        #gooRadius = self.tentativeGoo.gooRadius()
        #body = wh.body_in_bb(self.level.world, pos=self.wpos, roiRadius=gooRadius)
        #return body is None
        if self.tentativeGoo is None:
            return (0,None) 
        r = self.level.gooGraph.canGooBeAdded(self.tentativeGoo, self.wpos)
        return r
    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("RoundGooCreator: touch  down %.1f %.1f"%wpos ) 
        self.tentativeGoo = self.gooCls()
        self.wpos = wpos
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("RoundGooCreator: touch  move %.1f %.1f"%wpos ) 
        self.wpos = wpos
    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("RoundGooCreator: touch  up %.1f %.1f"%wpos ) 
        addAs,otherGoosBodies = self._canBeAdded()
        if addAs == 1:
            goo = self.gooCls()
            self.level.addGoo(goo, wpos)
            if otherGoosBodies is not None:     
                for ogb in otherGoosBodies:
                    self.level.connectGoos(goo, ogb.userData)
        if addAs == 2:
            b0,b1 = otherGoosBodies
            self.level.connectGoos(b0.userData, b1.userData)
        self.tentativeGoo = None
        self.wpos = None

    def render(self):
        if self.tentativeGoo is not None and self.wpos is not None:
            addAs,otherGoos = self._canBeAdded()
            if addAs <= 1:
                self.tentativeGoo.render_tentative(self.level, self.wpos, addAs==1)
            else:
                pass

class BlackGooCreator(RoundGooCreator):
    def __init__(self):
        super(BlackGooCreator,self).__init__()
        self.gooCls = BlackGoo

class GreenGooCreator(RoundGooCreator):
    def __init__(self):
        super(GreenGooCreator,self).__init__()
        self.gooCls = GreenGoo
        
class AnchorGooCreator(GooCreator):
    def __init__(self):
        super(AnchorGooCreator,self).__init__()
        self.gooCls = AnchorGoo
        self.tentativeGoo = None
        self.wpos = None

    def _canBeAdded(self):
        #gooRadius = self.tentativeGoo.gooRadius()
        #body = wh.body_in_bb(self.level.world, pos=self.wpos, roiRadius=gooRadius)
        #return body is None
        if self.tentativeGoo is None:
            return (0,None) 
        r = self.level.gooGraph.canGooBeAdded(self.tentativeGoo, self.wpos)
        return r
    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("RoundGooCreator: touch  down %.1f %.1f"%wpos ) 
        self.tentativeGoo = self.gooCls()
        self.wpos = wpos
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("RoundGooCreator: touch  move %.1f %.1f"%wpos ) 
        self.wpos = wpos
    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("RoundGooCreator: touch  up %.1f %.1f"%wpos ) 
        addAs,otherGoosBodies = self._canBeAdded()
        if addAs == 1:
            goo = self.gooCls()
            self.level.addGoo(goo, wpos)
            if otherGoosBodies is not None:     
                for ogb in otherGoosBodies:
                    self.level.connectGoos(goo, ogb.userData)
        if addAs == 2:
            b0,b1 = otherGoosBodies
            self.level.connectGoos(b0.userData, b1.userData)
        self.tentativeGoo = None
        self.wpos = None

    def render(self):
        if self.tentativeGoo is not None and self.wpos is not None:
            addAs,otherGoos = self._canBeAdded()
            if addAs <= 1:
                self.tentativeGoo.render_tentative(self.level, self.wpos, addAs==1)
            else:
                pass

class KillSelector(WorldManipulator):
    def __init__(self):
        super(KillSelector,self).__init__()

class WorldManipulatorManager(object):
    def __init__(self):

        # will be initialized externally
        self.level = None

        self.empty = WorldManipulator()

        # selectors
        self.simpleSelector = SimpleSelector()
        self.killSelector = KillSelector()

        # goo creators
        self.blackGooCreator = BlackGooCreator()
        self.greenGooCreator = GreenGooCreator()
        self.anchorGooCreator = AnchorGooCreator()

        # set current
        self.wm = self.simpleSelector

    def setLevel(self, level):
        self.level = level
        self.passLevelToCurrentWm()

    def passLevelToCurrentWm(self):
        self.wm.level = self.level

    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("WorldManipulatorManager: touch  up %.1f %.1f"%wpos ) 
        self.wm.world_on_touch_down(wpos, touch)
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("WorldManipulatorManager: touch  up %.1f %.1f"%wpos ) 
        self.wm.world_on_touch_move(wpos,wppos, touch)
    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("WorldManipulatorManager: touch  up %.1f %.1f"%wpos ) 
        self.wm.world_on_touch_up(wpos, touch)

    def render(self):
        return self.wm.render()



Builder.load_string("""
<CreateAndSelectWidget>:
    orientation: "vertical"
    TabbedPanel:
        tab_pos: "left_mid"
        do_default_tab: False
        TabbedPanelItem:
            text: "select"
            BoxLayout:
                orientation: "vertical"
                Button:
                    id: selectObjectButton
                    text: "->"
                    on_release: root.on_release_selector_button("select")
                Button:
                    id: killObjectButton
                    text: "kill"
                    on_release: root.on_release_selector_button("kill")
        TabbedPanelItem:
            text: "goos"
            default_tab:True
            BoxLayout:
                orientation: "vertical"
                Button:
                    id: blackGooButton
                    text: "BG"
                    on_release: root.on_release_creator_button("black-goo")
                    Image:
                        size: (self.parent.size[0], self.parent.size[1])
                        y: self.parent.y
                        x: self.parent.x
                        source: 'res/black_goo_128.png'
                Button:
                    id: greenGooButton
                    text: "GB"
                    on_release: root.on_release_creator_button("green-goo")
                    Image:
                        size: (self.parent.size[0], self.parent.size[1])
                        y: self.parent.y #+ self.parent.height - 30
                        x: self.parent.x
                        source: 'res/green_goo_128.png'
                Button:
                    id: anchorGooButton
                    on_release: root.on_release_creator_button("anchor-goo")
                    Image:
                        size: (self.parent.size[0], self.parent.size[1])
                        y: self.parent.y #+ self.parent.height - 30
                        x: self.parent.x
                        source: 'res/amboss_goo_128.png'
""")
class CreateAndSelectWidget(BoxLayout):

    selectObjectButton = ObjectProperty(None)
    killObjectButton = ObjectProperty(None)
    blackGooButton = ObjectProperty(None)
    greenGooButton = ObjectProperty(None)
    redGooButton = ObjectProperty(None)
    pinkGooButton = ObjectProperty(None)

    def __init__(self,*arg,**kwarg):
        super(CreateAndSelectWidget,self).__init__(*arg, **kwarg)
        self.wmManager = WorldManipulatorManager()

    def on_release_selector_button(self, selectorType):
        if selectorType == "select":
            self.wmManager.wm = self.wmManager.simpleSelector
        elif selectorType == "kill":
            self.wmManager.wm = self.wmManager.killSelector
        self.wmManager.passLevelToCurrentWm()
    def on_release_creator_button(self , objectType):
        if objectType == "black-goo":
            self.wmManager.wm = self.wmManager.blackGooCreator
        elif objectType == "green-goo":
            self.wmManager.wm = self.wmManager.greenGooCreator
        elif objectType == "anchor-goo":
            self.wmManager.wm = self.wmManager.anchorGooCreator
        self.wmManager.passLevelToCurrentWm()
