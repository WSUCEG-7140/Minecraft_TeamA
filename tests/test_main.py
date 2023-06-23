from unittest.mock import Mock

import pyglet
import pytest

from tempus_fugit_minecraft.main import Window


@pytest.fixture(scope="class")
def window():
    window = Window()
    return window


class TestPauseMenu:
    @staticmethod
    def mock_pause(window):
        if not window.paused:
            window.on_key_press(pyglet.window.key.ESCAPE, Mock())

    @staticmethod
    def mock_resume(window):
        if window.paused:
            window.on_key_press(pyglet.window.key.ESCAPE, Mock())

    def test_on_key_press(self, window):
        self.mock_pause(window)
        assert window.paused

        self.mock_resume(window)
        assert not window.paused

    def test_update(self, window):
        self.mock_pause(window)
        before = window.model.process_queue()
        window.update(0)
        after = window.model.process_queue()

        assert before == after

    def test_on_resize(self, window):
        RESIZE_WIDTH = RESIZE_HEIGHT = 100

        self.mock_pause(window)
        window.on_resize(RESIZE_WIDTH, RESIZE_HEIGHT)
        assert window.pause_label.x == RESIZE_WIDTH // 2
        assert window.pause_label.y == RESIZE_HEIGHT // 2

        self.mock_resume(window)

    def test_pause_and_resume_game(self, window):
        window.pause_game()
        assert window.paused
        assert not window.exclusive

        window.resume_game()
        assert not window.paused
        assert window.exclusive

    def test_draw_pause_menu(self, window):
        assert not pyglet.gl.glIsEnabled(pyglet.gl.GL_BLEND)
        assert not pyglet.gl.glIsEnabled(pyglet.gl.GL_DEPTH_TEST)

        self.mock_pause(window)
        window.draw_pause_menu()
        assert pyglet.gl.glIsEnabled(pyglet.gl.GL_BLEND)
        assert pyglet.gl.glIsEnabled(pyglet.gl.GL_DEPTH_TEST)

        self.mock_resume(window)

    def test_on_mouse_press(self, window):
        self.mock_pause(window)
        window.on_mouse_press(window.resume_label.x, window.resume_label.y, 1, 0)
        assert not window.paused

        self.mock_resume(window)

    def test_within_label(self, window):
        test_label = pyglet.text.Label(
            text="Test Label",
            font_name="Arial",
            font_size=18,
            width=100,
            height=50,
            x=window.width // 2,
            y=window.height // 2,
        )

        x = window.width // 2
        y = window.height // 2
        assert window.within_label(x, y, test_label)

        x = window.width + 1
        y = window.height + 1
        assert not window.within_label(x, y, test_label)

    def test_center_labels(self, window):
        RESIZE_WIDTH = RESIZE_HEIGHT = 100

        window.on_resize(RESIZE_WIDTH, RESIZE_HEIGHT)
        window.center_labels(RESIZE_WIDTH, RESIZE_HEIGHT)

        assert window.pause_label.x == window.resume_label.x == window.quit_label.x == RESIZE_WIDTH // 2
        assert window.pause_label.y == RESIZE_HEIGHT // 2
        assert window.resume_label.y == RESIZE_HEIGHT // 2 - 50
        assert window.quit_label.y == RESIZE_HEIGHT // 2 - 85

    def test_on_mouse_motion(self, window):
        self.mock_pause(window)
        assert window.resume_label.color == (255, 255, 255, 255)
        assert isinstance(window._mouse_cursor, type(window.get_system_mouse_cursor(window.CURSOR_DEFAULT)))

        window.on_mouse_motion(window.resume_label.x, window.resume_label.y, 1, 0)
        assert window.resume_label.color == (150, 150, 150, 255)
        assert isinstance(window._mouse_cursor, type(window.get_system_mouse_cursor(window.CURSOR_HAND)))
