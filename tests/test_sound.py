import pytest
import pyglet
import os
from tempus_fugit_minecraft.sound import Sound

@pytest.fixture(scope="class")
def sound():
    pyglet.options['audio'] = ('silent')
    yield Sound()

parent_directory = os.getcwd()

class TestSound:
    def test_load_sound(self, sound):
        sound.load_sound(parent_directory + "/assets/sound/rock_hit.wav")
        assert sound.sound_file
        
    def test_play_sound(self, sound):
        assert sound.play_sound()