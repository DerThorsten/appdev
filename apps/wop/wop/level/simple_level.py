from base_level import BaseLevel
from Box2D import *
from kivy.core.image import Image as CoreImage
from wop import CanvasDraw
from kivy.graphics import Rectangle,Color
from wop import renderDistanceJoint,renderRectangle
from math import degrees

class SimpleLevel1(BaseLevel):
    def __init__(self, gameRender):
        super(SimpleLevel1, self).__init__(world= b2World((0.0,-10.0)),gameRender=gameRender)

        self.roi = (0,0), (40, 40)
        self.s = 40
        self.groundBody = None

        self.image   = CoreImage.load("res/overworld_bg.png")
        self.texture = self.image.texture

        self.blockImg = CoreImage.load("res/Brick_Block.png")
        self.blockTexture = self.blockImg.texture

        self.blockSize = b2Vec2(15,15)

        self.blocks = None


    def initPhysics(self):  
        super(SimpleLevel1, self).initPhysics()
        self.blocks = set()

        s = self.s
        self.groundBody = self.world.CreateBody(position=(0, 0))
        self.groundBody.CreateEdgeChain([(0,0),(0,s),(s,s),(s,0), (0,0) ])


        fixture=b2FixtureDef(shape=b2PolygonShape(box=self.blockSize/2),density=0.05, friction=0.2)
        b = self.world.CreateDynamicBody(position=(10,10),fixtures=fixture)
        self.blocks.add(b)
    def add_levels_render_items(self, gr):

        def renderBg():
            Rectangle(size=(self.s,self.s),
                      pos=(0,0),image="res/overworld_bg.png",
                      color=Color(0.3,0.3,1,1.0))
            

        def renderPhysics():
            canvasDraw =CanvasDraw( )
            canvasDraw.drawSegment((0,0),(0,self.s),(1,1,1))
            canvasDraw.drawSegment((0,self.s),(self.s,self.s),(1,1,1))
            canvasDraw.drawSegment((self.s,self.s),(self.s,0),(1,1,1))
            canvasDraw.drawSegment((self.s,0),(0,0),(1,1,1))

            for block in self.blocks:
                renderRectangle(size=self.blockSize, pos=block.position, 
                    angle=degrees(block.angle),texture=self.blockTexture,shiftHalfSize=True)


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
