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


class GooParam(object):
    def __init__(self,
        shape = 'ellipse', 
        gooSize = (2.0, 2.0),
        allowsRotation = True,
        friction = 10.0,
        density = 1.0,
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
        self.addAsJointDist = addAsJointDist
        if self.addAsJointDist is None:
            self.addAsJointDist = min(*self.gooSize)
        self.removable = removable
        self.connectsNonGoos = connectsNonGoos




class Goo(GameItem):
    __metaclass__ = ABCMeta
    def __init__(self):
        super(Goo, self).__init__()

    #@abstractmethod
    def couldBeAddedAsGoo(self, level, wpos):
        raise RuntimeError("")

    #@abstractmethod
    def couldBeAddedAsJoint(self, level, wpos):
        raise RuntimeError("")

    def renderJoint(self,gr, joint, otherGoo):
        pa = joint.anchorA
        pb = joint.anchorB
        canvasDraw =CanvasDraw()
        canvasDraw.drawSegment(pa, pb, color=(1,1,1),width=0.2)


    def localAnchor(self):
        return (0,0)

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
        #c = Color(1,1,1)
        goo_radius = self.__class__.gooRadius()

        posA = pos-goo_radius
        posB = pos

        size = (2.0*goo_radius, 2.0*goo_radius)
        PushMatrix()
        rot = Rotate()
        rot.angle = angle
        #print goo.angle
        rot.axis = (0,0,1)
        rot.origin = posB
        Rectangle(texture=self.__class__.gooTexture(), 
                  pos=posA, size=size,color=Color(1,1,1,1.0))
        PopMatrix()



    def render_tentative(self, level, pos, canBeAdded):
        pos = numpy.array(pos)
        gooRadius = self.__class__.gooRadius()
        posB = level.gameRender.world_point_to_canvas(pos)
        if canBeAdded:
            extendedRad = gooRadius*1.2
            posA = pos-extendedRad
            size = (2.0*extendedRad, 2.0*extendedRad)
            e = Ellipse(pos=posA,size=size,color=Color(0,1,0,0.3))
            self.render_it(level, pos, 0.0)
        else :
            posA = pos-gooRadius
            self.render_it(level, pos, 0.0)
            size = (2.0*gooRadius, 2.0*gooRadius)
            e = Ellipse(pos=posA,size=size,color=Color(1,0,0,0.3))
            

    def addToWorld(self, world, pos):
        radius = self.__class__.gooRadius()
        circle=b2FixtureDef(shape=b2CircleShape(radius=radius),density=1,friction=20)
        self.body = world.CreateBody(type=b2_dynamicBody,
                                        position=pos,
                                        fixtures=circle)
        self.body.userData = self


class BlackGoo(RoundGoo):
    print __file__
    _gooParam = GooParam()
    _gooImg = CoreImage.load("res/black_goo_128.png")
    _gooTexture = _gooImg.texture

    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    _gooRadius = 1.0
    _gooDist = 8.0 * _gooRadius

    def renderJoint(self,gr, joint, otherGoo):
        pa = joint.anchorA
        pb = joint.anchorB
        canvasDraw =CanvasDraw( )
        pl = [pa[0],pa[1], pb[0], pb[1]]
        Line(points=pl, width=0.35, color=Color(0.0,0.0,0.0))
        Line(points=pl, width=0.2, color=Color(0.2,0.2,0.2))
    @classmethod
    def playBuildSound(cls):
       BlackGoo._buildSound.play()

    @classmethod
    def param(cls):
       return BlackGoo._gooParam

    @classmethod
    def gooRadius(cls):
        return BlackGoo._gooRadius
    @classmethod
    def gooDistance(cls):
        return BlackGoo._gooDist
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
    _gooRadius = 1.5
    _gooDist = 8.0 * _gooRadius
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')

    def renderJoint(self,gr, joint, otherGoo):
        pa = joint.anchorA
        pb = joint.anchorB
        Line(points=[pa, pb], width=0.2, color=Color(*(0.2,0.6,0.2,0.5)))

    @classmethod
    def playBuildSound(cls):
       GreenGoo._buildSound.play()
    @classmethod
    def param(cls):
       return GreenGoo._gooParam
    @classmethod
    def gooRadius(cls):
        return GreenGoo._gooRadius

    @classmethod
    def gooDistance(cls):
        return GreenGoo._gooDist

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



    def render(self, level):
        pos = numpy.array(self.body.position)
        angle = degrees(self.body.angle)

        self.render_it(level, pos,angle)

    def render_it(self, level,  pos, angle):

        param = self.param()
        gooSize = param.gooSize


        PushMatrix()
        rot = Rotate()
        rot.angle = angle
        #print goo.angle
        rot.axis = (0,0,1)
        rot.origin = pos
        Rectangle(pos=pos, size=param.gooSize,color=Color(1,1,1,1.0),
                  texture=self.gooTexture())
        PopMatrix()



    def render_tentative(self, level, pos, canBeAdded):
        param = self.param()
        if canBeAdded:
            e = Rectangle(pos=pos,size=param.gooSize,color=Color(0,1,0,0.3))
            self.render_it(level, pos, 0.0)
        else :
            #posA = level.gameRender.world_point_to_canvas(pos-gooRadius)
            self.render_it(level, pos, 0.0)
            #cRad = level.gameRender.world_length_to_canvas(gooRadius)
            #size = (2.0*cRad, 2.0*cRad)
            e = Rectangle(pos=pos,size=param.gooSize,color=Color(1,0,0,0.3))
            

    def addToWorld(self, world, pos):
        param = self.param()
        sx,sy = param.gooSize
        assert sx == sy
        self.verts = [
            ( (0.0/5.0)*sx, (0.0/4.0)*sy),
            ( (5.0/5.0)*sx, (0.0/4.0)*sy),
            ( (4.0/5.0)*sx, (3.0/4.0)*sy),
            ( (1.0/5.0)*sx, (3.0/4.0)*sy),
            ( (0.0/5.0)*sx, (0.0/4.0)*sy)
        ]
        rad = (sx / 5.0)/2.0
        circlePos = (2.5/5.0)*sx , (4.0/5.0)*sy
        poly   = b2PolygonShape(vertices=self.verts)
        circle = b2CircleShape(radius=rad ,pos=circlePos)

        shapes = [poly,circle]

        fdef = b2FixtureDef(shape=poly,
            density=param.density,
            friction=param.friction
        )
        self.body = world.CreateBody(type=b2_dynamicBody,
                                        position=pos,
                                        shapes=shapes,
                                        shapeFixture=fdef)
        self.body.userData = self

    def localAnchor(self):
        param = self.param()
        sx,sy = param.gooSize
        return (0.5*sx, (4.5/5.0)*sy)
