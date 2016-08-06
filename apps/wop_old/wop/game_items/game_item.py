from abc import ABCMeta ,abstractmethod
from Box2D import *
from kivy.logger import Logger
from kivy.core.image import Image as CoreImage
from wop import CanvasDraw
from kivy.graphics import Rectangle,Color
from wop import renderDistanceJoint,renderRectangle
from math import degrees
from wop.game_items import *
import numpy 
from kivy.graphics import Line,Mesh
from kivy.clock import Clock

class GameItem(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass
    def world_on_touch_down(self, wpos, touch):
        Logger.debug("GameItem down")
    def world_on_touch_move(self, wpos, wppos, touch):
        Logger.debug("GameItem move")
    def world_on_touch_up(self, wpos, touch):
        Logger.debug("GameItem   up")


    #@abstractmethod
    def add_to_level(self, world, pos, angle, scale):
        pass


    def remove_from_world(self):
        pass


class GooDestroyerItem(GameItem):
    def __init__(self):
        super(GooDestroyerItem,self).__init__()
        self.body = None

class StaticBlock(GameItem):
    blockImg = CoreImage.load("res/Brick_Block.png")
    blockTexture = blockImg.texture

    def __init__(self, size):
        super(StaticBlock, self).__init__()
        self.body = None
        self.size = b2Vec2(size)
    def add_to_level(self,level, pos, angle=0.0):
        world = level.world
        # Create a dynamic body
        size = self.size
        self.pos = b2Vec2(pos)+size/2.0
        self.body=world.CreateStaticBody(position=self.pos, angle=angle)
        # And add a box fixture onto it (with a nonzero density, so it will move)
        self.body.CreatePolygonFixture(box=size/2.0,friction=0.3)
        self.body.userData = self
        self.renderPos = self.pos-self.size/2.0
    def add_to_render_queue(self, gr):
        def render_it():
            Rectangle(pos=self.renderPos, size=self.size,color=Color(1,1,1,1.0),
              texture=StaticBlock.blockTexture)
        gr.add_render_item(render_it,1)


class RotatingKiller(GooDestroyerItem):
    blockImg = CoreImage.load("res/Brick_Block.png")
    blockTexture = blockImg.texture

    def __init__(self, size):
        super(RotatingKiller, self).__init__()
        self.body = None
        self.size = b2Vec2(size)
    def add_to_level(self,level, pos, angle=45.0):
        world = level.world
        # Create a dynamic body
        size = self.size
        self.pos = b2Vec2(pos)+size/2.0
        self.body=world.CreateDynamicBody(
                                          position=self.pos, 
                                          fixtures=b2FixtureDef(
                                          shape=b2PolygonShape(box=size/2.0),
                                          density=0.1)
        )
        # And add a box fixture onto it (with a nonzero density, so it will move)
        #self.body.CreatePolygonFixture(box=size/2.0,friction=0.3)
        self.body.userData = self
        self.renderPos = self.pos-self.size/2.0

    

        rjd=b2RevoluteJointDef(
                bodyA=level.groundBody,
                bodyB=self.body,
                localAnchorA=self.body.position,
                localAnchorB=(-0,0),
                enableMotor=True,
                #enableLimit=True,
                maxMotorTorque=10000,
                motorSpeed=0,
                #lowerAngle=-30.0 * b2_pi / 180.0,
                #upperAngle=5.0 * b2_pi / 180.0,
        )
            
        j = world.CreateJoint(rjd)
        j.motorSpeed = 2

    def add_to_render_queue(self, gr):
        def render_it():
            pos = self.body.position#-self.size/2.0
            renderRectangle(size=self.size,pos=pos,texture=RotatingKiller.blockTexture,
                            angle = degrees(self.body.angle),
                            shiftHalfSize=True)

        gr.add_render_item(render_it,1)

class ZigZackDestroyer(GooDestroyerItem):
    def __init__(self, size, orientation='horizontal',ticks=None):
        super(ZigZackDestroyer, self).__init__()
        self.body = None
        self.size = b2Vec2(size)
        self.ticks = ticks
        self.orientation = orientation
    def add_to_level(self,level, pos, angle=0.0):
        world = level.world
        # Create a dynamic body
        size = self.size
        self.pos = b2Vec2(pos)
        self.body=world.CreateStaticBody(position=self.pos+size/2.0, angle=angle)
        # And add a box fixture onto it (with a nonzero density, so it will move)
        self.body.CreatePolygonFixture(box=size/2.0,friction=0.3)
        self.body.userData = self
        self.renderPos = self.pos-self.size/2.0

        if self.orientation == 'horizontal':
            if self.ticks is None:
                self.ticks = int(self.size.x+0.5)
            x = numpy.linspace(self.pos.x,self.pos.x+self.size.x,self.ticks)
            y = numpy.zeros(x.shape[0])
            y[::2] = 2
            y+=self.pos.y
        elif self.orientation == 'vertical':
            if self.ticks is None:
                self.ticks = int(self.size.y+0.5)
            y = numpy.linspace(self.pos.y,self.pos.y+self.size.y,self.ticks)
            x = numpy.zeros(y.shape[0])
            x[::2] = 2
            x+=self.pos.x



        plist = []
        indices = []
        i=0
        for xx,yy in zip(x,y):
            plist.append(xx)
            plist.append(yy)
            indices.append(i)
            i+=1
        self.plist = plist
        


    def add_to_render_queue(self, gr):
        def render_it():
            Line(points=self.plist, width=0.3, color=Color(1.0,0.2,0.2,1))
        gr.add_render_item(render_it,1)



class GoalItem(GameItem):
    def __init__(self):
        super(GoalItem, self).__init__()
        self.size = b2Vec2(10,10)
        self.sensorBody = None
        self.inGoalGoos = set()
    def add_to_level(self,level, pos, angle=0.0):
        self.level = level
        world = level.world
        # Create a dynamic body
        size = self.size
        self.pos = b2Vec2(pos)
        self.sensorBody=world.CreateStaticBody(position=self.pos+b2Vec2(1.5,-2), angle=angle)
        fixture= self.sensorBody.CreatePolygonFixture(box=size/2.0,friction=0.3,isSensor=True)
        self.sensorBody.userData = self
        

        self.vertsA = [
            ( 0,0), (3,0), (3,1), (0,1),(0,0)
        ]
        self.vertsB = [
            (2,1), (2,5) , (1,5), (1,1), (2,1)
        ]
        fdef = b2FixtureDef(friction=1.0)
        polyA   = b2PolygonShape(vertices=self.vertsA)
        polyB   = b2PolygonShape(vertices=self.vertsB)
        self.body = world.CreateStaticBody(position=pos,shapes=[polyA,polyB],
                                          shapeFixture=fdef)
        #self.body.userData = self
    def add_to_render_queue(self, gr):
        size = self.size
        def render_it():
            Rectangle(pos=self.pos, size=(3,1),color=Color(1,1,1,1.0))
            Rectangle(pos=self.pos+b2Vec2(1,1), size=(1,4),color=Color(1,1,1,1.0))
        gr.add_render_item(render_it,1)


    def gooBeginsContact(self, goo):
        assert goo not in self.inGoalGoos 
        self.inGoalGoos.add(goo)

        def checkThatGooCallback(dt):
            
            if goo in self.inGoalGoos:
                self.level.level_finished()
            else:
                pass

        Clock.schedule_once(checkThatGooCallback, 2.0)
    

    def gooEndsContact(self,goo):
        assert goo in self.inGoalGoos 
        self.inGoalGoos.remove(goo)

