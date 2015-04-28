from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.lang import Builder

Builder.load_string("""
<MainMenuWidget>:
    orientation: 'vertical'
    Label:
        text: 'World Of Physics'
        color: (1,0.3,0.3,1)
        font_size: 80
        font_name: "CBlocks"

    Button:
        size_hint: (1,1)
        text: "Play"
        color: (0.3,1,0.3,1)
        font_size: 80
        font_name: "CBlocks"
        on_press: root.screen_manager.current = 'level_selector_screen'
        background_color: (0,0,0,0)
    BoxLayout:
        size_hint: (1,0.5)
        orientation: 'horizontal'
        Button:
            text: "Settings"
            color: (0.3,0.3,1,1)
            font_size: 80
            font_name: "CBlocks"
            on_press: root.screen_manager.current = 'main_settings_screen'
            background_color: (0,0,0,0)
        Button:
            text: "Exit"
            color: (0.6,0.6,0.2,1)
            font_size: 80
            font_name: "CBlocks"
            background_color: (0,0,0,0)

""")
class MainMenuWidget(BoxLayout):
    pass
