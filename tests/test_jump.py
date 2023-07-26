import pyglet
import pytest
from unittest.mock import Mock
from tempus_fugit_minecraft.window import Window

@pytest.fixture(scope="class")
def window():
    yield Window()

class TestJump:
    @pytest.fixture(autouse=True)
    def teardown(self, window):
        window.game_model.player.jump_speed_in_blocks_per_second = window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND

    # issue#39 Test Q key down to increase jump speed
    def test_Q_key(self, window): 
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND)

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND)+ 5

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.Q, Mock())
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND) + 15

    #issue#39 Test E key down to decrease jump speed
    
    
    def test_E_key(self, window):
        window.game_model.player.jump_speed_in_blocks_per_second = window.game_model.player.MAX_JUMP_SPEED_IN_BLOCKS_PER_SECOND
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND) + 10

        window.on_key_press(pyglet.window.key.E, Mock())
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND) + 5

        window.on_key_press(pyglet.window.key.E, Mock())
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND)

        #Issue #39 Players can jump 1 unit at least
        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.E, Mock())
        assert int(window.game_model.player.jump_speed_in_blocks_per_second) == int(window.game_model.player.INITIAL_JUMP_SPEED_IN_BLOCKS_PER_SECOND)