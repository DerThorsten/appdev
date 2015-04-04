'''
Bubble
======

Test of the widget Bubble.
'''
# kivy
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

from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty

# mystuff
import world_helper as wh
from debug_draw import DebugDraw
from Box2D import *
from math import cos,sin,degrees

import numpy
import functools
import level

from wop.game_items import *



class GameRendererWidget(BoxLayout):
    def __init__(self,*arg,**kwarg):
        self.lastTouchPos = None
        super(GameRendererWidget,self).__init__(orientation="horizontal",*arg,**kwarg)

        self.scale = 15.0
        self.offset = numpy.array([0,0],dtype='float32')

        self.level = None            
        #self.world = self.level.world
        #self.gooImg = CoreImage.load("res/pink_goo_128.png")
        #self.gooTexture = self.gooImg.texture
        #self.debugDraw = DebugDraw(world=self.world,widget=self, scale=self.scale, offset=self.offset)

        self.toRender = dict()

    def set_level(self, level):
        self.level = level

    def setScale(self, scale):
        self.scale = scale
        #self.debugDraw.scale = scale

    def getScale(self):
        return self.scale


    def canvas_point_to_world(self, point,out=None):
        s = self.scale
        o = self.offset
        x,y = point 
        wx  = x/s - o[0]
        wy  = y/s - o[1]
        return (wx,wy)

    def canvas_length_to_world(self,length,out=None):
        return  length/self.scale

    def world_point_to_canvas(self,point,out=None):
        s = self.scale
        o = self.offset
        x,y = point 
        cx  = (x+ o[0])*self.scale
        cy  = (y+ o[1])*self.scale
        return (cx, cy)

    def world_length_to_canvas(self,length,out=None):
        return length*self.scale


    def on_touch_down(self, touch):
        #return False
        if touch.button == 'scrollup':
            self.setScale(1.25*self.getScale())
        elif touch.button == 'scrolldown':
            os  = self.getScale()
            ns = os/1.25
            if ns > 1.0:
                self.setScale(ns)
        else :
            if self.level is not None:
                levelCb = self.level.world_on_touch_down
                wPos = self.canvas_point_to_world(touch.pos)
                r = levelCb(wPos , touch)

            if False:
                circle=b2FixtureDef(shape=b2CircleShape(radius=1),
                                    density=1,friction=20)
                gooBody = self.world.CreateBody(type=b2_dynamicBody,
                                                position=wPos,
                                                fixtures=circle)
                self.goos.append(gooBody)
    def on_touch_move(self, touch):

        ppos = touch.ppos
        if self.level is not None:
            levelCb = self.level.world_on_touch_move
            wpos = self.canvas_point_to_world(touch.pos)
            wppos = self.canvas_point_to_world(ppos)
            r = levelCb(wpos, wppos , touch)

        #d = numpy.array(touch.pos) - numpy.array(ppos)
        #d /= self.scale
        #self.offset += d

    def on_touch_up(self, touch):
        if touch.button == 'scrollup':
            pass
        elif touch.button == 'scrolldown':
            pass
        else :
            levelCb = self.level.world_on_touch_up
            wPos = self.canvas_point_to_world(touch.pos)
            r = levelCb(wPos , touch)   

    def update(self, dt):
        if False:
            self.canvas.clear()
            #print "dt",dt,self.size
            self.debugDraw.debugDraw()
            scale = self.debugDraw.scale
            offset = self.debugDraw.offset
            with self.canvas:
                for goo in self.goos:

                    pos = numpy.array(goo.position)
                    posA = pos + offset - 1.0 
                    posA *= scale
                    posB = pos + offset
                    posB *= scale
                    size = (2.0*scale, 2.0*scale)
                    PushMatrix()
                    rot = Rotate()
                    rot.angle = degrees(goo.angle)
                    #print goo.angle
                    rot.axis = (0,0,1)
                    rot.origin = posB
                    Rectangle(texture=self.gooTexture, pos=posA, size=size)
                    PopMatrix()
                

    def render(self):
        toRender = self.toRender
        zValues = toRender.keys()
        sortedzValues = sorted(zValues)

        self.canvas.clear()
        with self.canvas:
            for z in sortedzValues:
                renderList = toRender[z]
                for renderItem in renderList:
                    renderItem()
        for z in zValues:
                toRender[z] = []

    def add_render_item(self, renderItem, z):
        if z in self.toRender :
            self.toRender[z].append(renderItem)
        else:
            self.toRender[z] = [renderItem]

    def wToS(c):
        return c


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
        body = wh.body_at_pos(self.level.world, pos=wpos)
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



SELECT = 1
CREATE_GOOS = 2
CREATE_BLACK_GOOS = 1
CREATE_GREEN_GOOS = 2

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
        Logger.debug("Selector Button: %s "%selectorType)
        if selectorType == "select":
            self.wmManager.wm = self.wmManager.simpleSelector
        elif selectorType == "kill":
            self.wmManager.wm = self.wmManager.killSelector
        self.wmManager.passLevelToCurrentWm()
    def on_release_creator_button(self , objectType):
        Logger.debug("Creator Button: %s "%objectType)
        if objectType == "black-goo":
            self.wmManager.wm = self.wmManager.blackGooCreator
        elif objectType == "green-goo":
            self.wmManager.wm = self.wmManager.greenGooCreator
        self.wmManager.passLevelToCurrentWm()


class DrawPhysicsWidget(BoxLayout):
    viewer = ObjectProperty(None)
    zoomInButton = ObjectProperty(None)
    zoomIOutButton = ObjectProperty(None)
    createAndSelectWidget = ObjectProperty(None)

    def __init__(self,*arg,**kwarg):
        super(DrawPhysicsWidget,self).__init__(*arg, **kwarg)
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
        return self.viewer.getScale()

    def update(self, dt):
        self.viewer.update(dt)


    def init_level(self):
        # load level
        self.level = level.SimpleLevel(gameRender=self.viewer)
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





class WorldOfPhysicsApp(App):

    def build(self):
        bc =  DrawPhysicsWidget()
        #Clock.schedule_interval(bc.update,1.0/50)

        bc.init_level()
        return bc
        #return TheGame()
if __name__ == '__main__':
    WorldOfPhysicsApp().run()
