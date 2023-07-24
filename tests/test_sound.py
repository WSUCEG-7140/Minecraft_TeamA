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