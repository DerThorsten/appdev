import numpy
from math import degrees
from abc import ABCMeta ,abstractmethod
# Box2D
import pybox2d as b2

# kivy
from kivy.core.image import Image as CoreImage
from game_item import GameItem
from kivy.logger import Logger
from kivy.graphics import *
from kivy.core.audio import SoundLoader
from wop import Singleton
from wop import CanvasDraw, DebugDraw
from wop import renderDistanceJoint,renderRectangle,renderDistanceJointTentative
from wop import FileTextures,getImage,registerImage

from collections import OrderedDict

@Singleton
class RegisteredGoos(object):
    def __init__(self):
        self.gooClsDict = OrderedDict()

    def register(self, gooCls, gooName):
        assert gooName not in self.gooClsDict
        self.gooClsDict[gooName] = gooCls

@Singleton
class GameResources(object):
    def __init__(self):
        self.resources = dict()


class GooParam(object):
    def __init__(self,
        shape = 'ellipse', 
        gooSize = (2.0, 2.0),
        allowsRotation = True,
        friction = 10.0,
        density = 1.0,
        linearDamping = 0.5,
        angularDamping = 0.2,
        gravityMultiplier = 1.0,
        minGooDist = 4.0,
        maxGooDist = 8.0,
        addIfAnyToClose = True,
        autoExpanding = True,
        expandingDist = None,
        frequencyHz = 4.0,
        dampingRatio = 0.8,
        maxEdges = 10,
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
        self.maxEdges = maxEdges
        self.minBuildEdges = minBuildEdges
        self.maxBuildEdges = maxBuildEdges
        self.canBeAddedAsJoint = canBeAddedAsJoint
        self.addAsJointRadius = addAsJointRadius
        self.addAsJointDist = addAsJointDist
        if self.addAsJointDist is None:
            self.addAsJointDist = min(*self.gooSize)
        self.removable = removable
        self.connectsNonGoos = connectsNonGoos

import matplotlib
from matplotlib import cm

class Joint(GameItem):
    __metaclass__ = ABCMeta
    def __init__(self):
        super(Joint, self).__init__()
        self.joint = None
        self.force = 0

        self.cm  = matplotlib.cm.ScalarMappable(norm=matplotlib.colors.Normalize(0,1),
                                                cmap='jet')

    @abstractmethod
    def add_to_level(self,level, gameItemA, gameItemB):
        pass

    def jointStress():
        return 0

    def render(self, gr):
        f =  self.jointStress()
        color = self.cm.to_rgba(f)

        renderDistanceJoint(self.joint,color=color)

    def render_tentative(self, gr, pA, pB):
        renderDistanceJointTentative(pA,pB)


    def breakJoint(self):
        return False


class GooJoint(Joint):
    def __init__(self):
        super(GooJoint, self).__init__()
    @abstractmethod
    def add_to_level(self,level, gameItemA, gameItemB):
        pass

    def breakJoint(self):
        return False


class GooDistanceJoint(Joint):
    def __init__(self,goAddedAsJoint=False):
        super(GooDistanceJoint, self).__init__()
        self.joint = None
        self.goAddedAsJoint = goAddedAsJoint
        self._jointStress = 0
        self._d = 0
    def add_to_level(self,level, gameItemA, gameItemB):
        gA = gameItemA
        gB = gameItemB
        world = level.world
        gooGraph = level.gooGraph
        assert isinstance(gA,GameItem)
        assert isinstance(gB,GameItem)

        # take param from first goo (so far)
        gParam  = gA.param()
        dfn=b2.distanceJointDef(
           frequencyHz=gParam.frequencyHz,
           dampingRatio=gParam.dampingRatio,
           bodyA=gA.body,bodyB=gB.body,
           localAnchorA=gA.localAnchor(),
           localAnchorB=gB.localAnchor()
        )


        self.joint = world.createJoint(dfn).asDistanceJoint()
        self.joint.userData = self
        if gParam.autoExpanding and self.goAddedAsJoint==False:
            self.joint.length = gParam.expandingDist
        else:
            pA  = gA.body.getWorldPoint(b2.vec2(gA.localAnchor()))
            pB  = gB.body.getWorldPoint(b2.vec2(gB.localAnchor()))
            d = (pA - pB).length
            self.joint.length = d
        # add edge to gooGraph
        level.game_items.add(self.joint)
        gooGraph.add_edge(gA, gB, joint=self.joint)
    def jointStress(self):
        return self._jointStress

    def currentLength(self):
        j = self.joint
        return (j.anchorA -  j.anchorB).length

    def breakJoint(self):
        j = self.joint
        l = j.length
        al = self.currentLength()
        d = al - l 
        if(d<=0):
            self._jointStress = 0
        else:
            self._jointStress = 1.0 - numpy.exp(-1.0*d)
            self._d = 0.7*self._d + 0.3*d

            if self._d/l >= 0.13:
                return True
        return False 


class GooBalloonJoint(Joint):
    def __init__(self):
        super(GooBalloonJoint, self).__init__()
        self.joint = None

    def add_to_level(self,level, gameItemA, gameItemB):
        gA = gameItemA
        gB = gameItemB
        world = level.world
        gooGraph = level.gooGraph
        assert isinstance(gA,BalloonGoo) or isinstance(gA,BalloonGoo2) 
        assert isinstance(gB,Goo)
        assert not isinstance(gB,BalloonGoo)

        ballonGoo = gameItemA
        nonBalloonGoo = gameItemB
        balloonBody = ballonGoo.body
        nonBalloonBody = nonBalloonGoo.body

        shape=b2.polygonShape(box=(0.1,0.1))
        fd=b2.fixtureDef(
                    shape=shape,
                    friction=0.2,
                    density=20,
                    shapeFilter=b2.shapeFilter(
                        categoryBits=0x0001,
                        maskBits=(0xFFFF & ~0x0002)
                    )
                    )


        startPos = nonBalloonBody.position
        endPos   = balloonBody.position
        N=100
        y=startPos.y
        x=startPos.x

        ropeLength = (startPos - endPos).length

        prevBody=gameItemB.body
        extraLength=0.01
        self.rd=rd=b2.ropeJointDef(
                            bodyA=gameItemA.body, 
                            bodyB=gameItemB.body,
                            maxLength=ropeLength,
                            localAnchorA=(0,0), 
                            localAnchorB=(0,0),
                            )
        self.joint=world.createJoint(rd)
        self.joint.userData=self
        level.game_items.add(self.joint)
        gooGraph.add_edge(gA, gB, joint=self.joint)

    def render(self, gr):
        renderDistanceJoint(self.joint)

    def render_tentative(self, gr, pA, pB):
        renderDistanceJointTentative(pA,pB)

class Goo(GameItem):
    __metaclass__ = ABCMeta
    def __init__(self):
        super(Goo, self).__init__()

        self.isKilled = False
        self.sizeMult = 1.0
    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(1,1,1,1), width=0.3)

    def localAnchor(self):
        return b2.vec2(0,0)

    def createJoint(self, goAddedAsJoint=False):
        return GooDistanceJoint(goAddedAsJoint=goAddedAsJoint)
    
