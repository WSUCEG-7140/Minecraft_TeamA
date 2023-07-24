import pytest
import pyglet
import os
from tempus_fugit_minecraft.sound import Sound
from tempus_fugit_minecraft.sound_list import SoundList

parent_directory = os.getcwd()


@pytest.fixture(scope="class")
def sound():
    pyglet.options['audio'] = ('silent')
    yield Sound()

@pytest.fixture(scope="class")
def sound_list():
    pyglet.options['audio'] = ('silent')
    yield SoundList()

class TestSound:
    def test_load_sound(self, sound):
        sound.load_sound(parent_directory + "/assets/sound/rock_hit.wav")
        assert sound.sound_file

    def test_play_sound(self, sound):
        assert sound.play_sound()

class TestSoundList:
    def test_add_sound_to_dictionary(self, sound_list):
        sound_list.add_sound_to_dictionary('rock_hit', Sound(parent_directory + "/assets/sound/rock_hit.wav"))
        assert sound_list.dictionary['rock_hit']
        assert not sound_list.add_sound_to_dictionary('rock_hit', Sound(parent_directory + "/assets/sound/rock_hit.wav"))
    
    def test_adjust_all_volume(self, sound_list):
        sound_list.add_sound_to_dictionary('rock_hit1', Sound(parent_directory + "/assets/sound/rock_hit.wav"))
        sound_list.add_sound_to_dictionary('rock_hit2', Sound(parent_directory + "/assets/sound/rock_hit.wav"))
        sound_list.add_sound_to_dictionary('rock_hit3', Sound(parent_directory + "/assets/sound/rock_hit.wav"))
        rock_hit_1_volume = sound_list.dictionary['rock_hit1'].volume
        rock_hit_2_volume = sound_list.dictionary['rock_hit2'].volume
        rock_hit_3_volume = sound_list.dictionary['rock_hit3'].volume
        sound_list.adjust_all_volume(.1)
        assert rock_hit_1_volume != sound_list.dictionary['rock_hit1'].volume
        assert rock_hit_2_volume != sound_list.dictionary['rock_hit2'].volume
        assert rock_hit_3_volume != sound_list.dictionary['rock_hit3'].volume
        sound_list.adjust_all_volume(-1)
        assert sound_list.dictionary['rock_hit1'].volume == 0
        sound_list.adjust_all_volume(2)
        assert sound_list.dictionary['rock_hit1'].volume == 1
