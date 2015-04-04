import numpy
import networkx as nx
from Box2D import *
from kivy.clock import Clock
from debug_draw import CanvasDraw
from kivy.logger import Logger
import operator
import world_helper as wh
import debug_draw
import math
from wop.game_items import *

class FindAllGoos(Box2D.b2QueryCallback):
    def __init__(self, pos, maxDist): 
        super(FindAllGoos, self).__init__()
        self.pos = pos
        self.maxDist = maxDist
        self.dists  = dict()
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            ud = body.userData 
            if(isinstance(ud,Goo)):
                if body not in self.dists:
                    d = self.pos - body.position
                    Logger.debug("D %f"%d.length)
                    if d.length<=self.maxDist:
                        Logger.debug("DDDDD %f"%d.length)
                        self.dists[body] = d.length
        return True

    def sortedBodies(self):
        #sortedBodies = sorted(self.dists.items(), key=operator.itemgetter(1))
        d = self.dists

        #sortedBodies = sorted(d, key=lambda k: d[k][1])
        sortedBodies=[k for (k,v) in sorted(d.items(), key=lambda (k, v): v)]
        return self.dists, sortedBodies


def distToLine(line, p):
    def dist(x1,y1, x2,y2, x3,y3): # x3,y3 is the point
        px = x2-x1
        py = y2-y1

        something = px*px + py*py

        u =  ((x3 - x1) * px + (y3 - y1) * py) / float(something)

        if u > 1:
            u = 1
        elif u < 0:
            u = 0

        x = x1 + u * px
        y = y1 + u * py

        dx = x - x3
        dy = y - y3

        # Note: If the actual distance does not matter,
        # if you only want to compare what this function
        # returns to other results of this function, you
        # can just return the squared distance instead
        # (i.e. remove the sqrt) to gain a little performance

        dist = math.sqrt(dx*dx + dy*dy)

        return dist

    return dist(line[0][0],line[0][1],
                line[1][0],line[1][1],
                p[0],p[1])

class GooGraph(nx.Graph):
    def __init__(self, level):
        super(GooGraph, self).__init__()
        self.level = level
        self.world = level.world
    def canGooBeAdded(self, goo, pos):
        nGoos = self.number_of_nodes()
        #Logger.debug("GOO GRAPH: #goos %d " %nGoos)
        gooDist = goo.gooDistance()*1.2
        if nGoos==0:
            return (1,None)
        #if nGoos == 1:
        #    return (1,None)
        else :
            pos = b2Vec2(*pos)
            # find all goos in range
            query = FindAllGoos(pos, gooDist)
            aabb = b2AABB(lowerBound=pos-(gooDist, gooDist), upperBound=pos+(gooDist, gooDist))
            self.world.QueryAABB(query, aabb)

        dists, sortedBodies = query.sortedBodies()
        Logger.debug("found %d"%len(dists))
        nOther = len(dists)
        if nOther==0:
            return (0,None)
        elif nOther == 1:
            if nGoos==1:
                b0 = sortedBodies[0]
                return (1,(b0,))
            else :
                return (0,None)
        else :
            b0 = sortedBodies[0]
            b1 = sortedBodies[1]
            g0 = b0.userData
            g1 = b1.userData

            if self.has_edge(g0,g1):
                print "has edge"
            else:
                print "has no edge"
                lineDist = distToLine((b0.position,b1.position), pos)
                print "line dist", lineDist

                if lineDist < goo.gooRadius()/2.0:
                    print "add as edge"
                    return (2, (b0, b1))

            return (1,sortedBodies[:min(nOther,5)])  




class Level(object):
    def __init__(self,world, gameRender):
        self.world = world
        self.gameRender = gameRender
        self.debugDraw = debug_draw.DebugDraw(world=None,
                            scale=self.gameRender.scale, 
                            offset=self.gameRender.offset)

        self.wmManager = None
        
        self.gooGraph = GooGraph(self)
    ###############################
    # events
    ###############################

    def setScale(self, scale):
        self.gameRender.scale = scale
    def getScale(self):
        return self.gameRender.scale

    def setOffset(self, offset):
        self.gameRender.offset = offset
    def getOffset(self):
        return self.gameRender.offset   

    def world_on_touch_down(self, wpos, touch):
        #Logger.debug("Level: touch down %.1f %.1f"%wpos ) 
        self.wmManager.world_on_touch_down(wpos, touch)
        # find clicked bodies
        body = wh.body_at_pos(self.world, pos=wpos)
        if body is not None:
            print "found body ",body
    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("Level: touch move %.1f %.1f"%wpos ) 
        self.wmManager.world_on_touch_move(wpos, wppos, touch)

    def world_on_touch_up(self, wpos, touch):
        ##Logger.debug("Level: touch  up %.1f %.1f"%wpos ) 
        self.wmManager.world_on_touch_up(wpos, touch)

    def set_wm_manager(self, wmManager):
        self.wmManager = wmManager

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

    def addGoo(self, goo, pos):
        goo.playBuildSound()
        goo.addToWorld(self.world, pos)
        self.gooGraph.add_node(goo)

    def connectGoos(self, gooA, gooB):
        dfn=b2DistanceJointDef(
           frequencyHz=2.0,
           dampingRatio=0.1,
           bodyA=gooA.body,bodyB=gooB.body,
           anchorA=gooA.body.position,
           anchorB=gooB.body.position
        )
        j=self.world.CreateJoint(dfn)
        j.length = gooA.gooDistance()
        print j
        self.gooGraph.add_edge(gooA, gooB, joint=j)
        
    def render(self):
        gr = self.gameRender


        self.debugDraw.scale = gr.scale
        self.debugDraw.offset = gr.offset
        self.debugDraw.world = self.world
        
        # add debug draw to render queue
        gr.add_render_item(self.debugDraw.debugDraw,z=0)
        
        # add level render to render queue
        gr.add_render_item(self.render_level,z=1)

        # render goos
        def renderAllGoos():
            for goo in self.gooGraph.nodes():
                goo.render(self)
        gr.add_render_item(renderAllGoos,z=2)

        # builder/adder tentative render
        gr.add_render_item(self.wmManager.render, z=3)
        # do the actual rendering
        gr.render()


def boxVertices(p0, p1, shiftOrigin=True):
    w = p1[0]-p0[0]
    h = p1[1]-p0[1]
    a = numpy.array([(0,0),(0,h),(w,h),(w,0),(0,0)])#+p0
    if not shiftOrigin :
        a+=p0
    return a

class SimpleLevel(Level):
    def __init__(self, gameRender):
        super(SimpleLevel, self).__init__(world= b2World((0.0,-10.0)),gameRender=gameRender)


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
        canvasDraw =CanvasDraw( gr.offset, gr.scale)
        canvasDraw.drawSegment((0,0),(0,self.s),(1,1,1))
        canvasDraw.drawSegment((0,self.s),(self.s,self.s),(1,1,1))
        canvasDraw.drawSegment((self.s,self.s),(self.s,0),(1,1,1))
        canvasDraw.drawSegment((self.s,0),(0,0),(1,1,1))

if __name__ == '__main__':
    pass