class RoundGoo(Goo):
    #__metaclass__ = ABCMeta
    def __init__(self):
        super(RoundGoo, self).__init__()
        self.body = None

    def render(self, level):
        if not self.isKilled:
            pos = numpy.array(self.body.position)
            angle = degrees(self.body.angle)
            self.render_it(level, pos,angle)
        else:
            pos = self.pos
            angle = self.angle
            self.render_it(level, pos,angle)
            self.sizeMult*=0.95

    def render_it(self, level,  pos, angle, sizeMult=1.0):
        param = self.param()
        gooSize = b2.vec2(param.gooSize)*self.sizeMult
        renderRectangle(size=gooSize, pos=pos, 
                        angle=angle, texture=self.gooImage().texture,
                        shiftHalfSize=True)



    def render_tentative(self, level, pos, canBeAdded):
        size = b2.vec2(self.param().gooSize)
        color = (1,0,0,0.3)
        if canBeAdded:
            color = (0,1,0,0.3)
        self.render_it(level, pos, 0.0)
        e = Ellipse(pos=b2.vec2(pos)-size/2,size=size,color=Color(*color))

            

    def add_to_level(self, world, pos, angle=0.0, scale=1.0):
        param = self.param()
        assert param.gooSize[0] == param.gooSize[1]
        radius = param.gooSize[0]/2.0
        circle=b2.fixtureDef(shape=b2.circleShape(radius=radius),
                            density=param.density,
                            friction=param.friction)
        self.body = world.createBody(   b2.bodyDef(
                                            btype=b2.BodyTypes.dynamicBody,
                                            position=pos,
                                            angularDamping=param.angularDamping,
                                            linearDamping=param.linearDamping
                                        ),
                                        fixtures=circle,
                                        )
        self.body.userData = self




