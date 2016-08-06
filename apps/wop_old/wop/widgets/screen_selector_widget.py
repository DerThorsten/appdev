from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<ScreenSelectorWidget>:
    level_widget: level_widget
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
                level_widget: level_widget
        Screen:
            name: 'level_render_screen'
            on_pre_enter: level_widget.on_pre_enter()
            on_pre_leave: level_widget.on_pre_leave()
            on_enter: level_widget.on_enter()
            on_leave: level_widget.on_leave()
            LevelWidget:
                screen_manager: screen_manager
                id: level_widget


""")
class ScreenSelectorWidget(BoxLayout):
    level_widget = ObjectProperty(None)
    screen_manager = ObjectProperty(None)
    def __init__(self,*args,**kwargs):
        super(ScreenSelectorWidget,self).__init__(*args,**kwargs)
