from pyglet import media


#issue 17
class Sound:
    def __init__(self, file_path=None):
        '''!
            @brief  Initializes the class Sound. If a file path is named, uses that to load the sound file
            @param sound_file_path  String of the file path for the sound file
            @param  player  Pyglet media player class that handles sound
            @param sound_file   Sound file that will be used for the class
            @return Returns an initialization of the Sound class with the specified name
            @see (https://pyglet.readthedocs.io/en/latest/programming_guide/media.html)
            @see [issue#17] (https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/17)
        '''
        self.sound_file_path = file_path
        self.player = media.Player()
        self.sound_file = None
        if file_path != None:
            self.sound_file = media.load(file_path)

    def load_sound(self, file_path):
        '''!
            @brief  Loads the sound into the media player
            @param sound_file   String of the file path for the sound file
            @see [issue#17] (https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/17)
        '''
        self.sound_file = media.load(file_path)

    def play_sound(self):
        '''!
            @brief  Plays the sound file contained in the class
            @see [issue#17] (https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/17)
            @return Returns a 1 to signify successful completion.
        '''
        self.player.queue(self.sound_file)
        if not self.player.playing:
            self.player.play()
        else:
            self.player.next_source()
            self.player.play()
        return 1


class BackgroundSound(Sound):
    '''Subclass of sound for sounds that will loop'''
    def __init__(self, file_path=None):
        super().__init__(file_path)
        '''!
            @brief Initializes the class BackgroundSound. This is to separate sounds that will loop and have different
            features from normal sounds.
            @param sound_file_path  String of the file path for the sound file
            @param  player  Pyglet media player class that handles sound
            @param sound_file   Sound file that will be used for the class
            @return Returns an initialization of the BackgroundSound class with the specified name
        '''
        self.player.loop = True
