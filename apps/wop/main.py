'''
Bubble
======

Test of the widget Bubble.
'''

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang import Builder
from kivy.uix.bubble import Bubble
from kivy.uix.widget import Widget
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.clock import Clock
from kivy.graphics import *
from kivy.core.image import Image as CoreImage

from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty

from Box2D import *
from math import cos,sin,degrees

import numpy
import functools

class DebugDraw(object):
    def __init__(self, world, widget, offset, scale):
        self.world = world
        self.widget = widget
        self.canvas = widget.canvas
        self.offset = offset
        self.scale = scale


    def debugDraw(self):

        self.canvas.clear()
        for body in self.world.bodies:
            fixtures = body.fixtures
            btype = body.type
            xf  =  body.transform
            for f in fixtures:
                if body.active==False :
                    self.drawShape(f, xf, (0.5, 0.5, 0.3) )
                elif btype == b2_staticBody:
                    self.drawShape(f, xf, (0.5, 0.9, 0.5) )
                elif btype == b2_kinematicBody:
                    self.drawShape(f, xf, (0.5, 0.5, 0.5) )
                elif body.awake==False:
                    self.drawShape(f, xf, (0.6, 0.6, 0.6) )
                else :
                    self.drawShape(f, xf, (0.9, 0.7, 0.7) )

        for joint in self.world.joints:
            self.drawJoint(joint)

        

    def drawShape(self,f,t,color):
        
        ftype = f.type
        shape = f.shape

        if ftype == b2Shape.e_circle :
            #print "circle"
            center = b2Mul(t, shape.pos)
            radius = shape.radius
            axis = b2Mul(t.q,(1.0,0.0))

            self.drawSolidCiricle(center, radius, axis, color)

        elif ftype == b2Shape.e_edge :
            #print "edge"
            v1 = b2Mul(t, shape.vertex1)
            v2 = b2Mul(t, shape.vertex2)
            self.drawSegment(v1, v2, color)

        elif ftype == b2Shape.e_chain :
            #print "chain"
            c = shape.vertexCount
            vertices = shape.vertices
            v1 = b2Mul(t, shape.vertices[0])
            for i in range(c):
                v2 = b2Mul(t, shape.vertices[i])
                self.drawSegment(v1, v2, color)
                self.drawSolidCiricle(v1, 0.05,(1.0,0.0), color)
        elif ftype == b2Shape.e_polygon :
            #print "polygon"
            c = shape.vertexCount
            vertices = shape.vertices
            assert len(vertices) == c
            verts = []
            for i in range(c):
                r = b2Mul(t, vertices[i])
                verts.append(r)
            self.drawSolidPolygon(verts,c,color)


    def drawJoint(self, joint):
        jtype = joint.type 

        bodyA = joint.bodyA
        bodyB = joint.bodyB
        tA = bodyA.transform
        tB = bodyB.transform
        xa = tA.position
        xb = tB.position
        pa = joint.anchorA
        pb = joint.anchorB

        color = (0.5, 0.8, 0.8)

        if(isinstance(joint,b2RopeJoint)):
            pass
        elif(isinstance(joint,b2DistanceJoint)):
            self.drawSegment(pa, pb, color)
        elif(isinstance(joint,b2PulleyJoint)):
            gA = joint.groundAnchorA
            gB = joint.groundAnchorA
            self.drawSegment(gA, pA, color)
            self.drawSegment(gB, pB, color)
            self.drawSegment(gA, gB, color)
        elif(isinstance(joint,b2MouseJoint)):
            pass
        else:
            self.drawSegment(xA, pA, color)
            self.drawSegment(pA, pB, color)
            self.drawSegment(xB, pB, color)

    def drawSolidCiricle(self, center, radius, axis, color):
        center = (numpy.array(center)-radius+self.offset)*self.scale
        size = numpy.array([radius*2,radius*2])*self.scale
        #print "color",color
        with self.canvas:
            e = Ellipse(pos=center,size=size,color=Color(*color))

    def drawSegment(self,v1, v2, color):
        v1 = (numpy.array(v1)+self.offset)*self.scale
        v2 = (numpy.array(v2)+self.offset)*self.scale
        with self.canvas:
            Line(points=[v1[0],v1[1],v2[0],v2[1]], width=1.5, color=Color(*color))

    def drawSolidPolygon(self,vertices, vertexCount, color):
        vertices = numpy.array(vertices)
        vertices[:,0] += self.offset[0]
        vertices[:,1] += self.offset[1]
        vertices*=self.scale

        assert vertices.shape[0] ==vertexCount

        v = [] 
        indices = []
        for i in range(vertices.shape[0]):
            v.extend([vertices[i,0],vertices[i,1],0,0])
            indices.append(i)
        with self.canvas:
            Mesh(vertices=v,indices=indices,mode='triangle_fan',color=Color(*color))


class SelectGooBubble(Bubble):
    pass


class DrawRawPhysicsWidget(BoxLayout):
    def __init__(self,*arg,**kwarg):
        self.lastTouch = None
        super(DrawRawPhysicsWidget,self).__init__(orientation="horizontal",*arg,**kwarg)


        self.gooImg = CoreImage.load("res/pink_goo_128.png")
        self.gooTexture = self.gooImg.texture
        self.world = b2World((0.0,-10.0))

        scale = 30.0
        offset = numpy.array([15,5],dtype='float32')
        self.debugDraw = DebugDraw(world=self.world,widget=self, scale=scale, offset=offset)

        # Tell the framework we're going to use contacts, so keep track of them
        # every Step.
        self.using_contacts=True

        # Ground body
        world=self.world
        ground = world.CreateBody(
                    shapes=b2EdgeShape( vertices=[(-50,0),(50,10)],)
                )


        self.world.DebugDraw = self.debugDraw
        self.goos = []

    def setScale(self, scale):
        self.debugDraw.scale = scale

    def getScale(self):
        return self.debugDraw.scale

    def on_touch_down(self, touch):
        print "self.size",self.size
        print "contains"
        self.lastTouchPos = touch.pos

        x = touch.pos[0]/self.debugDraw.scale - self.debugDraw.offset[0]
        y = touch.pos[1]/self.debugDraw.scale - self.debugDraw.offset[1]

        circle=b2FixtureDef(
                shape=b2CircleShape(radius=1),
                density=1,
                friction=20
                )

        gooBody = self.world.CreateBody(
                    type=b2_dynamicBody,
                    position=(x,y),
                    fixtures=circle,
                )

        self.goos.append(gooBody)
    def on_touch_move(self, touch):
        print "move"
        if self.lastTouchPos is not None:
            print "move"
            d = numpy.array(touch.pos) - self.lastTouchPos
            d /= self.debugDraw.scale
            self.lastTouchPos = touch.pos
            self.debugDraw.offset += d
    def on_touch_up(self, touch):
        self.lastTouchPos = touch.pos    

    def update(self, dt):
        self.canvas.clear()
        #print "dt",dt,self.size
        self.world.Step(dt,5,5)
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


class DrawPhysicsWidget(BoxLayout):
    viewer = ObjectProperty(None)
    zoomInButton = ObjectProperty(None)
    zoomIOutButton = ObjectProperty(None)
    def __init__(self,*arg,**kwarg):
        self.lastTouch = None
        super(DrawPhysicsWidget,self).__init__(orientation='vertical')
        
      
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
if __name__ == '__main__':
    WorldOfPhysicsApp().run()
