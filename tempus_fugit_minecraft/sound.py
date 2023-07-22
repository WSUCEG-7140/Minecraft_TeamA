from pyglet import media


#issue 17
class Sound:
    def __init__(self, file_path=None):
        """!
        @brief Initializes the Sound class.
        @details If a file path is named, uses that to load the sound 
            file        
        @param file_path string The file path for the sound file
        @see [Issue#17](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/17)
        """
        self.sound_file_path = file_path
        self.player = media.Player()
        self.sound_file = None
        if file_path != None:
            self.sound_file = media.load(file_path)

    def load_sound(self, file_path):
        """!
        @brief Loads the sound into the media player.
        @param file_path string The file path for the sound file
        @see [Issue#17](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/17)
        """
        self.sound_file = media.load(file_path)

    def play_sound(self):
        """!
        @brief plays the sound contained in the class.
        @see [Issue#17](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/17)
        """
        self.player.queue(self.sound_file)
        if not self.player.playing:
            self.player.play()
        else:
            self.player.next_source()
            self.player.play()
        return 1


class BackgroundSound(Sound):
    
    """!
    @brief Subclass of sound for sounds that will be repeated
    """
    def __init__(self, file_path=None):
        super().__init__(file_path)
        self.player.loop = True
