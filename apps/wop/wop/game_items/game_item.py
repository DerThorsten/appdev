from abc import ABCMeta ,abstractmethod
from Box2D import *
from kivy.logger import Logger

class GameItem(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        pass
    def world_on_touch_down(self, wpos, touch):
        Logger.debug("GameItem down")
    def world_on_touch_move(self, wpos, wppos, touch):
        Logger.debug("GameItem move")
    def world_on_touch_up(self, wpos, touch):
        Logger.debug("GameItem   up")


    #@abstractmethod
    def add_to_level(self, world, pos, angle, scale):
        pass


    def remove_from_world(self):
        pass


class GooDestroyerItem(GameItem):
    def __init__(self):
        super(GooDestroyerItem,self).__init__()
        self.body = None

