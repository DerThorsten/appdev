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


import numpy

Builder.load_string("""
<LevelCanvasWidget>:
    #size_hint: (1, 1)
    BoxLayout:
        #size_hint: (1, 1)
        orientation: "horizontal" 
""")
class LevelCanvasWidget(BoxLayout):
    def __init__(self,*arg,**kwarg):
        Config.set("input", "mouse", "mouse,disable_multitouch")
        self.lastTouchPos = None
        super(LevelCanvasWidget,self).__init__(orientation="horizontal",*arg,**kwarg)

        self.scale_ = 40.0
        self.offset_ = numpy.array([10,0],dtype='float32')

        self.level = None            
        self.toRender = dict()
        self.roi = None


    def set_level(self, level):
        self.level = level
        self.roi = roi = level.roi

    def on_pre_leave(self):
        print "pre leave viewer"
    def on_leave(self):
        print "leave viewer"
        
    def on_pre_enter(self):
        print "pre enter viewer"
    def on_enter(self):
        print "enter viewer"
        self.roi = roi = self.level.roi
        lw,lh = roi[1][0] - roi[0][0],roi[1][1] - roi[0][1]
        w,h = self.width,self.height
        sw,sh = w/lw, h/lh

        print "lw,lh",lw,lh,"w,h",w,h,"sw,sh",sw,sh

        
        self.set_scale(max(sw,sh))
        self.set_offset(roi[0])
    def set_scale(self, scale):
        wc = self.wolrdCenterOfCanvas()
        self.scale_ = scale
        if self.level is not None:
            wc2 = numpy.array(self.wolrdCenterOfCanvas())
            self.set_offset(self.get_offset() + (wc2-wc))
    def get_scale(self):
        return self.scale_

    def wolrdCenterOfCanvas(self):
        return self.canvas_point_to_world((self.width/2.0, self.height/2.0))

    def visibleWorldWidth(self):
        return self.canvas_length_to_world(self.width)

    def visibleWorldHeight(self):
        return self.canvas_length_to_world(self.width)

    def visible_part_of_world(self):
        w = self.width
        h = self.height
        return (self.canvas_point_to_world(0,0),
                self.canvas_point_to_world(w,h))

    def set_offset(self, offset):
        self.offset_ = numpy.require(offset)
        vwW = self.visibleWorldWidth()
        canvasPixelSize = self.width, self.height
        canvasWorldSize = self.canvas_length_to_world(canvasPixelSize)

        #if self.roi is not None:
        #    # do not allow scrolling beyond left border
        #    #self.offset_[0] =  min(self.roi[0][0], self.offset_[0])
        #    #if self.offset_[0] + vwW  < self.roi[1][0]:
        #    #    self.offset_[0] = self.roi[1][0]-vwW
        #    #self.offset_[1] = max(self.roi[1][0]-self.visibleWorldWidth(),self.offset_[1])
        #print self.offset_[0] +vwW
        #if self.offset_[0] + vwW < self.roi[1][0]:
        #    print "OUTCH"

    def get_offset(self):
        return self.offset_


    def canvas_point_to_world(self, point,out=None):
        s = self.get_scale()
        o = self.get_offset()
        x,y = point 
        wx  = x/s - o[0]
        wy  = y/s - o[1]
        return (wx,wy)

    def canvas_length_to_world(self,length,out=None):
        s = self.get_scale()
        if isinstance(length,(list,tuple)):
            return [l/s for l in length]
        else : 
            return  length/s

    def world_point_to_canvas(self,point,out=None):
        s = self.get_scale()
        o = self.get_offset()
        x,y = point 
        cx  = (x+ o[0])*s
        cy  = (y+ o[1])*s
        return (cx, cy)

    def world_length_to_canvas(self,length,out=None):
        s = self.get_scale()
        if isinstance(length,(list,tuple)):
            return [l*s for l in length]
        else :
            return length*s


    def on_touch_down(self, touch):


        print "off ",self.get_offset(), "sc ",self.get_scale()
        print "cpos",touch.pos

 



        #return False
        hasButton = False
        if 'button' in touch.profile:
            hasButton = True
        if hasButton and touch.button == 'scrollup':
            self.set_scale(1.25*self.get_scale())
        elif hasButton and touch.button == 'scrolldown':
            os  = self.get_scale()
            ns = os/1.25
            if ns > 1.0:
                self.set_scale(ns)
        elif hasButton and touch.button == 'right':
            pass

        else :
            if self.level is not None:
                levelCb = self.level.world_on_touch_down
                wPos = self.canvas_point_to_world(touch.pos)
                r = levelCb(wPos , touch)
                print "wpos",wPos
    def on_touch_move(self, touch):

        hasButton = False
        if 'button' in touch.profile:
            hasButton = True

        if hasButton and touch.button == 'right':
            diff = (numpy.array(touch.ppos) - touch.pos)/self.get_scale()
            self.set_offset(self.get_offset() - diff)
        else :
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
        elif hasButton and touch.button == 'right':
            pass
        else :
            levelCb = self.level.world_on_touch_up
            wPos = self.canvas_point_to_world(touch.pos)
            r = levelCb(wPos , touch)   


                

    def render(self):

        sc = self.get_scale()
        o = self.get_offset().copy()
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
