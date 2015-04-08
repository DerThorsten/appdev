from abc import ABCMeta ,abstractmethod
from Box2D import *

class GameItem(object):
    def __init__(self):
        pass



class NewGameItem(object):
    def __init__(self):
        pass
    

    @abstractmethod
    def bounding_box_size(self):
        pass

    @abstractmethod    
    def bounding_box_pos(self):
        pass




class PhysicalGameItem(NewGameItem):

    @abstractmethod
    def shape(self):
        """
            vertices or b2Shapes.

            The shape is always in a local coordinate
            system. 
            This mean the position of the body is at zero
            and the body has a 
        """
        pass

    @abstractmethod
    def pos(self):
        """
            global position of the object
        """
        pass


    @abstractmethod
    def angle(self):
        """ Angle of the shape:

            Angle with respect to the local anchor
        """
        pass

  
    @abstractmethod
    def bounding_box_size(self):
        pass

    @abstractmethod
    def bounding_box_pos(self):
        pass
