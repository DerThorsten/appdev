from base_level import BaseLevel
from pybox2d import *
from kivy.core.image import Image as CoreImage
from wop import CanvasDraw
from kivy.graphics import *
from wop import renderDistanceJoint,renderRectangle
from math import degrees
from wop.game_items import *
from wop import getImage,registerImage
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


        self.gooRes[BlackGoo] = 500
        self.gooRes[GreenGoo] = 500
        self.gooRes[AnchorGoo] = 500
        self.gooRes[BalloonGoo] = 500

    def initPhysics(self):  
        super(SimpleLevel1, self).initPhysics()




        s = self.s
        self.groundBody = self.world.createBody(position=(0, 0))
        w = s[1][0]
        h = s[1][1]
        self.groundBody.createEdgeChainFixture(
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



class SimpleLevel2(SimpleLevel1):
    def __init__(self, gameRender):
        super(SimpleLevel2, self).__init__(gameRender=gameRender)




    def initPhysics(self):  
        super(SimpleLevel2, self).initPhysics()




        #### add a few blocks
        rotKiller = RotatingKiller(size=(15, 2))
        rotKiller.add_to_level(level=self, pos=(75, 50))
        self.staticItem.append(rotKiller)


    def add_levels_render_items(self, gr):
        super(SimpleLevel2, self).add_levels_render_items(gr)
        pass
        #def renderBg():
        #    canvasDraw =CanvasDraw( )
        #    Rectangle(texture=self.texture,size=(self.s,self.s),
        #              pos=(0,0),image="res/bg.jpg",
        #              color=Color(1,1,1,1.0))
        #def renderPhysics():
        #    canvasDraw =CanvasDraw( )
        #    canvasDraw.drawSegment((0,0),(0,self.s),(1,1,1))
        #    canvasDraw.drawSegment((0,self.s),(self.s,self.s),(1,1,1))
        #    canvasDraw.drawSegment((self.s,self.s),(self.s,0),(1,1,1))
        #    canvasDraw.drawSegment((self.s,0),(0,0),(1,1,1))

        #gr.add_render_item(renderBg, z=0)
        #gr.add_render_item(renderPhysics, z=1)



registerImage("raymanPlanet","res/rayman_planet.png")
registerImage("planet","res/planet.png")

class Planet(GameItem):
    planetImage = CoreImage.load("res/planet.png")
    planetTexture = planetImage.texture

 

    def __init__(self, radius, mass = 200000.0, texutreName='raymanPlanet'):
        super(Planet, self).__init__()
        self.body = None
        self.radius = radius
        self.mass = mass
        self.texutreName=texutreName
    def add_to_level(self,level, pos, angle=0.0):
        world = level.world
        # Create a dynamic body
        size = self.radius*2
        self.pos = b2.vec2(pos)#+size/2.0
        self.body=world.createStaticBody(position=self.pos, angle=angle)
        # And add a box fixture onto it (with a nonzero density, so it will move)
        shape  = b2.circleShape(radius=self.radius)
        fd = b2.fixtureDef(shape=shape)
        self.body.createFixture(fd)
        self.body.userData = self
        self.renderPos = self.pos-size/2.0
    def add_to_render_queue(self, gr):
        def render_it():
            #print "RENDER POS",self.renderPos,len(self.renderPos)
            #e = Ellipse(pos=center,size=size,color=Color(*color))
            Ellipse(
               pos=(self.renderPos[0],self.
                    renderPos[1]), 
               size=(self.radius*2,self.radius*2),
               color=Color(1,1,1,1),
               texture=getImage(self.texutreName).texture

            )
        gr.add_render_item(render_it,1)





class SpaceLevel(BaseLevel):
    levelSound = SoundLoader.load('res/sounds/soundtrack/tumbler.wav')

    def __init__(self, gameRender):
        super(SpaceLevel, self).__init__(world= b2World((0.0,-10.0)),gameRender=gameRender)

        self.roi = (0,0), (1024.0/4.0, 432.0/4.0)
        self.s = self.roi
        self.groundBody = None

        self.image   = CoreImage.load("res/space_bg.jpg")
        self.texture = self.image.texture

        self.blockImg = CoreImage.load("res/Brick_Block.png")
        self.blockTexture = self.blockImg.texture

        self.blockSize = b2Vec2(15,15)

        self.staticItem = []


        self.gooRes[BlackGoo] = 500
        self.gooRes[GreenGoo] = 500
        self.gooRes[AnchorGoo] = 500
        self.gooRes[BalloonGoo] = 500

        self.planets = []

    def initPhysics(self):  
        super(SpaceLevel, self).initPhysics()


        self.world.gravity  = b2.vec2(0,0)

        s = self.s
        self.groundBody = self.world.createBody(position=(0, 0))
        w = s[1][0]
        h = s[1][1]
        self.groundBody.createEdgeChainFixture(
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

        
        planetRadius = 10
        planetPos = 30,30

        #### add a few blocks
        planetA = Planet(planetRadius,texutreName='raymanPlanet')
        planetA.add_to_level(level=self, pos=planetPos)
        self.staticItem.append(planetA)
        self.planets.append(planetA)


        planetRadius = 5
        planetPos = 40,55

        #### add a few blocks
        planetA = Planet(planetRadius,mass=-500000,texutreName='raymanPlanet')
        planetA.add_to_level(level=self, pos=planetPos)
        self.staticItem.append(planetA)
        self.planets.append(planetA)



        planetRadius = 10
        planetPos = 45,80

        #### add a few blocks
        planetA = Planet(planetRadius,texutreName='raymanPlanet')
        planetA.add_to_level(level=self, pos=planetPos)
        self.staticItem.append(planetA)
        self.planets.append(planetA)




        planetRadius = 10
        planetPos = 80,50

        planetA = Planet(planetRadius,texutreName='planet')
        planetA.add_to_level(level=self, pos=planetPos)
        self.staticItem.append(planetA)
        self.planets.append(planetA)

        planetPos = 30,30
        # add a single starting goo
        blackGoo = BlackGoo()
        self.addGoo(blackGoo, (planetPos[0],planetPos[1]+planetRadius))

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


    def preUpdate(self, dt):

        for planet in self.planets:
            planetPos = b2.vec2(planet.pos)
            planetMass = planet.mass
            for gooItem in self.gooGraph.nodes_iter():
                gooBody = gooItem.body 
                gooPosition = gooBody.position
                gooMass = gooBody.mass
                dvec = planetPos - gooPosition
                dSquared =dvec.lengthSquared
                #print "dSquared",dSquared,gooMass,planetMass
                force  =  planetMass*gooMass/dSquared
                fvec = dvec*force*gooBody.gravityScale
                fvec = fvec / dvec.lengthSquared

                gooBody.applyForceToCenter(fvec, True)

        super(SpaceLevel,self).preUpdate(dt)
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



    def start_level(self):
        super(SpaceLevel, self).start_level()
        SpaceLevel.levelSound.load()
        SpaceLevel.levelSound.play()

    def stop_level(self):
        super(SpaceLevel, self).stop_level()
        SpaceLevel.levelSound.stop()
        SpaceLevel.levelSound.unload()
