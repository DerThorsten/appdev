import numpy
import networkx as nx
from Box2D import *
from kivy.clock import Clock
from kivy.logger import Logger
import operator
from wop import DebugDraw,CanvasDraw
import math
from wop.game_items import *
import wop
from kivy.config import Config
from kivy.app import App

class FindAllGoos(Box2D.b2QueryCallback):
    def __init__(self, pos, minDist, maxDist): 
        super(FindAllGoos, self).__init__()
        self.pos = pos
        self.minDist = minDist
        self.maxDist = maxDist
        self.dists  = dict()
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            ud = body.userData 
            if(isinstance(ud,Goo)):
                if body not in self.dists:
                    d = self.pos - body.position
                    d = d.length
                    if d>=self.minDist and d<=self.maxDist:
                        self.dists[body] = d
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
        gParam = goo.param()
        nGoos = self.number_of_nodes()
        print "GOO TO ADD",goo, "ngoos",self.number_of_nodes()
        print "min b edge",gParam.minBuildEdges

        #Logger.debug("GOO GRAPH: #goos %d " %nGoos)
        gooDist = gParam.maxGooDist*1.2
        if nGoos==0:
            return (1,None)
        #if nGoos == 1:
        #    return (1,None)
        else :
            pos = b2Vec2(*pos)
            # find all goos in range
            query = FindAllGoos(pos, minDist=gParam.minGooDist,
                                maxDist=gParam.maxGooDist)
            aabb = b2AABB(lowerBound=pos-(gooDist, gooDist), upperBound=pos+(gooDist, gooDist))
            self.world.QueryAABB(query, aabb)

        dists, sortedBodies = query.sortedBodies()
        nOther = len(dists)
        print "nOthers",nOther
        if nOther ==0 :
            return (0, None)
        if nOther<gParam.minBuildEdges and not(nGoos < gParam.minBuildEdges):
            return (0,None)
        elif nOther == 1:
            if nGoos==1 or gParam.minBuildEdges==1:
                b0 = sortedBodies[0]
                return (1,(b0,))
            else :
                return (0,None)
        else :
            b0 = sortedBodies[0]
            b1 = sortedBodies[1]
            g0 = b0.userData
            g1 = b1.userData

            if gParam.canBeAddedAsJoint:
                if not self.has_edge(g0,g1):
                    lineDist = distToLine((b0.position,b1.position), pos)
                    if lineDist < gParam.addAsJointDist:
                        return (2, (b0, b1))

            return (1,sortedBodies[:min(nOther,gParam.maxBuildEdges)])  




class LevelDestructionListener(b2DestructionListener):
    """
    The destruction listener callback:
    "SayGoodbye" is called when a joint or shape is deleted.
    """
    def __init__(self,level, **kwargs):
        super(LevelDestructionListener, self).__init__(**kwargs)

    def SayGoodbye(self, pobject):
        if isinstance(pobject, b2Joint):
            if self.level.mouseJoint==pobject:
                self.level.mouseJoint=None
            else:
                self.level.joint_destroyed(pobject)
        elif isinstance(pobject, b2Fixture):
            self.level.FixtureDestroyed(pobject)



