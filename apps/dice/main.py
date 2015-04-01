
import random

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.widget import Widget



class Dice(object):
    def __init__(self):
        pass

    def __call__(self):
        return random.randint(1,6)


class MultiDice(object):
    def __init__(self):
        pass

    def __call__(self):
        return [random.randint(1,6) for r in range(self.__len__())]

    def __len__(self):
        return 5








class SingleDiceDisplay(BoxLayout):
    def __init__(self, dice,name='unnamed dice',  *args, **kwargs):
        self.value = None
        self.dice = dice
        self.name = name
        super(SingleDiceDisplay, self).__init__(orientation='horizontal')

        self.isBlocked = False
        self.isFixed = False

        # the label displaying the number
        self.diceNameButton = Button(text=self.name,background_color=(0,1,1,1))
        self.add_widget(self.diceNameButton)

        # the label displaying the number
        self.numberLabel = Label(text="")
        self.add_widget(self.numberLabel)

    # run dice and update label
    def runDice(self):
        self.value = self.dice()
        self.numberLabel.text = str(self.value)




class MultiDiceWidget(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(MultiDiceWidget, self).__init__(orientation='vertical')

        # this layout holds the viewers for all single dices
        self.diceDisplayLayout = BoxLayout(orientation='vertical')
        self.add_widget(self.diceDisplayLayout)

        # add single dice viewers
        self.viewers = []
        for i in range(5):
            dice = Dice()
            singleDiceDisplay = SingleDiceDisplay(dice=dice,name='dice %d'%i)
            self.diceDisplayLayout.add_widget(singleDiceDisplay)
            self.viewers.append(singleDiceDisplay)

        t = "run all"
        try :
            import Box2D
            t+= ("boxversion"+Box2D.__version__)
        except ImportError as e:
            t+="NO BOX2D "
            t+=" ({})".format(e)
        # add run all button 
        self.runAllButton = Button(text=t,size_hint=(1,0.2))
        self.add_widget(self.runAllButton)

        def cb(instance):
            self.runDice()
        self.runAllButton.bind(on_release=cb)


    def runDice(self):
        for viewer in self.viewers:
                viewer.runDice()


class DiceAppWidget(BoxLayout):
    def __init__(self, *args, **kwargs):
        super(DiceAppWidget, self).__init__(orientation='horizontal')


        a = MultiDiceWidget()
        #b = MultiDiceWidget()
        #c = MultiDiceWidget()
        self.add_widget(a)
        #self.add_widget(b)
        #self.add_widget(c)

w = DiceAppWidget()

class MyApp(App):
    def build(self):
        return w


if __name__ == '__main__':
    MyApp().run()
