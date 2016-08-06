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
from kivy.properties import NumericProperty,StringProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.event import EventDispatcher
from functools import partial
import numpy
from pybox2d import *
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
        goosLeft = self.level.gooRes[self.gooCls]
        if goosLeft <= 0 or self.tentativeGoo is None:
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
            jointGameItem = self.tentativeGoo.createJoint(goAddedAsJoint=True)
            jointGameItem.add_to_level(self.level, b0.userData, b1.userData)

        # decrement number of goos and update gui
        if addAs == 1 or addAs == 2: 
            goosLeft = self.level.gooRes[self.gooCls]
            assert goosLeft >= 1
            goosLeft -= 1
            self.level.gooRes[self.gooCls] = goosLeft
            self.gooButtonWidgets[self.gooCls].goosLeft = str(goosLeft)
            self.selectedGooButtonWidget.goosLeft = str(goosLeft)

            if goosLeft == 0 :
                self.gooButtonWidgets[self.gooCls].disabled = True
                #self.selectedGooButtonWidget.disabled = True
            self.level.gooOrJointAdded()
        self.wpos = None
        self.tentativeGoo  = None

    def render(self):
        goosLeft = self.level.gooRes[self.gooCls]
        if goosLeft > 0:
            if self.wpos is not None and self.tentativeGoo is not None:
                gr = self.level.gameRender
                addAs,otherGoosBodies = self._canBeAdded()
                if addAs <= 1:
                    #render connections/joints
                    if otherGoosBodies is not None:
                        for ogb in otherGoosBodies:
                            jointGameItem = self.tentativeGoo.createJoint()
                            otherGoo = ogb.userData
                            posB  = ogb.getWorldPoint(b2.vec2(*otherGoo.localAnchor()))
                            posA  = b2.vec2(self.wpos) + b2.vec2(self.tentativeGoo.localAnchor())
                            jointGameItem.render_tentative(gr, posA, posB)
                    # render the goo
                    self.tentativeGoo.render_tentative(self.level, self.wpos, addAs==1)
                else:
                    ogbA = otherGoosBodies[0]                    
                    ogbB = otherGoosBodies[1]     
                    ogA = ogbA.userData             
                    ogB = ogbB.userData

                    posA  = ogbA.getWorldPoint(b2.vec2(*ogA.localAnchor()))
                    posB  = ogbB.getWorldPoint(b2.vec2(*ogB.localAnchor()))
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

        # here we initialize the resources

        for gooCls in self.gooButtonWidgets.keys():
            goosLeft = self.level.gooRes[gooCls]
            gooButtonWidget =  self.gooButtonWidgets[gooCls]
            gooButtonWidget.disabled = goosLeft == 0
            gooButtonWidget.goosLeft = str(self.level.gooRes[gooCls])



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
<GooButtonWidget>:
    imageButton: imageButton
    image: imageButton.image
    size_hint_x: 1
    size_hint_y: None
    height: 45
    width: 200
    BoxLayout:
        orientation: 'horizontal'
        ImageButton:
            id: imageButton
            size_hint_x: 1
        Label:
            size_hint_x: 1
            text: root.goosLeft
""")
class GooButtonWidget(BoxLayout):
    goosLeft  = StringProperty('0')



Builder.load_string("""
<GooDropDown>:
""")

class GooDropDown(BoxLayout):
    dropdown  = ObjectProperty(None)
    gooButtonWidgets = ObjectProperty(dict())
    selectedGooButtonWidget = ObjectProperty(None)
    def __init__(self,*args,**kwargs):
        super(GooDropDown, self).__init__(*args,**kwargs)
        self.register_event_type('on_select_goo')

        gooClsDict = RegisteredGoos.Instance().gooClsDict
        
        self.dropdown = DropDown(spacing=5)
        dropdown = self.dropdown


        def onRel(button,gooCls):
            self.selectedGooButtonWidget.image.source = gooCls.gooImage().filename
            goosLeft = self.gooButtonWidgets[gooCls].goosLeft
            self.selectedGooButtonWidget.goosLeft = goosLeft
            #self.selectedGooButtonWidget.disabled = goosLeft == 0
            self.dropdown.select(gooCls)
            self.dispatch('on_select_goo',gooCls)

        for gooName in gooClsDict.keys():

            gooCls = gooClsDict[gooName] 

            gooButtonWidget = GooButtonWidget()
            imageButton = gooButtonWidget.imageButton
            imageButton.bind(on_release=partial(onRel,gooCls=gooCls))
            imageButton.image.source = gooCls.gooImage().filename
            dropdown.add_widget(gooButtonWidget)

            self.gooButtonWidgets[gooCls] = gooButtonWidget


        # create a big main button
        self.selectedGooButtonWidget = GooButtonWidget()
        self.selectedGooButtonWidget.imageButton.bind(on_release=dropdown.open)

        
        #dropdown.bind(on_select=lambda instance, x: setattr(self.mainbutton, 'text', x))
        self.add_widget(self.selectedGooButtonWidget)
        #mainbutton.add_widget(dropdown)


    def on_select_goo(self, gooCls):
        print "internal on select goo", gooCls

Builder.load_string("""
<CreateAndSelectWidget>:
    orientation: "horizontal"
    gooDropDown: gooDropDown
    gooButtonWidgets: gooDropDown.gooButtonWidgets
    selectedGooButtonWidget: gooDropDown.selectedGooButtonWidget
    GooDropDown:
        id: gooDropDown
        size_hint_x: None
        size_X: 40
        on_select_goo: root.on_release_creator_button(args[1])
""")
class CreateAndSelectWidget(BoxLayout):
    #gooDropDown = ObjectProperty(None)
    def __init__(self,*arg,**kwarg):
        super(CreateAndSelectWidget,self).__init__(*arg, **kwarg)
        self.wmManager = WorldManipulatorManager()
        Clock.schedule_once(self.post_init, 0)
    def post_init(self,*args):
        self.wmManager.gooButtonWidgets = self.gooDropDown.gooButtonWidgets
        self.wmManager.gooCreator.gooButtonWidgets = self.gooDropDown.gooButtonWidgets

        self.wmManager.selectedGooButtonWidget = self.gooDropDown.selectedGooButtonWidget
        self.wmManager.gooCreator.selectedGooButtonWidget = self.gooDropDown.selectedGooButtonWidget

    def on_release_selector_button(self, selectorType):
        if selectorType == "select":
            self.wmManager.wm = self.wmManager.simpleSelector
        elif selectorType == "kill":
            self.wmManager.wm = self.wmManager.killSelector
        self.wmManager.passLevelToCurrentWm()
    def on_release_creator_button(self , gooCls):

        self.wmManager.wm = self.wmManager.gooCreator
        self.wmManager.wm.gooCls = gooCls
        self.wmManager.passLevelToCurrentWm()