class Level(object):
    def __init__(self,world, gameRender):

        self.world = world
        self.destructionListener = LevelDestructionListener(level=self)
        self.world.destructionListener=self.destructionListener


        self.gameRender = gameRender
        self.debugDraw = DebugDraw(world=None)

        self.wmManager = None
        self.gooGraph = GooGraph(self)

        self.mouseJoint = None

    ###############################
    # events
    ###############################

    def joint_destroyed(self, joint):
        pass

    def fixture_destroyed(self, fixture):
        pass

    def set_scale(self, scale):
        self.gameRender.set_scale(scale)
    def get_scale(self):
        return self.gameRender.get_scale()

    def set_offset(self, offset):
        self.gameRender.set_offset(offset)
    def get_offset(self):
        return self.gameRender.get_offset()

    def world_on_touch_down(self, wpos, touch):
        body = wop.body_at_pos(self.world, pos=wpos)

        if body is not None:

            self.mouseJoint = self.world.CreateMouseJoint(
                bodyA=self.groundBody,
                bodyB=body,
                target=wpos,
                maxForce=1000.0*body.mass
            )
            body.awake = True

        else :
            self.wmManager.world_on_touch_down(wpos, touch)

    def world_on_touch_move(self, wpos, wppos, touch):
        #Logger.debug("Level: touch move %.1f %.1f"%wpos ) 
        
        if self.mouseJoint is not None:
            self.mouseJoint.target  =  wpos
        else :
            self.wmManager.world_on_touch_move(wpos, wppos, touch)

    def world_on_touch_up(self, wpos, touch):
        ##Logger.debug("Level: touch  up %.1f %.1f"%wpos ) 
        self.wmManager.world_on_touch_up(wpos, touch)
        if self.mouseJoint is not None:
            self.world.DestroyJoint(self.mouseJoint)
            self.mouseJoint = None
        else :
            self.wmManager.world_on_touch_up(wpos, touch)
    def set_wm_manager(self, wmManager):
        self.wmManager = wmManager

    def initPhysics(self):
        self.killBoxVerts = boxVertices(*self.roi)
        self.killBoundingBoxBody = self.world.CreateBody(position=self.roi[0])
        self.killBoundingBoxBody.CreateEdgeChain(self.killBoxVerts)

    def start_level(self):
        Clock.schedule_interval(self.updateCaller,1.0/50)

    def stop_level(self):
        Clock.unschedule(self.updateCaller)

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
        # take param from first goo (so far)
        gParam  = gooA.param()
        dfn=b2DistanceJointDef(
           frequencyHz=gParam.frequencyHz,
           dampingRatio=gParam.dampingRatio,
           bodyA=gooA.body,bodyB=gooB.body,
           localAnchorA=gooA.localAnchor(),
           localAnchorB=gooB.localAnchor()
        )
        j=self.world.CreateJoint(dfn)
        if gParam.autoExpanding:
            j.length = gParam.expandingDist
        self.gooGraph.add_edge(gooA, gooB, joint=j)
        
    def render(self):
        gr = self.gameRender


        self.debugDraw.world = self.world
        
        # add debug draw to render queue
        app = App.get_running_app()
        config = app.config

        dd = config.getboolean(u'section1',u'debugDraw')
        if(dd):
            z = config.getint(u'section1',u'debugDrawZ')
            gr.add_render_item(self.debugDraw.debugDraw,z=z)
        
        # add level render to render queue
        self.add_levels_render_items(gr)

        # render goos
        gr = self.gameRender
        
        def renderGoosJoints():
            for e in self.gooGraph.edges(data=True):
                (gooA,gooB,d) = e
                j=d['joint']
                gooA.renderJoint(gr,j,gooB)      
                gooB.renderJoint(gr,j,gooA)  
        def renderAllGoos():
            for goo in self.gooGraph.nodes():
                goo.render(self)
        gr.add_render_item(renderAllGoos,z=4)
        gr.add_render_item(renderGoosJoints,z=3)

        # builder/adder tentative render
        # if and only if there is NO mouse joint
        if self.mouseJoint is None:
            gr.add_render_item(self.wmManager.render, z=4)

        # do the actual rendering
        gr.render()


def boxVertices(p0, p1, shiftOrigin=True):
    w = p1[0]-p0[0]
    h = p1[1]-p0[1]
    if shiftOrigin:
        return [(0,0),(0,h),(w,h),(w,0),(0,0)]
    else:
        px,py = p0
        return [(0+px,0+py),(0+px,h+py),(w+px,h+py),(w+px,0+py),(0+px,0+py)]

class SimpleLevel1(Level):
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



    def preUpdate(self, dt):
        super(SimpleLevel1, self).preUpdate(dt)

    def update(self, dt):
        super(SimpleLevel1, self).update(dt)

    def postUpdate(self, dt):
        super(SimpleLevel1, self).postUpdate(dt)

    def add_levels_render_items(self, gr):

        def renderBg():
            canvasDraw =CanvasDraw( )
            Rectangle(texture=self.texture,size=(40,40),
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


class SimpleLevel2(Level):
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

if __name__ == '__main__':
    pass
