from kivy.app import App
from wop.widgets import ScreenSelectorWidget

class WorldOfPhysicsBaseApp(App):

    def build(self):
        screenSelectorWidget = ScreenSelectorWidget()
        #screenSelectorWidget.level_widget.init_level()
        return screenSelectorWidget

    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'debugDraw' : True,
            'debugDrawZ' : 100
        })

    def build_settings(self, settings):
        jsondata = """
        [
            { 
                "type": "title",
                "title": "Test application" 
            },

            { 
                "type": "options",
                "title": "My first key",
                "desc": "Description of my first key",
                "section": "section1",
                "key": "key1",
                "options": ["value1", "value2", "another value"] 
            },

            { 
                "type": "bool",
                "title": "show debug render",
                "desc": "Description of my second key",
                "section": "section1",
                "key": "debugDraw" 
            },
            { 
                "type": "numeric",
                "title": "Z value for debug draw layer",
                "desc": "Description of my second key",
                "section": "section1",
                "key": "debugDrawZ" 
            }
        ]
        """
        settings.add_json_panel('Test application',
            self.config, data=jsondata)

    def on_config_change(self, config, section, key, value):
            if config is self.config:
                token = (section, key)
                print token
                #if token == (u'section1', u'key1'):
                #    print('Our key1 have been changed to', value)
                #elif token == ('section1', 'key2'):
                #    print('Our key2 have been changed to', value)

            #Config.get(u'section1',u'debugDraw')

    def on_pause(self):
        # Here you can save data if needed
        return True
    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        pass
