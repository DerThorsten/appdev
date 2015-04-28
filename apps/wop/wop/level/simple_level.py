from base_level import BaseLevel
from Box2D import *
from kivy.core.image import Image as CoreImage
from wop import CanvasDraw
from kivy.graphics import Rectangle,Color
from wop import renderDistanceJoint,renderRectangle
from math import degrees
from wop.game_items import *
import numpy
from kivy.graphics import Line,Mesh






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

        self.staticItem = []


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
        platW = 50
        platH = 50
        gap = 50

        

        #### add a few blocks
        blockA = StaticBlock(size=(platW, platH))
        blockA.add_to_level(level=self, pos=(0, 0))
        blockB = StaticBlock(size=(platW, platH))
        blockB.add_to_level(level=self, pos=(platW+gap, 0))
        self.staticItem.append(blockA)
        self.staticItem.append(blockB)

        # add a single starting goo
        blackGoo = BlackGoo()
        self.addGoo(blackGoo, (platW/2.0, platH+2.0))

        ##### add goal
        goal = GoalItem()
        goal.add_to_level(self, pos=(platW*1.5+gap-2.5, platH+50))
        self.staticItem.append(goal)

        # add destroyer
        destroyer = ZigZackDestroyer(size=(gap,2),orientation='horizontal')
        destroyer.add_to_level(level=self,pos=(platW,0))
        self.staticItem.append(destroyer)

        # top destroyer
        destroyer = ZigZackDestroyer(size=(self.roi[1][0],2),orientation='horizontal')
        destroyer.add_to_level(level=self,pos=(0,self.roi[1][1]-2))
        self.staticItem.append(destroyer)

        # left destroyer
        destroyer = ZigZackDestroyer(size=(2,self.roi[1][1]),orientation='vertical')
        destroyer.add_to_level(level=self,pos=(0,0))
        self.staticItem.append(destroyer)

        # right destroyer
        destroyer = ZigZackDestroyer(size=(2,self.roi[1][1]),orientation='vertical')
        destroyer.add_to_level(level=self,pos=(self.roi[1][0]-2,0))
        self.staticItem.append(destroyer)


    def add_levels_render_items(self, gr):

        def renderBg():
            w = self.roi[1][0]
            h = self.roi[1][1]
            Rectangle(size=(w,h),
                      pos=(0.0,0.0),texture=self.texture,
                      color=Color(1,1,1,1))
    
        for item in self.staticItem:
            item.add_to_render_queue(gr)


        gr.add_render_item(renderBg, z=0)



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
