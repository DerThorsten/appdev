import numpy
import networkx as nx
import pybox2d as b2
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
from goo_graph import GooGraph



class LevelDestructionListener(b2.DestructionListener):
    """
    The destruction listener callback:
    "SayGoodbye" is called when a joint or shape is deleted.
    """
    def __init__(self,level, **kwargs):
        super(LevelDestructionListener, self).__init__(**kwargs)
        self.level = level

    def sayGoodbyeJoint(self, joint):
        if self.level.mouseJoint==joint:
            self.level.mouseJoint=None
        else:
            self.level.joint_destroyed(joint)




class LevelContactListener(b2.ContactListener):
    def __init__(self, level):
        super(LevelContactListener, self).__init__()
        self.level = level
    def beginContact(self, contact):
        """
        This is a critical function when there are many contacts in the world.
        It should be optimized as much as possible.
        """
        #print "CONTACT",contact
        bodyA=contact.fixtureA.body
        bodyB=contact.fixtureB.body
        
        udA = bodyA.userData
        udB = bodyB.userData


        if(udA is not None and udB is not None):
            
            # both goos
            if(isinstance(udA, Goo) and isinstance(udB, Goo) ):
                pass
            # noo goos
            if( not isinstance(udA, Goo) and not isinstance(udB, Goo) ):
                pass   
            elif isinstance(udA, GoalItem):
                #print "goal item begin contact"
                udA.gooBeginsContact(udB)
            elif isinstance(udB, GoalItem):
                #print "goal item begin contact"
                udN.gooBeginsContact(udA)

        
    def endContact(self, contact):

        bodyA=contact.fixtureA.body
        bodyB=contact.fixtureB.body
        
        udA = bodyA.userData
        udB = bodyB.userData


        if(udA is not None and udB is not None):
            
            # both goos
            if(isinstance(udA, Goo) and isinstance(udB, Goo) ):
                pass
            # noo goos
            if( not isinstance(udA, Goo) and not isinstance(udB, Goo) ):
                pass   
            elif isinstance(udA, GoalItem):
                #print "goal item end contact"
                udA.gooEndsContact(udB)
            elif isinstance(udB, GoalItem):
                #print "goal item end contact"
                udN.gooEndsContact(udA)
    def preSolve(self, contact, oldManifold):
        worldManifold=contact.worldManifold
        #state1, state2 = b2GetPointStates(oldManifold, contact.manifold)

        bodyA=contact.fixtureA.body
        bodyB=contact.fixtureB.body
        
        udA = bodyA.userData
        udB = bodyB.userData


        if(udA is not None and udB is not None):

            # both goos
            if(isinstance(udA, Goo) and isinstance(udB, Goo) ):
                pass
            # noo goos
            if( not isinstance(udA, Goo) and not isinstance(udB, Goo) ):
                pass   

            # destroyers
            elif isinstance(udA, GooDestroyerItem):
                # destroy udA
                self.level.toDeleteGoos.add(udB)
            elif isinstance(udB, GooDestroyerItem):
                # destroy udA
                self.level.toDeleteGoos.add(udA)
            #elif isinstance(udA, GoalItem):
            #    print "goal item contact"
            #    #udA.gooBeginsContact(udB)
            #elif isinstance(udB, GoalItem):
            #    print "goal item contact"
            #    #udN.gooBeginsContact(udA)


    def postSolve(self, contact, impulse):
        pass




