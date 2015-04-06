from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<LevelSelectorWidget>:
    Button:
        text: "level 1"
        on_press: root.screen_manager.current = 'level_render_screen'
    Button:
        text: "level 2"
    Button:
        text: "level 3"
    Button:
        text: "back"
        on_press: root.screen_manager.current = 'main_menu_screen'
""")
class LevelSelectorWidget(BoxLayout):
    screen_manager = ObjectProperty(None)
