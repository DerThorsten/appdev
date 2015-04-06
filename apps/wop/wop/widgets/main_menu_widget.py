from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<MainMenuWidget>:
    orientation: 'vertical'
    Button:
        text: "Play"
        on_press: root.screen_manager.current = 'level_selector_screen'
    Button:
        text: "Settings"
        on_press: root.screen_manager.current = 'main_settings_screen'
    Button:
        text: "Exit"

""")
class MainMenuWidget(BoxLayout):
    pass
