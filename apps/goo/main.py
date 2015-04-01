from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock





class GooBall(Widget):
    pass


class GooGame(BoxLayout):
  pass


class GooApp(App):
    def build(self):
        game = GooGame()
        return game


if __name__ == '__main__':
    GooApp().run()
