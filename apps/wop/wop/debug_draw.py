from Box2D import *
import numpy
from kivy.graphics import *


class CanvasDraw(object):    
    def __init__(self):
        pass

    def drawSolidCiricle(self, center, radius, axis, color):
        center = (numpy.array(center)-radius)
        size = numpy.array([radius*2,radius*2])
        #print "color",color
        #with self.canvas:
        e = Ellipse(pos=center,size=size,color=Color(*color))

    def drawSegment(self,v1, v2, color,width=1.0):
        #v1 = (numpy.array(v1)+self.offset)*self.scale
        #v2 = (numpy.array(v2)+self.offset)*self.scale
        #with self.canvas:
        Line(points=[v1[0],v1[1],v2[0],v2[1]], width=width, color=Color(*color))

    def drawSolidPolygon(self,vertices, vertexCount, color):
        vertices = numpy.array(vertices)
        vertices[:,0] #+= self.offset[0]
        vertices[:,1] #+= self.offset[1]
        #vertices*=self.scale

        assert vertices.shape[0] ==vertexCount

        v = [] 
        indices = []
        for i in range(vertices.shape[0]):
            v.extend([vertices[i,0],vertices[i,1],0,0])
            indices.append(i)
        #with self.canvas:
        Mesh(vertices=v,indices=indices,mode='triangle_fan',color=Color(*color))



class DebugDraw(CanvasDraw):
    def __init__(self, world):
        super(DebugDraw, self).__init__()
        self.world = world

    def debugDraw(self):
        if self.world is not None:
            for body in self.world.bodies:
                fixtures = body.fixtures
                btype = body.type
                xf  =  body.transform
                for f in fixtures:
                    if body.active==False :
                        self.drawShape(f, xf, (0.5, 0.5, 0.3, 0.7) )
                    elif btype == b2_staticBody:
                        self.drawShape(f, xf, (0.5, 0.9, 0.5, 0.7) )
                    elif btype == b2_kinematicBody:
                        self.drawShape(f, xf, (0.5, 0.5, 0.5, 0.7) )
                    elif body.awake==False:
                        self.drawShape(f, xf, (0.6, 0.6, 0.6, 0.7) )
                    else :
                        self.drawShape(f, xf, (0.9, 0.7, 0.7, 0.7) )

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
                #=self.drawSolidCiricle(v1, 0.05,(1.0,0.0), color)
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

