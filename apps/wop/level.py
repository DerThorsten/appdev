import numpy
from Box2D import *
from kivy.clock import Clock
from debug_draw import CanvasDraw
from kivy.logger import Logger

import world_helper as wh

class Level(object):
    def __init__(self, gameRender):
        self.gameRender = gameRender


    ###############################
    # events
    ###############################

    def world_on_touch_down(self, wpos, touch):
        Logger.debug("Level: touch down %.1f %.1f"%wpos ) 
        # find clicked bodies
        body = wh.body_at_pos(self.world, pos=wpos)
        if body is not None:
            print "found body ",body

    def world_on_touch_move(self, wpos, touch):
        Logger.debug("Level: touch move %.1f %.1f"%wpos ) 
    def world_on_touch_up(self, wpos, touch):
        Logger.debug("Level: touch  up %.1f %.1f"%wpos ) 

    def initPhysics(self):
        self.killBoxVerts = boxVertices(*self.roi)
        self.killBoundingBoxBody = self.world.CreateBody(position=self.roi[0])
        self.killBoundingBoxBody.CreateEdgeChain(self.killBoxVerts)


    def start(self):
        Clock.schedule_interval(self.updateCaller,1.0/50)

    def updateCaller(self, dt):
        self.preUpdate(dt)
        self.update(dt)
        self.postUpdate(dt)

    def preUpdate(self, dt):
        pass
    def update(self, dt):
        self.world.Step(dt,5,5)
        self.render()
    def postUpdate(self, dt):
        pass

    def render(self):
        self.render_level()



def boxVertices(p0, p1, shiftOrigin=True):
    w = p1[0]-p0[0]
    h = p1[1]-p0[1]
    a = numpy.array([(0,0),(0,h),(w,h),(w,0),(0,0)])#+p0
    if not shiftOrigin :
        a+=p0
    return a

class SimpleLevel(Level):
    def __init__(self, gameRender):
        super(SimpleLevel, self).__init__(gameRender=gameRender)

        self.scale = 1.0
        self.offset = numpy.array([0,0])
        self.world = b2World((0.0,-10.0))

        self.roi = (-5,-5), (45, 45)

        self.s = 40

    def initPhysics(self):
        super(SimpleLevel, self).initPhysics()

        



        s = self.s
        ground = self.world.CreateBody(position=(0, 0))
        ground.CreateEdgeChain([(0,0),(0,s),(s,s),(s,0), (0,0) ])



    def preUpdate(self, dt):
        super(SimpleLevel, self).preUpdate(dt)

    def update(self, dt):
        super(SimpleLevel, self).update(dt)

    def postUpdate(self, dt):
        super(SimpleLevel, self).postUpdate(dt)

    def render_level(self):
        gr = self.gameRender
        canvasDraw =CanvasDraw(gr.canvas, gr.offset, gr.scale)
        canvasDraw.drawSegment((0,0),(0,self.s),(1,1,1))
        canvasDraw.drawSegment((0,self.s),(self.s,self.s),(1,1,1))
        canvasDraw.drawSegment((self.s,self.s),(self.s,0),(1,1,1))
        canvasDraw.drawSegment((self.s,0),(0,0),(1,1,1))

if __name__ == '__main__':
    pass
