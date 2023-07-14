import pyglet
import pytest
from unittest.mock import Mock
from tempus_fugit_minecraft.window import Window

@pytest.fixture(scope="class")
def window():
    yield Window()

class TestSpeed:
    @pytest.fixture(autouse=True)
    def teardown(self, window):
        window.player.walking_speed = 5

    def test_Q_key(self, window): # Test Q key down to increase speed
        assert window.player.walking_speed == 5

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.player.walking_speed == 10

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.player.walking_speed == 15

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.player.walking_speed == 20

    def test_E_key(self, window): # Test E key down to Decrease speed
        window.player.walking_speed = 20
        assert window.player.walking_speed == 20

        window.on_key_press(pyglet.window.key.E, Mock())
        assert window.player.walking_speed == 15

        window.on_key_press(pyglet.window.key.E, Mock())
        assert window.player.walking_speed == 10

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.E, Mock())
        assert window.player.walking_speed == 5
