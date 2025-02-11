"""!
@brief File to contain all sound variables and the SoundList class that will contain and adjust volume controls.
"""
from tempus_fugit_minecraft import sound

class SoundList():
    """!
        @brief The SoundList class will be used to group different types of sounds so that they can all be modified 
        at the same time.
    """
    def __init__(self):
        """!
        @param dictionary   A dict class object that uses the name of sounds as keys and refers to a Sound class object
            as the value.
        @param default_volume   A float between 0 and 1 that determines the initial volume for all sounds in the sound_list
        @returns An instance of the SoundList class with the specified name.
        @see [Issue#99](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/99)
        """
        self.default_volume = 1
        self.dictionary = dict()
    def add_sound_to_dictionary(self, sound_name:str, sound:sound.Sound):
        """!
            @brief The add_sound_to_dictionary function adds the name of of a sound as the key and the Sound class object
                as the value. If the sound already exists, it will return 0. If it does not, it will return sound
            @param sound_name   A string value that will be used as the key for the dictionary
            @param sound    A Sound class object that will be used as the value referenced by the key in the dictionary
            @see [Issue#99](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/99)
        """
        try:
            self.dictionary[sound_name]
            return 0
        except:
            self.dictionary[sound_name] = sound
            return sound
        
    def change_all_sound_volume_in_dictionary(self, volume_change_by_value_between_0_and_1:float):
        """!
            @brief The adjust_volume function allows for the adjustment of all sounds contained in the class
                If the sum of the current volume of the sound object plus the volume adjustment is less than 0 or
                greater than 1, it will default to 0 or 1.
            @param volume_change_by_value_between_0_and_1 A float value that determines how much to adjust the volume.
            @see [Issue#99](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/99)
        """
        for sound in self.dictionary.values():
            if sound.player.volume + volume_change_by_value_between_0_and_1 > 1:
                sound.player.volume = 1
            elif sound.player.volume + volume_change_by_value_between_0_and_1 < 0:
                sound.player.volume = 0
            else:
                sound.player.volume += volume_change_by_value_between_0_and_1
    
    def set_all_sound_volume_in_dictionary(self, set_volume_by_value_between_0_and_1:float):
        """!
            @brief The adjust_volume function allows a direct setting of the volume of all sounds in the class.
            @param volume A float value that determines the volume
            @see [Issue#99](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/99)
        """
        for sound in self.dictionary.values():
            if set_volume_by_value_between_0_and_1 > 1:
                sound.player.volume = 1
            elif set_volume_by_value_between_0_and_1 < 0:
                sound.player.volume = 0
            else:
                sound.player.volume = set_volume_by_value_between_0_and_1

    def get_sound(self, sound_name:str):
        """!
            @brief Grabs the sound with the corresponding name from the sound_list. If it does not exist, return 0
            @param sound_name   A string that is the name of the sound being grabbed
            @return Returns the sound if it exists in the dictionary list. Else returns a 0
            @see [Issue#99](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/99)
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
