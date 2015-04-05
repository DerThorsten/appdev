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
from wop import DebugDraw
from Box2D import *
from math import cos,sin,degrees

import numpy
import functools
import level as all_level

from wop.game_items import *



class GameRendererWidget(BoxLayout):
    def __init__(self,*arg,**kwarg):
        self.lastTouchPos = None
        super(GameRendererWidget,self).__init__(orientation="horizontal",*arg,**kwarg)

        self.scale_ = 15.0
        self.offset_ = numpy.array([10,0],dtype='float32')

        self.level = None            
        #self.world = self.level.world
        #self.gooImg = CoreImage.load("res/pink_goo_128.png")
        #self.gooTexture = self.gooImg.texture
        #self.debugDraw = DebugDraw(world=self.world,widget=self, scale=self.scale, offset=self.offset)

        self.toRender = dict()
        self.roi = None
    def set_level(self, level):
        self.level = level
        self.roi = roi = level.roi


    def on_enter(self):
        print "enter viewer"
        self.roi = roi = self.level.roi
        lw,lh = roi[1][0] - roi[0][0],roi[1][1] - roi[0][1]
        w,h = self.width,self.height
        sw,sh = w/lw, h/lh

        print "lw,lh",lw,lh,"w,h",w,h,"sw,sh",sw,sh

        self.setOffset(roi[0])
        self.setScale(min(sw,sh))

    def setScale(self, scale):
        wc = self.wolrdCenterOfCanvas()
        self.scale_ = scale
        if self.level is not None:
            wc2 = numpy.array(self.wolrdCenterOfCanvas())
            self.setOffset(self.getOffset() + (wc2-wc))
    def getScale(self):
        return self.scale_

    def wolrdCenterOfCanvas(self):
        return self.canvas_point_to_world((self.width/2.0, self.height/2.0))

    def setOffset(self, offset):
        self.offset_ = numpy.require(offset)

        canvasPixelSize = self.width, self.height
        canvasWorldSize = self.canvas_length_to_world(canvasPixelSize)

        #if self.roi is not None:
        #   self.offset_[0] =  min(self.roi[0][0], self.offset_[0])
        #   self.offset_[1] =  min(self.roi[0][1], self.offset_[1])

    def getOffset(self):
        return self.offset_


    def canvas_point_to_world(self, point,out=None):
        s = self.getScale()
        o = self.getOffset()
        x,y = point 
        wx  = x/s - o[0]
        wy  = y/s - o[1]
        return (wx,wy)

    def canvas_length_to_world(self,length,out=None):
        s = self.getScale()
        if isinstance(length,(list,tuple)):
            return [l/s for l in length]
        else : 
            return  length/s

    def world_point_to_canvas(self,point,out=None):
        s = self.getScale()
        o = self.getOffset()
        x,y = point 
        cx  = (x+ o[0])*s
        cy  = (y+ o[1])*s
        return (cx, cy)

    def world_length_to_canvas(self,length,out=None):
        s = self.getScale()
        if isinstance(length,(list,tuple)):
            return [l*s for l in length]
        else :
            return length*s


    def on_touch_down(self, touch):
        print "off ",self.getOffset(), "sc ",self.getScale()
        print "cpos",touch.pos

 



        #return False
        hasButton = False
        if 'button' in touch.profile:
            hasButton = True
        if hasButton and touch.button == 'scrollup':
            self.setScale(1.25*self.getScale())
        elif hasButton and touch.button == 'scrolldown':
            os  = self.getScale()
            ns = os/1.25
            if ns > 1.0:
                self.setScale(ns)
        else :
            if self.level is not None:
                levelCb = self.level.world_on_touch_down
                wPos = self.canvas_point_to_world(touch.pos)
                r = levelCb(wPos , touch)
                print "wpos",wPos
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
        hasButton = False
        if 'button' in touch.profile:
            hasButton = True
        if hasButton and touch.button == 'scrollup':
            pass
        elif hasButton and touch.button == 'scrolldown':
            pass
        else :
            levelCb = self.level.world_on_touch_up
            wPos = self.canvas_point_to_world(touch.pos)
            r = levelCb(wPos , touch)   


                

    def render(self):

        sc = self.getScale()
        o = self.getOffset().copy()
        o*=sc
        #o = tuple(o)
        toRender = self.toRender
        zValues = toRender.keys()
        sortedzValues = sorted(zValues)

        self.canvas.clear()
        
        for z in sortedzValues:
            renderList = toRender[z]
            with self.canvas:

                PushMatrix()
                t = Translate()
                t.xy = o

                s = Scale()
                s.xyz = [sc,sc,1.0]

                for renderItem in renderList:
                    renderItem()

                PopMatrix()

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
        print self.pos,self.size
        return self.viewer.getScale()




    def init_level(self):
        # load level
        self.level = all_level.SimpleLevel(gameRender=self.viewer)
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




class LevelSelectorWidget(BoxLayout):
    screen_manager = ObjectProperty(None)


class MainMenuWidget(BoxLayout):
    pass

class MainSettingWidget(BoxLayout):
    pass

class ScreenSelectorWidget(BoxLayout):
    drawPysicsWidget = ObjectProperty(None)
    screen_manager = ObjectProperty(None)
    def __init__(self,*args,**kwargs):
        super(ScreenSelectorWidget,self).__init__(*args,**kwargs)


class WorldOfPhysicsApp(App):

    def build(self):
        if False:
            bc =  DrawPhysicsWidget()

            bc.init_level()
            return bc
            #return TheGame()
        else:
            screenSelectorWidget = ScreenSelectorWidget()
            screenSelectorWidget.drawPysicsWidget.init_level()
            return screenSelectorWidget
if __name__ == '__main__':
    WorldOfPhysicsApp().run()
