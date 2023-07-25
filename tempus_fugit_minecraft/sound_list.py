from tempus_fugit_minecraft import sound
"""!
@brief File to contain all sound variables and the SoundList class that will contain and adjust volume controls.
"""

class SoundList():
    def __init__(self):
        """!
        @brief The SoundList class will be used to group different types of sounds so that they can all be modified 
        at the same time.
        @param dictionary   A dict class object that uses the name of sounds as keys and refers to a Sound class object
            as the value.
        @param default_volume   A float between 0 and 1 that determines the initial volume for all sounds in the sound_list
        @returns An instance of the SoundList class with the specified name.
        """
        self.default_volume = .5
        self.dictionary = dict()
    def add_sound_to_dictionary(self, sound_name:str, sound):
        """!
            @brief The add_sound_to_dictionary function adds the name of of a sound as the key and the Sound class object
                as the value. If the sound already exists, it will return 0. If it does not, it will return sound
            @param sound_name   A string value that will be used as the key for the dictionary
            @param sound    A Sound class object that will be used as the value referenced by the key in the dictionary
        """
        try:
            self.dictionary[sound_name]
            return 0
        except:
            self.dictionary[sound_name] = sound
            return sound
        
    def adjust_all_volume(self, volume_increment):
        """!
            @brief The adjust_volume function allows for the adjustment of all sounds contained in the class
                If the sum of the current volume of the sound object plus the volume adjustment is less than 0 or
                greater than 1, it will default to 0 or 1.
            @param volume_increment A float value that determines how much to adjust the volume. 
        """
        for sound in self.dictionary.values():
            if sound.player.volume + volume_increment > 1:
                sound.player.volume = 1
            elif sound.player.volume + volume_increment < 0:
                sound.player.volume = 0
            else:
                sound.player.volume += volume_increment
    
    def set_all_volume(self, volume):
        """!
            @brief The adjust_volume function allows a direct setting of the volume of all sounds in the class.
            @param volume A float value that determines the volume
        """
        for sound in self.dictionary.values():
            if volume > 1:
                sound.player.volume = 1
            elif volume < 0:
                sound.player.volume = 0
            else:
                sound.player.volume == volume

    def get_sound(self, sound_name:str):
        """!
            @brief Grabs the sound with the corresponding name from the sound_list. If it does not exist, return 0
            @param sound_name   A string that is the name of the sound being grabbed
            @return Returns the sound if it exists in the dictionary list. Else returns a 0
        """
        try:
            sound = self.dictionary[sound_name]
            return sound
        except:
            return 0




#Sound Effects
sound_effects_list = SoundList()
sound_effects_list.add_sound_to_dictionary('rock_hit', sound.Sound("assets/sound/rock_hit.wav")) 

#Background Sounds
background_sound_list = SoundList()
background_sound_list.add_sound_to_dictionary('wind_blowing', sound.BackgroundSound("assets/sound/wind-blowing-ambience.wav"))


    