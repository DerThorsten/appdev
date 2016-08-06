from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.logger import Logger

import wop.level

Builder.load_string("""
<LevelSelectorWidget>:
    orientation: 'vertical'
    Button:
        text: "level 1"
        background_color: (0,0,0,0)
        color: (0.3,1,0.3,1)
        font_size: 80
        font_name: "CBlocks"
        on_press: root.on_select_level("level-1")
    Button:
        text: "level 2"
        background_color: (0,0,0,0)
        color: (0.3,1,0.3,1)
        font_size: 80
        font_name: "CBlocks"
        on_press: root.on_select_level("level-2")
    Button:
        text: "SpaceLevel"
        background_color: (0,0,0,0)
        color: (0.3,1,0.3,1)
        font_size: 80
        font_name: "CBlocks"
        on_press: root.on_select_level("SpaceLevel")
    Button:
        text: "back"
        background_color: (0,0,0,0)
        color: (1,0.3,0.3,1)
        font_size: 80
        font_name: "CBlocks"
        on_press: root.screen_manager.current = 'main_menu_screen'
""")
class LevelSelectorWidget(BoxLayout):
    screen_manager = ObjectProperty(None)
    level_widget = ObjectProperty(None)
    def __init__(self, *args, **kwargs):
        super(LevelSelectorWidget, self).__init__(*args,**kwargs)


    def on_select_level(self, levelStr):
        Logger.debug("LevelSelectorWidget: selected level '%s'"%levelStr)
        
        gr = self.level_widget.levelCanvasWidget

        if levelStr == "level-1":
            level = wop.level.SimpleLevel1(gameRender=gr)
        elif levelStr == "level-2":
            level = wop.level.SimpleLevel2(gameRender=gr)
        elif levelStr == "SpaceLevel":
            level = wop.level.SpaceLevel(gameRender=gr)


        Logger.debug("LevelSelectorWidget: pass level to level_widget")
        self.level_widget.set_level(level)

        Logger.debug("LevelSelectorWidget: switch screen")
        self.screen_manager.current = 'level_render_screen'
        Logger.debug("LevelSelectorWidget: switch done")
