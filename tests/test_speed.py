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
        window.model.player.walking_speed_in_blocks_per_second = 5

    #Issue #61 Test Q key down to increase speed
    def test_Q_key(self, window): 
        assert window.model.player.walking_speed_in_blocks_per_second == 5

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.model.player.walking_speed_in_blocks_per_second == 10

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.model.player.walking_speed_in_blocks_per_second == 15

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.Q, Mock())
        assert window.model.player.walking_speed_in_blocks_per_second == 20

    #Issue #61 Test E key down to decrease speed
    def test_E_key(self, window):
        window.model.player.walking_speed_in_blocks_per_second = 20
        assert window.model.player.walking_speed_in_blocks_per_second == 20

        window.on_key_press(pyglet.window.key.E, Mock())
        assert window.model.player.walking_speed_in_blocks_per_second == 15

        window.on_key_press(pyglet.window.key.E, Mock())
        assert window.model.player.walking_speed_in_blocks_per_second == 10

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.E, Mock())
        assert window.model.player.walking_speed_in_blocks_per_second == 5