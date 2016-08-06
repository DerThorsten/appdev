from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<MainSettingWidget>:
    orientation: 'vertical'
    Button: 
        text: "base settings"
        background_color: (0,0,0,0)
        color: (1,0.3,0.3,1)
        font_size: 80
        font_name: "CBlocks"

        on_press: app.open_settings()
    Button:
        background_color: (0,0,0,0)
        text: "back"
        color: (0.3,1,0.3,1)
        font_size: 80
        font_name: "CBlocks"
        on_press: root.screen_manager.current = 'main_menu_screen'
""")
class MainSettingWidget(BoxLayout):
    pass
