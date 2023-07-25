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
        window.model.player.jump_speed = window.model.player.MIN_JUMP_SPEED

    #Issue #39 Test Q key down to increase jump
    def test_Q_key(self, window): 
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED)

        window.on_key_press(pyglet.window.key.Q, Mock())
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED)+ 5

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.Q, Mock())
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED) + 15

    #Issue #39 Test E key down to decrease jump
    
    
    def test_E_key(self, window):
        window.model.player.jump_speed = window.model.player.MAX_JUMP_SPEED
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED) + 10

        window.on_key_press(pyglet.window.key.E, Mock())
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED) + 5

        window.on_key_press(pyglet.window.key.E, Mock())
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED)

        #Issue #39 Players can jump 1 unit at least
        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.E, Mock())
        assert int(window.model.player.jump_speed) == int(window.model.player.MIN_JUMP_SPEED)