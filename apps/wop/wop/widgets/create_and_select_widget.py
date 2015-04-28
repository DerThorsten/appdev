from kivy.logger import Logger
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.uix.image import Image as UixImage
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.graphics import *
from kivy.core.image import Image as CoreImage
from kivy.uix.dropdown import DropDown
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.event import EventDispatcher
from functools import partial
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
            oldOffset = self.level.get_offset()[:]
            self.level.set_offset(oldOffset+d)

    def world_on_touch_up(self, wpos, touch):
        #Logger.debug("SimpleSelector: touch  move %.1f %.1f"%wpos ) 
        self.hasBody = False


class GooCreator(WorldManipulator):
    def __init__(self):
        super(GooCreator,self).__init__()
        self.gooCls = None
        self.tentativeGoo = None
        self.wpos = None

    def _canBeAdded(self):
        if self.tentativeGoo is None:
            return (0,None)
        self.tentativeGoo.pos = self.wpos
        r = self.level.gooGraph.canGooBeAdded(self.tentativeGoo, self.wpos)
        return r
    def world_on_touch_down(self, wpos, touch):
        Logger.debug("RoundGooCreator: touch  down %.1f %.1f"%wpos ) 
        self.tentativeGoo = self.gooCls()
        self.wpos = wpos
    def world_on_touch_move(self, wpos, wppos, touch):
        Logger.debug("RoundGooCreator: touch  move %.1f %.1f"%wpos ) 
        self.wpos = wpos
    def world_on_touch_up(self, wpos, touch):
        Logger.debug("RoundGooCreator: touch  up %.1f %.1f"%wpos ) 
        self.wpos = wpos
        addAs,otherGoosBodies = self._canBeAdded()
        if addAs == 1:
            goo = self.gooCls()
            self.level.addGoo(goo, wpos)
            if otherGoosBodies is not None:     
                for ogb in otherGoosBodies:
                    jointGameItem = goo.createJoint()
                    jointGameItem.add_to_level(self.level, goo, ogb.userData)
                    #self.level.connectGoos(goo, ogb.userData)
        elif addAs == 2:
            b0,b1 = otherGoosBodies
            jointGameItem = self.tentativeGoo.createJoint()
            jointGameItem.add_to_level(self.level, b0.userData, b1.userData)

        self.wpos = None
        self.tentativeGoo  = None

    def render(self):
        if self.wpos is not None and self.tentativeGoo is not None:
            gr = self.level.gameRender
            addAs,otherGoosBodies = self._canBeAdded()
            if addAs <= 1:
                #render connections/joints
                if otherGoosBodies is not None:
                    for ogb in otherGoosBodies:
                        jointGameItem = self.tentativeGoo.createJoint()
                        otherGoo = ogb.userData
                        posB  = ogb.GetWorldPoint(b2Vec2(*otherGoo.localAnchor()))
                        posA  = b2Vec2(self.wpos) + self.tentativeGoo.localAnchor()
                        jointGameItem.render_tentative(gr, posA, posB)
                # render the goo
                self.tentativeGoo.render_tentative(self.level, self.wpos, addAs==1)
            else:
                ogbA = otherGoosBodies[0]                    
                ogbB = otherGoosBodies[1]     
                ogA = ogbA.userData             
                ogB = ogbB.userData

                posA  = ogbA.GetWorldPoint(b2Vec2(*ogA.localAnchor()))
                posB  = ogbB.GetWorldPoint(b2Vec2(*ogB.localAnchor()))
                jointGameItem = self.tentativeGoo.createJoint()
                jointGameItem.render_tentative(gr, posA, posB)

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
        self.gooCreator = GooCreator()


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
<ImageButton>:
    image: image
    id: blackGooButton
    text: "BG"
    background_color: 0,0,0,0.0

    Image:
        id: image
        size: (self.parent.size[0], self.parent.size[1])
        y: self.parent.y
        x: self.parent.x
        source: 'res/black_goo_128.png'
""")
class ImageButton(Button):
    #image =  ObjectProperty(None)
    pass


Builder.load_string("""
<GooDropDown>:
""")

class GooDropDown(BoxLayout):
    dropdown  = ObjectProperty(None)
    def __init__(self,*args,**kwargs):
        super(GooDropDown, self).__init__(*args,**kwargs)
        self.register_event_type('on_select_goo')

        
        self.dropdown = DropDown(spacing=5)
        dropdown = self.dropdown


        self.goos = dict(
            blackGoo='res/black_goo_128.png', 
            greenGoo='res/green_goo_128.png', 
            anchorGoo='res/amboss_goo_128.png',
            balloonGoo='res/pink_goo_128.png',  
        )

        def onRel(button,gooName):
            self.mainbutton.image.source = self.goos[gooName]
            self.dropdown.select(gooName)
            self.dispatch('on_select_goo',gooName)

        for gooName in self.goos.keys():
            imgButton = ImageButton(size_hint=(None,None),height=44)
            imgButton.bind(on_release=partial(onRel,gooName=gooName))
            imgButton.image.source = self.goos[gooName]
            dropdown.add_widget(imgButton)


        # create a big main button
        self.mainbutton = ImageButton()
        self.mainbutton.bind(on_release=dropdown.open)

        
        #dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.add_widget(self.mainbutton)
        #mainbutton.add_widget(dropdown)


    def on_select_goo(self, gooName):
        print "internal on select goo", gooName

Builder.load_string("""
<CreateAndSelectWidget>:
    orientation: "horizontal"
    GooDropDown:
        size_hint_x: None
        size_X: 40
        on_select_goo: root.on_release_creator_button(args[1])
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
        print "i got aevent"
        self.wmManager.wm = self.wmManager.gooCreator
        if objectType == "blackGoo":
            self.wmManager.wm.gooCls = BlackGoo
        elif objectType == "greenGoo":
           Logger.debug("green goo")
           self.wmManager.wm.gooCls = GreenGoo
        elif objectType == "anchorGoo":
            self.wmManager.wm.gooCls = AnchorGoo
        elif objectType == "balloonGoo":
            self.wmManager.wm.gooCls = BallonGoo
        self.wmManager.passLevelToCurrentWm()
