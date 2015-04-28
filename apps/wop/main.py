'''
WorldOfPhysics
======

A simple world-of-goo clone
'''

__version__ = "0.5"
from wop.app import WorldOfPhysicsBaseApp
from kivy.app import App


from kivy.core.text import LabelBase  
LabelBase.register(name="CBlocks",  
                   fn_regular="res/fonts/From Cartoon Blocks.ttf")
LabelBase.register(name="ka1",  
                   fn_regular="res/fonts/ka1.ttf")


class WorldOfPhysics(WorldOfPhysicsBaseApp):
    pass

if __name__ == '__main__':
    WorldOfPhysics().run()

    
