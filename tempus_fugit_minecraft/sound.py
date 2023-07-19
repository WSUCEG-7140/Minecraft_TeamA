from pyglet import media


#issue 17
class Sound:
    def __init__(self, file_path=None):
        '''!Initializes the class. If a file path is named, uses that to load the sound file
            @param string The file path for the sound file'''
        self.sound_file_path = file_path
        self.player = media.Player()
        if file_path != None:
            self.sound_file = media.load(file_path)

    def load_sound(self, file_path):
        '''!Loads the sound into the media player
            @param string The file path for the sound file'''
        self.sound_file = media.load(file_path)

    def play_sound(self):
        '''!plays the sound contained in the class'''
        self.player.queue(self.sound_file)
        if not self.player.playing:
            self.player.play()
        else:
            self.player.next_source()
            self.player.play()
        return 1

