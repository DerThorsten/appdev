import numpy
import networkx as nx
from Box2D import *
from kivy.clock import Clock
from kivy.logger import Logger
import operator
import math
from wop.game_items import *
import wop
from kivy.config import Config
from kivy.app import App

class FindAllGoos(Box2D.b2QueryCallback):
    def __init__(self, pos, minDist, maxDist,verbose=False): 
        super(FindAllGoos, self).__init__()
        self.pos = pos
        self.minDist = minDist
        self.maxDist = maxDist
        self.dists  = dict()
        self.verbose = verbose
    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            ud = body.userData 
            if self.verbose : print "found goo"
            if(isinstance(ud,Goo)):
                if body not in self.dists:
                    #print "body pos",body.position, "local anchor ",ud.localAnchor()
                    #print "wpos ",body.GetWorldPoint(b2Vec2(*ud.localAnchor())),"\n"
                    d = self.pos - body.GetWorldPoint(b2Vec2(*ud.localAnchor())) #position
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
        
        if isinstance(pos,tuple):
            pos = b2Vec2(*pos)
        # try to add the goo as edge first
        if nGoos >= 2 :
            rad = gParam.addAsJointRadius
            
            # find all goos in range
            query = FindAllGoos(pos,
                                minDist=0,
                                maxDist=rad,verbose=False)
            lb = lowerBound=pos-(rad, rad)
            ub = lowerBound=pos+(rad, rad)
            aabb = b2AABB(lowerBound=lb, upperBound=ub)
            self.world.QueryAABB(query, aabb)
            dists, sortedBodies = query.sortedBodies()
            nOther = len(dists)
            
            # can this goo be directly added as joint
            # (and are enough goos there)
            if gParam.canBeAddedAsJoint and nOther>=2:

                # remember the best matching two
                # goos which connecting line
                # has the minimal distance 
                # to the users clicked position
                bestDist = float('inf')
                bestPair = None

                # loop over all pairs
                useN = min(nOther, 3)
                for i0 in range(useN-1):
                    b0 = sortedBodies[i0]
                    goo0 = b0.userData
                    for i1 in range(i0+1,useN):
                        b1 = sortedBodies[i1]
                        goo1 = b1.userData

                        # only goos which are not yet connected can be connected
                        if not self.has_edge(goo0,goo1):
                            p0 = b0.GetWorldPoint(b2Vec2(*goo0.localAnchor()))
                            p1 = b1.GetWorldPoint(b2Vec2(*goo1.localAnchor()))

          
                            lineDist = distToLine((p0,p1), pos)
                            if lineDist < bestDist:
                                bestDist = lineDist
                                bestPair = (b0, b1)
                if bestDist <  gParam.addAsJointDist:
                    return (2, bestPair)

        #  from here on it is ensured
        # that the goo cannot be added as joint
        # if there are no goos
        # at all we do not need
        if nGoos==0:
            return (1,None)
        else :
            # find all goos in range
            mxDst = gParam.maxGooDist
            query = FindAllGoos(pos, minDist=gParam.minGooDist,
                                maxDist=gParam.maxGooDist)
            aabb = b2AABB(lowerBound=pos-(mxDst, mxDst), upperBound=pos+(mxDst, mxDst))
            self.world.QueryAABB(query, aabb)

            dists, sortedBodies = query.sortedBodies()
            nOther = len(dists)
            #print "nOthers",nOther
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



class BaseLevel(object):
    def __init__(self,world, gameRender):

        self.world = world
        self.destructionListener = LevelDestructionListener(level=self)
        self.world.destructionListener=self.destructionListener


        self.gameRender = gameRender
        self.debugDraw = DebugDraw(world=None)

        self.wmManager = None
        self.gooGraph = GooGraph(self)
        self.mouseJoint = None




        self.is_scheduled = False
        self.was_scheduled_bevore_global_pause = False
    ###############################
    # events
    ###############################
    def on_global_pause(self):
        self.was_scheduled_bevore_global_pause = self.is_scheduled
        if self.is_scheduled :
            Clock.unschedule(self.updateCaller,1.0/50)
        self.is_scheduled = False

    def on_global_resume(self):
        if self.was_scheduled_bevore_global_pause:
            self.is_scheduled = True
            Clock.schedule_interval(self.updateCaller,1.0/50)
        else:
            self.is_scheduled = False

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
        self.render()
        self.update(dt)
        self.postUpdate(dt)

    def preUpdate(self, dt):
        md = 0
        for i,e in enumerate(self.gooGraph.edges(data=True)):
            (gooA,gooB,d) = e
            j=d['joint']
            jReacForceV = j.GetReactionForce(30)
            #print i,jReacForceV
            #print j.length
            d =  (j.anchorA-j.anchorB).length
            if d > md :
                md = d
            #if(d>9):
            #    gooA = j.bodyA.userData
            #    gooB = j.bodyB.userData
            #    self.gooGraph.remove_edge(gooA,gooB)
            #    self.world.DestroyJoint(j)
            #    break
        #print "maxdist ",md
    def update(self, dt):
        self.world.Step(dt,5,5)
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
                #gooB.renderJoint(gr,j,gooA)  
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


if __name__ == '__main__':
    pass
