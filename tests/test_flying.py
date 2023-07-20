from unittest.mock import Mock

import pyglet
import pytest

from tempus_fugit_minecraft.window import Window


@pytest.fixture(scope="class")
def window():
    yield Window()


class TestFlying:
    @pytest.fixture(autouse=True)
    def teardown(self, window):
        window.flying = False

    def test_ascend(self, window):
        window.on_key_press(pyglet.window.key.TAB, Mock())
        window.on_key_press(pyglet.window.key.SPACE, Mock())
        assert window.model.player.ascend is True

    def test_descend(self, window):
        window.on_key_press(pyglet.window.key.TAB, Mock())
        window.on_key_press(pyglet.window.key.LSHIFT, Mock())
        assert window.model.player.descend is False