class BaseLevel(object):

    _killSound = SoundLoader.load('res/sounds/discovery3.wav')

    def __init__(self,world, gameRender):

        self.world = world
        self.destructionListener = LevelDestructionListener(level=self)
        self.contactListener = LevelContactListener(level=self)

        self.world.setDestructionListener(self.destructionListener)
        self.world.setContactListener(self.contactListener)


        self.gameRender = gameRender
        self.debugDraw = DebugDraw(world=None)

        self.wmManager = None
        self.gooGraph = GooGraph(self)
        self.game_items = set()
        self.mouseJoint = None

        self.is_scheduled = False
        self.was_scheduled_bevore_global_pause = False

        self.currentGameItem = None
    

        self.toDeleteGoos = set()

        gooClsDict = RegisteredGoos.Instance().gooClsDict
        self.gooRes = dict()

        for gooName in gooClsDict:
            gooCls = gooClsDict[gooName]
            self.gooRes[gooCls] = 0

        self.justAddedGooOrJoint = False


    def gooOrJointAdded(self):
        #print "jay"
        self.justAddedGooOrJoin = True

        def cb(dt):
            self.justAddedGooOrJoin = False
        Clock.schedule_once(cb, 0.25)


    def removeGoo(self, goo):

        #print "remove gooo"
        for e in self.gooGraph.edges_iter(goo,data=True):
                j = e[2]['joint']
                self.world.destroyJoint(j)
                self.gooGraph.remove_edge(e[0],e[1])
        
        goo.isKilled = True
        goo.pos = goo.body.position
        goo.angle = degrees(goo.body.angle)
        def removeFromGraph(dt):
            self.gooGraph.remove_node(goo)
            #rint "gone"
        Clock.schedule_once(removeFromGraph,0.5)
        self.world.destroyBody(goo.body)
        BaseLevel._killSound.play()

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

        if False: #body is not None:
            gameItem = body.userData
            if isinstance(gameItem, GameItem):
                self.currentGameItem = gameItem
                gameItem.world_on_touch_down(wpos, touch)

            self.mouseJoint = self.world.createMouseJoint(
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
        gameItem = self.currentGameItem
        if gameItem is not None:
            gameItem.world_on_touch_move(wpos, wppos, touch)


        if self.mouseJoint is not None:
            self.mouseJoint.target  =  wpos
        else :
            self.wmManager.world_on_touch_move(wpos, wppos, touch)

    def world_on_touch_up(self, wpos, touch):
        gameItem = self.currentGameItem
        if gameItem is not None:
            gameItem.world_on_touch_up(wpos, touch)
            self.currentGameItem = None

        if self.mouseJoint is not None:
            self.world.DestroyJoint(self.mouseJoint)
            self.mouseJoint = None
        else :
            self.wmManager.world_on_touch_up(wpos, touch)
    def set_wm_manager(self, wmManager):
        self.wmManager = wmManager

    def initPhysics(self):
        self.killBoxVerts = boxVertices(*self.roi)
        self.killBoundingBoxBody = self.world.createBody(position=self.roi[0])
        self.killBoundingBoxBody.createEdgeChainFixture(self.killBoxVerts)

    def start_level(self):
        Clock.schedule_interval(self.updateCaller,1.0/50)

    def stop_level(self):
        Clock.unschedule(self.updateCaller)


    def level_finished(self):
        self.level_widget.level_finished()
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

            if not self.justAddedGooOrJoin:
                if j.userData.breakJoint():
                    self.gooGraph.remove_edge(gooA, gooB)
                    self.world.destroyJoint(j)
                    break

            if False:
                jReacForceV = j.getReactionForce(30)
                j.userData.force = jReacForceV.length
                f = jReacForceV.length
                gamma = 0.004
                normval = 1.0 - numpy.exp(-1.0 * gamma * f)
                realLength = (j.anchorA -  j.anchorB).length
                lengthDiff = realLength - j.length
                if lengthDiff < 0:
                    j.userData.force = 0.0
                else:
                    if not self.justAddedGooOrJoin:
                        if(normval>0.9):
                           gooA = j.bodyA.userData
                           gooB = j.bodyB.userData
                           self.gooGraph.remove_edge(gooA,gooB)
                           self.world.destroyJoint(j)
                           break

        #print "maxdist ",md
    def update(self, dt):
        #print "DT",dt
        self.world.step(float(dt),5,5,5)#
                        # timeStpep=float(dt),
                        # velocityIterations=5,
                        # positionIterations=5,
                        # particleIterations=5)
        #print "step done"
    def postUpdate(self, dt):
        for g in self.toDeleteGoos:
            self.removeGoo(g)

        self.toDeleteGoos.clear()


    def addGoo(self, goo, pos):
        goo.playBuildSound()
        goo.add_to_level(self.world, pos)
        self.gooGraph.add_node(goo)

    #def connectGoos(self, gooA, gooB):
    #    # take param from first goo (so far)
    #    gParam  = gooA.param()
    #    dfn=b2DistanceJointDef(
    #       frequencyHz=gParam.frequencyHz,
    #       dampingRatio=gParam.dampingRatio,
    #       bodyA=gooA.body,bodyB=gooB.body,
    #       localAnchorA=gooA.localAnchor(),
    #       localAnchorB=gooB.localAnchor()
    #    )
    #    j=self.world.createJoint(dfn)
    #    if gParam.autoExpanding:
    #        j.length = gParam.expandingDist
    #    self.gooGraph.add_edge(gooA, gooB, joint=j)
        
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
                jGameItem = j.userData
                assert isinstance(jGameItem, Joint)
                jGameItem.render(gr)
                #gooA.renderJoint(gr,j,gooB)      
                #gooB.renderJoint(gr,j,gooA)  
        def renderAllGoos():
            for goo in self.gooGraph.nodes():
                goo.render(self)
        gr.add_render_item(renderAllGoos,z=4)
        gr.add_render_item(renderGoosJoints,z=3)

        # builder/adder tentative render
        # if and only if there is NO mouse joint
        if self.mouseJoint is None:
            gr.add_render_item(self.wmManager.render, z=3)

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
