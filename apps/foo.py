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
from kivy.clock import Clock
from kivy.graphics import *
from Box2D import *
from math import cos,sin

import numpy


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

        #cc = InstructionGroup()
        #cc.add(Color(1,0,0,1))
        #cc.add(Ellipse(pos=center, size=size))
        ## Here, self should be a Widget or subclass
        #[self.canvas.add(group) for group in [cc]]

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


class DrawRawPhysicsWidget(BoxLayout):
    def __init__(self):
        self.lastTouch = None

        super(DrawRawPhysicsWidget,self).__init__()

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
                    shapes=b2EdgeShape( vertices=[(-50,0),(50,0)],)
                )

        xlow, xhi = -5, 5
        ylow, yhi = 2, 35
        random_vector = lambda: b2Vec2(b2Random(xlow, xhi), b2Random(ylow, yhi))

        # Small triangle
        triangle=b2FixtureDef(
                shape=b2PolygonShape(vertices= [(-1,0),(1,0),(0,2)]),
                density=1,
                )

        world.CreateBody(
                type=b2_dynamicBody,
                position=random_vector(),
                fixtures=triangle,
                )

        # Large triangle (recycle definitions)
        triangle.shape.vertices = [2.0*b2Vec2(v) for v in triangle.shape.vertices]

        trianglebody=world.CreateBody(
                type=b2_dynamicBody,
                position=random_vector(),
                fixtures=triangle,
                fixedRotation=True, # <-- note that the large triangle will not rotate
                )

        # Small box
        box=b2FixtureDef(
                shape=b2PolygonShape(box=(1, 0.5)),
                density=1,
                restitution=0.1,
                )

        world.CreateBody(
                type=b2_dynamicBody,
                position=random_vector(),
                fixtures=box,
                )

        # Large box
        box.shape.box = (2, 1)
        world.CreateBody(
                type=b2_dynamicBody,
                position=random_vector(),
                fixtures=box,
            )

        # Small circle
        circle=b2FixtureDef(
                shape=b2CircleShape(radius=1),
                density=1,
                )

        world.CreateBody(
                    type=b2_dynamicBody,
                    position=random_vector(),
                    fixtures=circle,
                )

        # Large circle
        circle.shape.radius *= 2
        world.CreateBody(
                    type=b2_dynamicBody,
                    position=random_vector(),
                    fixtures=circle,
                )


        self.world.DebugDraw = self.debugDraw

    def setScale(self, scale):
        self.debugDraw.scale = scale

    def getScale(self):
        return self.debugDraw.scale

    def on_touch_down(self, touch):
        self.lastTouchPos = touch.pos
    def on_touch_move(self, touch):
        d = numpy.array(touch.pos) - self.lastTouchPos
        d /= self.debugDraw.scale
        self.lastTouchPos = touch.pos
        self.debugDraw.offset += d
    def on_touch_up(self, touch):
        self.lastTouchPos = touch.pos    
    def update(self, dt):

        #print "dt",dt,self.size
        self.world.Step(dt,5,5)
        self.debugDraw.debugDraw()

    def wToS(c):
        return c


class DrawPhysicsWidget(BoxLayout):
    def __init__(self):
        self.lastTouch = None
        super(DrawPhysicsWidget,self).__init__(orientation='vertical')

        self.viewer =  DrawRawPhysicsWidget()
        self.add_widget(self.viewer)

        self.ctrlLayer = BoxLayout(orientation='horizontal')
        self.add_widget(self.ctrlLayer)

        self.zoomOutButton = Button(text='-',size_hint=(1,0.1))
        def cb(instance):
            print self.getScale()
            s = self.getScale()
            ns = s/1.25
            if ns > 1.0:
                self.setScale(ns)
        self.zoomOutButton.bind(on_release=cb)
        self.ctrlLayer.add_widget(self.zoomOutButton)


        self.zoomInButton = Button(text='+',size_hint=(1,0.1))
        def cb(instance):
            print self.getScale()
            s = self.getScale()
            self.setScale(s*1.25)
        self.zoomInButton.bind(on_release=cb)
        self.ctrlLayer.add_widget(self.zoomInButton)


    def setScale(self, scale):
        self.viewer.setScale(scale)
        
    def getScale(self):
        return self.viewer.getScale()

    def update(self, dt):
        self.viewer.update(dt)

class TestBubbleApp(App):

    def build(self):
        bc =  DrawPhysicsWidget()
        Clock.schedule_interval(bc.update,1.0/50)
        return bc
if __name__ == '__main__':
    TestBubbleApp().run()
