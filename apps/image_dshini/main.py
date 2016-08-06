
import random
from kivy.lang import Builder
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatter import Scatter
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget
from kivy.graphics.texture import Texture
import pygame
import io
from kivy.core.image import Image as CoreImage
from kivy.graphics import *
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty


import numpy 



def loadImageAsArray(path, loadAs3d=True):
    surf = pygame.image.load(path)
    if loadAs3d:
        array = pygame.surfarray.array3d(surf)
    else :
        array = pygame.surfarray.array2d(surf)

    alpha = pygame.surfarray.array_alpha(surf)

    print "apha",alpha.shape,alpha.min(),alpha.max()

    aMin = alpha.min()
    if aMin < 255:
        array = numpy.concatenate([array,alpha[:,:,None]],axis=2)


    array = numpy.swapaxes(array,0,1)   
    array = numpy.flipud(array)
    array = numpy.ascontiguousarray(array)
    #array = numpy.asfortranarray(array)
    return array

def arrayToTexture(array):
    if array.ndim == 2:
        assert False
    x,y = array.shape[0:2]
    texture = Texture.create(size=(y,x))
    strArray = array.tostring()
    if array.shape[2] == 3:
        colorfmt = 'rgb'
    elif array.shape[2] == 4:
        colorfmt = 'rgba'

    texture.blit_buffer(strArray, colorfmt=colorfmt, bufferfmt='ubyte')
    return texture

Builder.load_string("""
<PictureWidget>:
    size_hint: (None, None)
    canvas.after:
        Rectangle:
            texture: self.texture
            size: root.imgSize
            pos: root.pos
""")
class PictureWidget(BoxLayout):
    image = ObjectProperty(None)
    source = ObjectProperty(None)
    texture = ObjectProperty(None)
    imgSize = ObjectProperty((100,100))

    def setPicture(self, array):
        x,y = array.shape[0:2]
        self.imgSize = (y,x)
        self.texture = arrayToTexture(array)
        
        

Builder.load_string("""
<DummyWidgey>:
    slider: slider
    pictureWidget: pictureWidget

    BoxLayout:
        StencilView:
            BoxLayout:
                size_hint: (0.5,1)
                Scatter:
                    size_hint: (None, None)
                    BoxLayout:
                        size_hint: (None, None)
                        PictureWidget:
                            size_hint: (None, None)
                            id: pictureWidget
    Slider:
        id: slider
        text: "le slider"
        min: 0
        max: 1
        value: 0.5
        steps: 20
        on_value: root.changed()
    BoxLayout:
        size_hint: (0.5,1)
        orientation: "horizontal" 
        FileChooserIconView:
            rootpath:"/home/tbeier/src/appdev/apps/"
            id: filechooser
            on_selection: root.image_selected(filechooser.selection)
""")
class DummyWidgey(BoxLayout):
    pictureWidget = ObjectProperty(None)
    array = ObjectProperty(None)
    def changed(self):
        print "changed"
        t = self.pictureWidget.texture
        if t is not None:
            print self.slider.value
            a = self.array.copy()
            a[:,:,0]*=self.slider.value
            self.pictureWidget.setPicture(a)
        else:
            print "we have no texture DUDE"
    def image_selected(self,path):

        try:
            array = loadImageAsArray(path[0])
            print "array ",array.shape,array.dtype
            self.pictureWidget.setPicture(array)
            self.array = array
        except:
            pass

class ImageDshiniApp(App):
    def build(self):
        return DummyWidgey()


if __name__ == '__main__':
    ImageDshiniApp().run()
