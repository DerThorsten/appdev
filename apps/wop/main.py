'''
Bubble
======

Test of the widget Bubble.
'''
# kivy
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
from debug_draw import DebugDraw
from Box2D import *
from math import cos,sin,degrees

import numpy
import functools
import level


# 'rd'

class ResManager(object):
    def __init__(self, resolution='hd'):
        pass









class GameRendererWidget(BoxLayout):
    def __init__(self,*arg,**kwarg):
        self.lastTouchPos = None
        super(GameRendererWidget,self).__init__(orientation="horizontal",*arg,**kwarg)

        self.scale = 15.0
        self.offset = numpy.array([0,0],dtype='float32')
        # load level
        self.level = level.SimpleLevel(gameRender=self)
        self.level.initPhysics()
        self.level.start()


        self.world = self.level.world
        self.gooImg = CoreImage.load("res/pink_goo_128.png")
        self.gooTexture = self.gooImg.texture
        


        self.debugDraw = DebugDraw(world=self.world,widget=self, scale=self.scale, offset=self.offset)





        self.goos = []

    def setScale(self, scale):
        self.scale = scale
        self.debugDraw.scale = scale

    def getScale(self):
        return self.debugDraw.scale


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
        cx  = (x+ o[0])*scale
        cy  = (y+ o[1])*scale
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
            levelCb = self.level.world_on_touch_down
            wPos = self.canvas_point_to_world(touch.pos)
            r = levelCb(wPos , touch)

            circle=b2FixtureDef(shape=b2CircleShape(radius=1),
                                density=1,friction=20)

            gooBody = self.world.CreateBody(type=b2_dynamicBody,
                                            position=wPos,
                                            fixtures=circle)

            self.goos.append(gooBody)
    def on_touch_move(self, touch):
        levelCb = self.level.world_on_touch_move
        wPos = self.canvas_point_to_world(touch.pos)

        r = levelCb(wPos , touch)
        d = numpy.array(touch.pos) - numpy.array(touch.ppos)
        d /= self.debugDraw.scale
        self.debugDraw.offset += d
        self.offset = self.debugDraw.offset
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
                

    def wToS(c):
        return c



class CreateAndSelectWidget(BoxLayout):

    selectObjectButton = ObjectProperty(None)
    killObjectButton = ObjectProperty(None)
    blackGooButton = ObjectProperty(None)
    greenGooButton = ObjectProperty(None)
    redGooButton = ObjectProperty(None)
    pinkGooButton = ObjectProperty(None)

    def __init__(self,*arg,**kwarg):
        super(CreateAndSelectWidget,self).__init__(*arg, **kwarg)


class DrawPhysicsWidget(BoxLayout):
    viewer = ObjectProperty(None)
    zoomInButton = ObjectProperty(None)
    zoomIOutButton = ObjectProperty(None)
    def __init__(self,*arg,**kwarg):
        super(DrawPhysicsWidget,self).__init__(*arg, **kwarg)
        
      
        self.zoomOutButton.bind(on_release=lambda inst : self.zoomIn())
        self.zoomInButton.bind(on_release=lambda inst : self.zoomOut())

    def zoomIn(self):
        s = self.getScale()
        ns = s/1.25
        if ns > 1.0:
            self.setScale(ns)
    def zoomOut(self):
        s = self.getScale()
        self.setScale(s*1.25)
    def setScale(self, scale):
        self.viewer.setScale(scale)
        
    def getScale(self):
        return self.viewer.getScale()

    def update(self, dt):
        self.viewer.update(dt)


class WorldOfPhysicsApp(App):

    def build(self):
        bc =  DrawPhysicsWidget()
        Clock.schedule_interval(bc.update,1.0/50)
        return bc
        #return TheGame()
if __name__ == '__main__':
    WorldOfPhysicsApp().run()
