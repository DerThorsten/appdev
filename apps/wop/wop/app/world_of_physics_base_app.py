from kivy.app import App
from wop.widgets import ScreenSelectorWidget
from kivy.storage.jsonstore import JsonStore

hasSaveGamemMod = True
try:
    from wop import SaveGame
except:
    hasSaveGamemMod = False

class WorldOfPhysicsBaseApp(App):
    title = 'World Of Physics!'
    def build(self):

        if hasSaveGamemMod:
            self.savegame = SaveGame('wop_savegame.json')
            #store.put('tito', name='Mathieu', org='kivy')
            print self.savegame.totalPlayTime

        screenSelectorWidget = ScreenSelectorWidget()
        #screenSelectorWidget.level_widget.init_level()
        self.level_widget = screenSelectorWidget.level_widget
        return screenSelectorWidget

    def on_pause(self):
        self.level_widget.on_global_pause()
        self.savegame.on_pause()
        return True
    def on_resume(self):
        # Here you can check if any data needs replacing (usually nothing)
        self.level_widget.on_global_resume()
        if hasSaveGamemMod:    
            self.savegame.on_resume()


    def on_stop(self):
        if hasSaveGamemMod:
            self.savegame.on_stop()

    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'debugDraw' : False,
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

