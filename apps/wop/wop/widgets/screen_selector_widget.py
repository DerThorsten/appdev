from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<ScreenSelectorWidget>:
    levelWidget: levelWidget
    screen_manager: screen_manager
    ScreenManager:
        id: screen_manager

        Screen:
            name: 'main_menu_screen'
            MainMenuWidget:
                screen_manager: screen_manager
        Screen:
            name: 'main_settings_screen'
            MainSettingWidget:
                screen_manager: screen_manager
        Screen:
            name: 'level_selector_screen'
            LevelSelectorWidget:
                screen_manager: screen_manager
        Screen:
            name: 'level_render_screen'
            on_pre_enter: levelWidget.viewer.on_pre_enter()
            on_pre_leave: levelWidget.viewer.on_pre_leave()
            on_enter: levelWidget.viewer.on_enter()
            on_leave: levelWidget.viewer.on_leave()
            LevelWidget:
                screen_manager: screen_manager
                id: levelWidget


""")
class ScreenSelectorWidget(BoxLayout):
    levelWidget = ObjectProperty(None)
    screen_manager = ObjectProperty(None)
    def __init__(self,*args,**kwargs):
        super(ScreenSelectorWidget,self).__init__(*args,**kwargs)
