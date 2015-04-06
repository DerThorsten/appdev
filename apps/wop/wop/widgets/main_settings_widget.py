from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<MainSettingWidget>:
    orientation: 'vertical'
    Button: 
        text: "base settings"
        on_press: app.open_settings()
    Button:
        text: "back"
        on_press: root.screen_manager.current = 'main_menu_screen'
""")
class MainSettingWidget(BoxLayout):
    pass
