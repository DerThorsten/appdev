import numpy
from math import degrees
from abc import ABCMeta ,abstractmethod
# Box2D
from Box2D import *

# kivy
from kivy.core.image import Image as CoreImage
from game_item import GameItem
from kivy.logger import Logger
from kivy.graphics import *
from kivy.core.audio import SoundLoader

from wop import CanvasDraw, DebugDraw
from wop import renderDistanceJoint,renderRectangle

class GooParam(object):
    def __init__(self,
        shape = 'ellipse', 
        gooSize = (2.0, 2.0),
        allowsRotation = True,
        friction = 10.0,
        density = 1.0,
        linearDamping = 0.1,
        angularDamping = 0.2,
        gravityMultiplier = 1.0,
        minGooDist = 4.0,
        maxGooDist = 8.0,
        addIfAnyToClose = True,
        autoExpanding = True,
        expandingDist = None,
        frequencyHz = 2.0,
        dampingRatio = 0.1,
        minBuildEdges = 2,
        maxBuildEdges = 5,
        canBeAddedAsJoint = True,
        addAsJointRadius = 6.0,
        addAsJointDist = None,
        removable = False,
        connectsNonGoos = False
    ):

        # graph Param
        self.shape = shape
        self.gooSize = gooSize
        self.allowsRotation = allowsRotation
        self.friction = friction
        self.density = density
        self.linearDamping = linearDamping
        self.angularDamping = angularDamping
        self.gravityMultiplier = gravityMultiplier
        self.minGooDist = minGooDist
        self.maxGooDist = maxGooDist
        self.addIfAnyToClose = addIfAnyToClose
        self.autoExpanding = autoExpanding
        self.expandingDist = expandingDist
        if self.expandingDist is None:
            self.expandingDist = self.maxGooDist

        self.frequencyHz = frequencyHz
        self.dampingRatio = dampingRatio
        self.minBuildEdges = minBuildEdges
        self.maxBuildEdges = maxBuildEdges
        self.canBeAddedAsJoint = canBeAddedAsJoint
        self.addAsJointRadius = addAsJointRadius
        self.addAsJointDist = addAsJointDist
        if self.addAsJointDist is None:
            self.addAsJointDist = min(*self.gooSize)
        self.removable = removable
        self.connectsNonGoos = connectsNonGoos





class Goo(GameItem):
    __metaclass__ = ABCMeta
    def __init__(self):
        super(Goo, self).__init__()

    def renderJoint(self,gr, joint, otherGoo):
        renderDistanceJoint(joint, color=(1,1,1,1), width=0.3)

    def localAnchor(self):
        return b2Vec2(0,0)

class RoundGoo(Goo):
    #__metaclass__ = ABCMeta
    def __init__(self):
        super(RoundGoo, self).__init__()
        self.body = None

    @classmethod
    def gooTexture(cls):
        raise RuntimeError("child class gooTexture should be called")



    def render(self, level):
        pos = numpy.array(self.body.position)
        angle = degrees(self.body.angle)

        self.render_it(level, pos,angle)

    def render_it(self, level,  pos, angle):
        param = self.param()
        gooSize = b2Vec2(param.gooSize)
        renderRectangle(size=param.gooSize, pos=pos, 
                        angle=angle, texture=self.gooTexture(),
                        shiftHalfSize=True)



    def render_tentative(self, level, pos, canBeAdded):
        size = b2Vec2(self.param().gooSize)
        color = (1,0,0,0.3)
        if canBeAdded: color = (0,1,0,0.3)
        self.render_it(level, pos, 0.0)
        e = Ellipse(pos=b2Vec2(pos)-size/2,size=size,color=Color(*color))

            

    def addToWorld(self, world, pos):
        param = self.param()
        assert param.gooSize[0] == param.gooSize[1]
        radius = param.gooSize[0]/2.0
        circle=b2FixtureDef(shape=b2CircleShape(radius=radius),
                            density=param.density,
                            friction=param.friction)
        self.body = world.CreateBody(type=b2_dynamicBody,
                                        position=pos,
                                        fixtures=circle,
                                        angularDamping=param.angularDamping,
                                        linearDamping=param.linearDamping)
        self.body.userData = self


