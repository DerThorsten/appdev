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
from wop.game_items import GameItem,GooDestroyerItem
from wop.game_items import RegisteredGoos

class FindAllGoos(Box2D.b2QueryCallback):
    def __init__(self, pos, minDist, maxDist,gooGraph,verbose=False): 
        super(FindAllGoos, self).__init__()
        self.pos = pos
        self.minDist = minDist
        self.maxDist = maxDist
        self.dists  = dict()
        self.gooGraph = gooGraph
        self.verbose = verbose


        


    def ReportFixture(self, fixture):
        body = fixture.body
        if body.type == b2_dynamicBody:
            ud = body.userData 
            if self.verbose : print "found goo"
            if(isinstance(ud,Goo)):
                currentDegree = self.gooGraph.degree(ud)
                if currentDegree+1 < ud.param().maxEdges :
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
                                maxDist=rad,gooGraph=self,
                                verbose=False)
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
                                maxDist=gParam.maxGooDist,gooGraph=self)
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
