import numpy
# Box2D
from Box2D import *
# kivy
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.graphics import *
from wop import CanvasDraw, DebugDraw
from math import degrees,atan2,pi



def renderDistanceJointTentative(pa, pb, color=(0.2,0.2,0.2,0.1), width=0.3):
    if True:
        pl = [pa[0],pa[1], pb[0], pb[1]]
        Line(points=pl, width=width, color=Color(*color))
    else:
        d = pb-pa
        a = atan2(d[1], d[0])+pi
        aDegrees = degrees(a)
        
        PushMatrix()
        rot = Rotate()
        rot.axis = (0,0,1)
        rot.origin = pa
        rot.angle = aDegrees+180

        nR = d.length/(2*pi)

        nrt = 10.0

        f = nR/nrt

        x = numpy.linspace(0,d.length, 500)
        y = numpy.sin(x/f)*0.5+pa[1]
        x += pa[0]

        pl = []
        for xx,yy in zip(x, y):
            pl.append(xx)
            pl.append(yy)
        Line(points=pl, width=0.1, color=Color(*color))

        PopMatrix()


def renderDistanceJoint(joint, color=(0.2,0.2,0.2,1), width=0.3):
    pa = joint.anchorA
    pb = joint.anchorB
    renderDistanceJointTentative(pa, pb,color,width)


def renderRectangle(size, pos, angle, texture, shiftHalfSize=False):
    PushMatrix()
    rot = Rotate()
    rot.angle = angle
    #print goo.angle
    rot.axis = (0,0,1)
    rot.origin = pos
    if shiftHalfSize :
        rpos = b2Vec2(pos) -b2Vec2(size)/2
    else:
        rpos = pos
    Rectangle(pos=rpos, size=size,color=Color(1,1,1,1.0),
              texture=texture)
    PopMatrix()
