from tempus_fugit_minecraft import sound
"""!
@brief File to contain all sound variables
"""

class SoundList():
    """!
        @brief The SoundList class will be used to group different types of sounds so that they can all be modified 
        at the same time.
        @param dictionary   A dict class object that uses the name of sounds as keys and refers to a Sound class object
            as the value.
        @returns An instance of the SoundList class with the specified name.
    """
    def __init__(self):
        self.dictionary = dict()
    def add_sound_to_dictionary(self, sound_name:str, sound):
        """
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
    def adjust_volume(self, volume_increment):
        return



#Sound Effects
rock_hit_sound = sound.Sound("assets/sound/rock_hit.wav")

#Background Sounds
wind_blowing = sound.BackgroundSound("assets/sound/wind-blowing-ambience.wav")


    