registerImage("blackGoo","res/black_goo_128.png")
class BlackGoo(RoundGoo):
    _gooParam = GooParam(removable=True)
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')

    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(0.2,0.2,0.2,1), width=0.3)

    @classmethod
    def playBuildSound(cls):
       BlackGoo._buildSound.play()

    @classmethod
    def param(cls):
       return BlackGoo._gooParam

    @classmethod
    def gooImage(cls):
        return getImage('blackGoo')

    def __init__(self):
        super(BlackGoo, self).__init__()

registerImage("greenGoo","res/green_goo_128.png")
class GreenGoo(RoundGoo):
    _gooParam = GooParam(autoExpanding=False)
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(0.2,1,0.2,1), width=0.3)

    @classmethod
    def playBuildSound(cls):
       GreenGoo._buildSound.play()
    @classmethod
    def param(cls):
       return GreenGoo._gooParam
    @classmethod
    def gooImage(cls):
        return getImage('greenGoo')
    def __init__(self):
        super(GreenGoo, self).__init__()

registerImage("anchorGoo","res/amboss_goo_128.png")
class AnchorGoo(Goo):
    
    _gooParam = GooParam(minBuildEdges=1,gooSize=(3,3), density=10,
                         autoExpanding=False,
                         canBeAddedAsJoint=False)
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(0.2,1,0.2,1), width=0.3)

    @classmethod
    def playBuildSound(cls):
       AnchorGoo._buildSound.play()

    def __init__(self):
        super(AnchorGoo, self).__init__()
        self.body = None
    @classmethod
    def playBuildSound(cls):
        pass
    @classmethod
    def param(cls):
       return AnchorGoo._gooParam

    @classmethod
    def gooImage(cls):
        return getImage('anchorGoo')

    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(0.2,0.1,0.2,1), width=0.3)

    def render(self, level):
        if not self.isKilled:
            self.render_it(level, self.body.position, degrees(self.body.angle))
        else:
            self.render_it(level, self.pos, degrees(self.angle))
            self.sizeMult*=0.95

    def render_it(self, level,  pos, angle):
        size = b2.vec2(self.param().gooSize)*self.sizeMult
        renderRectangle(size=size, pos=pos, 
                        angle=angle, texture=self.gooImage().texture)

    def render_tentative(self, level, pos, canBeAdded):
        param = self.param()
        if canBeAdded:
            e = Rectangle(pos=pos,size=param.gooSize,color=Color(0,1,0,0.3))
            self.render_it(level, pos, 0.0)
        else :
            self.render_it(level, pos, 0.0)
            e = Rectangle(pos=pos,size=param.gooSize,color=Color(1,0,0,0.3))
            

    def add_to_level(self, world, pos, angle=0.0, scale=1.0):
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
        poly   = b2.polygonShape(vertices=self.verts)
        circle = b2.circleShape(radius=rad ,pos=circlePos)

        fdef = b2.fixtureDef(density=param.density,
                            friction=param.friction)

        self.body = world.createBody(
                                     b2.bodyDef(
                                     btype=b2.BodyTypes.dynamicBody,
                                     position=pos,
                                     angularDamping=param.angularDamping,
                                     linearDamping=param.linearDamping
                                     ),
                                     shapes=[poly,circle],
                                     shapeFixture=fdef)
        self.body.userData = self

    def localAnchor(self):
        param = self.param()
        sx,sy = param.gooSize
        return (0.5*sx, (4.5/5.0)*sy)

