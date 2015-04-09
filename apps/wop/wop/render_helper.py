import numpy
# Box2D
from Box2D import *
# kivy
from kivy.core.image import Image as CoreImage
from kivy.logger import Logger
from kivy.graphics import *
from wop import CanvasDraw, DebugDraw
from math import degrees



def renderDistanceJoint(joint, color=(1,1,1,1), width=0.3):
    pa = joint.anchorA
    pb = joint.anchorB
    pl = [pa[0],pa[1], pb[0], pb[1]]
    Line(points=pl, width=width, color=Color(*color))
    


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