class BlackGoo(RoundGoo):
    print __file__
    _gooParam = GooParam()
    _gooImg = CoreImage.load("res/black_goo_128.png")
    _gooTexture = _gooImg.texture
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')

    def renderJoint(self,gr, joint, otherGoo):
        renderDistanceJoint(joint, color=(0.2,0.2,0.2,1), width=0.3)

    @classmethod
    def playBuildSound(cls):
       BlackGoo._buildSound.play()

    @classmethod
    def param(cls):
       return BlackGoo._gooParam

    @classmethod
    def gooTexture(cls):
        return BlackGoo._gooTexture

    def __init__(self):
        super(BlackGoo, self).__init__()

class GreenGoo(RoundGoo):
    print __file__
    _gooImg = CoreImage.load("res/green_goo_128.png")
    _gooTexture = _gooImg.texture
    _gooParam = GooParam()
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    def renderJoint(self,gr, joint, otherGoo):
        renderDistanceJoint(joint, color=(0.2,1,0.2,1), width=0.3)

    @classmethod
    def playBuildSound(cls):
       GreenGoo._buildSound.play()
    @classmethod
    def param(cls):
       return GreenGoo._gooParam
    @classmethod
    def gooTexture(cls):
        return GreenGoo._gooTexture

    def __init__(self):
        super(GreenGoo, self).__init__()


class AnchorGoo(Goo):
    
    _gooParam = GooParam(minBuildEdges=1,gooSize=(3,3), density=1000,
                         autoExpanding=False)
    _gooImg = CoreImage.load("res/amboss_goo_128.png")
    _gooTexture = _gooImg.texture

    def __init__(self):
        super(Goo, self).__init__()
        self.body = None
    @classmethod
    def playBuildSound(cls):
        pass
    @classmethod
    def param(cls):
       return AnchorGoo._gooParam

    @classmethod
    def gooTexture(cls):
        return AnchorGoo._gooTexture

    def renderJoint(self,gr, joint, otherGoo):
        renderDistanceJoint(joint, color=(0.2,0.1,0.2,1), width=0.3)

    def render(self, level):
        self.render_it(level, self.body.position, degrees(self.body.angle))

    def render_it(self, level,  pos, angle):
        renderRectangle(size=self.param().gooSize, pos=pos, 
                        angle=angle, texture=self.gooTexture())

    def render_tentative(self, level, pos, canBeAdded):
        param = self.param()
        if canBeAdded:
            e = Rectangle(pos=pos,size=param.gooSize,color=Color(0,1,0,0.3))
            self.render_it(level, pos, 0.0)
        else :
            self.render_it(level, pos, 0.0)
            e = Rectangle(pos=pos,size=param.gooSize,color=Color(1,0,0,0.3))
            

    def addToWorld(self, world, pos):
        param = self.param()
        sx,sy = param.gooSize
        assert sx == sy
        self.verts = [
            ( (0.0/5.0)*sx, (0.0/4.0)*sy),
            ( (5.0/5.0)*sx, (0.0/4.0)*sy),
            ( (4.0/5.0)*sx, (3.5/4.0)*sy),
            ( (1.0/5.0)*sx, (3.5/4.0)*sy),
            ( (0.0/5.0)*sx, (0.0/4.0)*sy)
        ]
        rad = (sx / 5.0)/2.0
        circlePos = (2.5/5.0)*sx , (4.5/5.0)*sy
        poly   = b2PolygonShape(vertices=self.verts)
        circle = b2CircleShape(radius=rad ,pos=circlePos)

        fdef = b2FixtureDef(density=param.density,
                            friction=param.friction)

        self.body = world.CreateBody(type=b2_dynamicBody,
                                     position=pos,
                                     shapes=[poly,circle],
                                     shapeFixture=fdef,
                                     angularDamping=param.angularDamping,
                                     linearDamping=param.linearDamping)

        self.body.userData = self

    def localAnchor(self):
        param = self.param()
        sx,sy = param.gooSize
        return (0.5*sx, (4.5/5.0)*sy)