registerImage("pinkGoo","res/pink_goo_128.png")
class BalloonGoo(Goo):
    
    _gooParam = GooParam(minBuildEdges=1,
                         maxBuildEdges=1,
                         gooSize=(3,3), density=2,
                         autoExpanding=False,
                         canBeAddedAsJoint=False,
                         maxEdges=1)
    
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(0.2,1,0.2,1), width=0.3)
    def __init__(self):
        super(BalloonGoo, self).__init__()
        self.body = None

    @classmethod
    def playBuildSound(cls):
       BalloonGoo._buildSound.play()


    @classmethod
    def playBuildSound(cls):
        pass
    @classmethod
    def param(cls):
       return BalloonGoo._gooParam

    @classmethod
    def gooImage(cls):
        return getImage('pinkGoo')

    #def renderJoint(self,gr, joint, otherGoo):
    #    renderDistanceJoint(joint, color=(0.2,0.1,0.2,1), width=0.3)

    def render(self, level):
        if not self.isKilled:
            self.render_it(level, self.body.position, degrees(self.body.angle))
        else:
            self.render_it(level, self.pos, self.angle)
            self.sizeMult*=0.95

    def render_it(self, level,  pos, angle):
        renderRectangle(size=b2.vec2(self.param().gooSize)*self.sizeMult, pos=pos, 
                        angle=angle, texture=self.gooImage().texture,
                        shiftHalfSize=True)

    def render_tentative(self, level, pos, canBeAdded):
        pos  =  b2.vec2(pos)
        param = self.param()
        size = b2.vec2(param.gooSize)
        if canBeAdded:
            e = Rectangle(pos=pos-size/2,size=param.gooSize,color=Color(0,1,0,0.3))
            self.render_it(level, pos, 0.0)
        else :
            self.render_it(level, pos, 0.0)
            e = Rectangle(pos=pos-size/2,size=param.gooSize,color=Color(1,0,0,0.3))
            

    def add_to_level(self, world, pos, angle=0.0, scale=1.0):
        param = self.param()
        assert param.gooSize[0] == param.gooSize[1]
        radius = param.gooSize[0]/2.0
        circle=b2.fixtureDef(shape=b2.circleShape(radius=radius),
                            density=param.density,
                            friction=param.friction)
        self.body = world.createBody(   
                                        b2.bodyDef(
                                        btype=b2.BodyTypes.dynamicBody,
                                        position=pos,
                                        angularDamping=param.angularDamping,
                                        linearDamping=param.linearDamping
                                        ),
                                        fixtures=circle,
                                        )
        self.body.gravityScale = -1.0
        self.body.userData = self

    #def localAnchor(self):
    #    param = self.param()
    #    sx,sy = param.gooSize
    #    return ()

    def createJoint(self):
        return GooBalloonJoint()




RegisteredGoos.Instance().register(BlackGoo,    'blackGoo')
RegisteredGoos.Instance().register(GreenGoo,    'greenGoo')
RegisteredGoos.Instance().register(AnchorGoo,   'anchroGoo')
RegisteredGoos.Instance().register(BalloonGoo,  'balloonGoo')

