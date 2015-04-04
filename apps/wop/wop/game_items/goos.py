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
        goo_radius = self.__class__.gooRadius()

        posA = level.gameRender.world_point_to_canvas(pos-goo_radius)
        posB = level.gameRender.world_point_to_canvas(pos)
        cRad = level.gameRender.world_length_to_canvas(goo_radius)
        size = (2.0*cRad, 2.0*cRad)
        PushMatrix()
        rot = Rotate()
        rot.angle = angle
        #print goo.angle
        rot.axis = (0,0,1)
        rot.origin = posB
        Rectangle(texture=self.__class__.gooTexture(), 
                  pos=posA, size=size)
        PopMatrix()



    def render_tentative(self, level, pos, canBeAdded):
        pos = numpy.array(pos)
        gooRadius = self.__class__.gooRadius()
        posB = level.gameRender.world_point_to_canvas(pos)
        if canBeAdded:
            extendedRad = gooRadius*1.2
            posA = level.gameRender.world_point_to_canvas(pos-extendedRad)
            cExtendedRad = level.gameRender.world_length_to_canvas(extendedRad)
            size = (2.0*cExtendedRad, 2.0*cExtendedRad)
            e = Ellipse(pos=posA,size=size,color=Color(0,1,0,0.3))
            self.render_it(level, pos, 0.0)
        else :
            posA = level.gameRender.world_point_to_canvas(pos-gooRadius)
            self.render_it(level, pos, 0.0)
            cRad = level.gameRender.world_length_to_canvas(gooRadius)
            size = (2.0*cRad, 2.0*cRad)
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

    _gooImg = CoreImage.load("res/black_goo_128.png")
    _gooTexture = _gooImg.texture

    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    _gooRadius = 1.0
    _gooDist = 8.0 * _gooRadius

    @classmethod
    def playBuildSound(cls):
       BlackGoo._buildSound.play()

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
    _gooRadius = 1.5
    _gooDist = 8.0 * _gooRadius
    _buildSound = SoundLoader.load('res/sounds/discovery1.wav')
    @classmethod
    def playBuildSound(cls):
       GreenGoo._buildSound.play()

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
