from base_level import BaseLevel
from Box2D import *
from kivy.core.image import Image as CoreImage
from wop import CanvasDraw
from kivy.graphics import Rectangle,Color
from wop import renderDistanceJoint,renderRectangle
from math import degrees
from wop.game_items import GameItem,GooDestroyerItem
import numpy

class SimpleLevel1(BaseLevel):
    def __init__(self, gameRender):
        super(SimpleLevel1, self).__init__(world= b2World((0.0,-10.0)),gameRender=gameRender)

        self.roi = (0,0), (1024.0/4.0, 432.0/4.0)
        self.s = self.roi
        self.groundBody = None

        self.image   = CoreImage.load("res/bg0.jpg")
        self.texture = self.image.texture

        self.blockImg = CoreImage.load("res/Brick_Block.png")
        self.blockTexture = self.blockImg.texture

        self.blockSize = b2Vec2(15,15)

        self.blocks = None


    def initPhysics(self):  
        super(SimpleLevel1, self).initPhysics()


        s = self.s
        self.groundBody = self.world.CreateBody(position=(0, 0))
        w = s[1][0]
        h = s[1][1]
        self.groundBody.CreateEdgeChain(
            [
                (0.0,0.0),
                (0.0,h),
                (w,h),
                (w,0.0), 
                (0.0,0.0) 
            ]
        )
        self.platW = 50
        self.platH = 50
        self.gap = 50
        platW = self.platW
        platH = self.platH
        gap =self.gap
        self.groundBody.CreateEdgeChain([
            (0,0),
            (0,platH),
            (platW,platH),
            (platW,0), 
            (0+platW+gap,0),
            (0+platW+gap,platH),
            (platW+platW+gap,platH),
            (platW+platW+gap,0), 
            (platW+platW+gap,0) 
        ])


        

        xx = numpy.linspace(0, self.gap, 200)
       

        self.killerVerts  = [
            (0,0),
            (self.gap,0),
            (self.gap,2),
            (0,2),
            (0,0)
        ]

        fixtures=b2FixtureDef(
            shape=b2PolygonShape(vertices=self.killerVerts)
        )
        self.killerBody = self.world.CreateBody(
            position=(self.platW, 0),
            fixtures=fixtures
        )

        self.killerItem  = GooDestroyerItem()
        self.killerBody.body = self.killerBody
        self.killerBody.userData = self.killerItem



    def add_levels_render_items(self, gr):

        def renderBg():
            w = self.roi[1][0]
            h = self.roi[1][1]
            Rectangle(size=(w,h),
                      pos=(0.0,0.0),texture=self.texture,
                      color=Color(1,1,1,1))
            

        def renderPhysics():
            canvasDraw =CanvasDraw( )
            #canvasDraw.drawSegment((0,0),(0,self.s),(1,1,1))
            #canvasDraw.drawSegment((0,self.s),(self.s,self.s),(1,1,1))
            #canvasDraw.drawSegment((self.s,self.s),(self.s,0),(1,1,1))
            #canvasDraw.drawSegment((self.s,0),(0,0),(1,1,1))

            
            Rectangle(pos=(0,0), size=(self.platW,self.platH),color=Color(1,1,1,1.0),
              texture=self.blockTexture)
            Rectangle(pos=(self.platW+self.gap,0), size=(self.platW,self.platH),color=Color(1,1,1,1.0),
              texture=self.blockTexture)


        gr.add_render_item(renderBg, z=0)
        gr.add_render_item(renderPhysics, z=1)


class SimpleLevel2(BaseLevel):
    def __init__(self, gameRender):
        super(SimpleLevel2, self).__init__(world= b2World((0.0,-10.0)),gameRender=gameRender)


        self.roi = (0,0), (20, 20)
        self.s = 10
        self.groundBody = None

        self.image   = CoreImage.load("res/bg.jpg")
        self.texture = self.image.texture

    def initPhysics(self):  
        super(SimpleLevel2, self).initPhysics()
        s = self.s
        self.groundBody = self.world.CreateBody(position=(0, 0))
        self.groundBody.CreateEdgeChain([(0,0),(0,s),(s,s),(s,0), (0,0) ])



    def add_levels_render_items(self, gr):

        def renderBg():
            canvasDraw =CanvasDraw( )
            Rectangle(texture=self.texture,size=(self.s,self.s),
                      pos=(0,0),image="res/bg.jpg",
                      color=Color(1,1,1,1.0))
        def renderPhysics():
            canvasDraw =CanvasDraw( )
            canvasDraw.drawSegment((0,0),(0,self.s),(1,1,1))
            canvasDraw.drawSegment((0,self.s),(self.s,self.s),(1,1,1))
            canvasDraw.drawSegment((self.s,self.s),(self.s,0),(1,1,1))
            canvasDraw.drawSegment((self.s,0),(0,0),(1,1,1))

        gr.add_render_item(renderBg, z=0)
        gr.add_render_item(renderPhysics, z=1)
