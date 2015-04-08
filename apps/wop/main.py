'''
WorldOfPhysics
======

A simple world-of-goo clone
'''

__version__ = "0.1"
from wop.app import WorldOfPhysicsBaseApp
from kivy.app import App

class WorldOfPhysics(WorldOfPhysicsBaseApp):
    pass

if __name__ == '__main__':
    WorldOfPhysics().run()

