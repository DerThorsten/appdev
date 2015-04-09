from kivy.storage.jsonstore import JsonStore


class SaveGame(object):
    def __init__(self, filename):
        # create store
        self.store =  JsonStore(filename)

        store = self.store

      
        self.totalPlayTime = 0.0
        self.playerName = 'player 0'

        if store.exists('meta_data'):
            self.totalPlayTime  = store.get('meta_data')['totalPlayTime']
            print self.totalPlayTime
        else :
            store.put('meta_data',totalPlayTime=self.totalPlayTime)


    def on_stop(self):
        self.put_to_file()

    def on_pause(self):
        self.put_to_file()

    def on_resume(self):
        self.put_to_file()

    def on_exit(self):
        self.put_to_file()


    def put_to_file(self):
        store = self.store
        store.put('meta_data',totalPlayTime=self.totalPlayTime)



