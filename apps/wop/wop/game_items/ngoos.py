import numpy
from math import degrees
from abc import ABCMeta ,abstractmethod
# Box2D
from pybox2d import *

# kivy
from kivy.core.image import Image as CoreImage
from game_item import GameItem
from kivy.logger import Logger
from kivy.graphics import *
from kivy.core.audio import SoundLoader

from wop import CanvasDraw, DebugDraw


class GooParam(object):
    def __init__(self,
        shape = 'ellipse', 
        gooSize = (2.0, 2.0),
        allowsRotation = True,
        friction = 10.0,
        density = 1.0,
        gravityMultiplier = 1.0,
        minGooDist = 4.0,
        maxGooDist = 8.0,
        addIfAnyToClose = True,
        autoExpanding = True,
        expandingDist = None,
        frequencyHz = 2.0,
        dampingRatio = 0.1,
        minBuildEdges = 2,
        maxBuildEdges = 5,
        canBeAddedAsJoint = True,
        addAsJointDist = None,
        removable = False,
        connectsNonGoos = False
    ):

        # graph Param
        self.shape = shape
        self.gooSize = gooSize
        self.allowsRotation = allowsRotation
        self.friction = friction
        self.density = density
        self.gravityMultiplier = gravityMultiplier
        self.minGooDist = minGooDist
        self.maxGooDist = maxGooDist
        self.addIfAnyToClose = addIfAnyToClose
        self.autoExpanding = autoExpanding
        self.expandingDist = expandingDist
        if self.expandingDist is None:
            self.expandingDist = self.maxGooDist

        self.frequencyHz = frequencyHz
        self.dampingRatio = dampingRatio
        self.minBuildEdges = minBuildEdges
        self.maxBuildEdges = maxBuildEdges
        self.canBeAddedAsJoint = canBeAddedAsJoint
        self.addAsJointDist = addAsJointDist
        if self.addAsJointDist is None:
            self.addAsJointDist = min(*self.gooSize)
        self.removable = removable
        self.connectsNonGoos = connectsNonGoos




class Goo(GameItem):
    __metaclass__ = ABCMeta

