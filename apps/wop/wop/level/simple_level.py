from base_level import BaseLevel
from Box2D import *
from kivy.core.image import Image as CoreImage
from wop import CanvasDraw
from kivy.graphics import Rectangle,Color

class SimpleLevel1(BaseLevel):
    def __init__(self, gameRender):
        super(SimpleLevel1, self).__init__(world= b2World((0.0,-10.0)),gameRender=gameRender)

        self.roi = (0,0), (40, 40)
        self.s = 40
        self.groundBody = None

        self.image   = CoreImage.load("res/bg.jpg")
        self.texture = self.image.texture

    def initPhysics(self):  
        super(SimpleLevel1, self).initPhysics()

        s = self.s
        self.groundBody = self.world.CreateBody(position=(0, 0))
        self.groundBody.CreateEdgeChain([(0,0),(0,s),(s,s),(s,0), (0,0) ])


    def add_levels_render_items(self, gr):

        def renderBg():
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
