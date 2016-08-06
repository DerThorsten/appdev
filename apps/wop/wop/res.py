import numpy
from kivy.core.image import Image as CoreImage
from kivy.core.audio import SoundLoader
from singleton import *

class FileImage(CoreImage):
    def __init__(self,filename, *args, **kwargs):
        super(FileImage,self).__init__(filename)
        self.filename = filename




class FileTextures(object):
    blackGoo  = FileImage("res/black_goo_128.png")
    greenGoo  = FileImage("res/green_goo_128.png")
    pinkGoo  = FileImage("res/pink_goo_128.png")
    anchorGoo  = FileImage("res/amboss_goo_128.png")



@Singleton
class FileImages(object):
    def __init__(self):
        self.fileImages = dict()

    def registerImage(self, name, path):
        img = FileImage(path)
        img.load(path)
        self.fileImages[name] = img
    def getImage(self, name):
        #print self.fileImages[name]
        return self.fileImages[name]

def registerImage(name, path):
    FileImages.Instance().registerImage(name, path)

def getImage(name):
    return FileImages.Instance().getImage(name)



