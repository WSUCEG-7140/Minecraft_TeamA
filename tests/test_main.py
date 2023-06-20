from unittest.mock import Mock

import pyglet

from tempus_fugit_minecraft.main import Window


window = Window()


class TestPauseMenu:
    def mock_pause(self):
        if not window.paused:
            window.on_key_press(pyglet.window.key.ESCAPE, Mock())

    def mock_resume(self):
        if window.paused:
            window.on_key_press(pyglet.window.key.ESCAPE, Mock())

    def test_on_key_press(self):
        self.mock_pause()
        assert window.paused

        self.mock_resume()
        assert not window.paused

    def test_update(self):
        self.mock_pause()
        before = window.model.process_queue()
        window.update(0)
        after = window.model.process_queue()

        assert before == after

    def test_on_resize(self):
        RESIZE_WIDTH = RESIZE_HEIGHT = 100

        self.mock_pause()
        window.on_resize(RESIZE_WIDTH, RESIZE_HEIGHT)
        assert window.pause_label.x == RESIZE_WIDTH // 2
        assert window.pause_label.y == RESIZE_HEIGHT // 2

        self.mock_resume()

    def test_pause_and_resume_game(self):
        window.pause_game()
        assert window.paused
        assert window.exclusive is False

        window.resume_game()
        assert not window.paused
        assert window.exclusive is True

    def test_draw_pause_menu(self):
        assert pyglet.gl.glIsEnabled(pyglet.gl.GL_BLEND) != pyglet.gl.GL_TRUE
        assert pyglet.gl.glIsEnabled(pyglet.gl.GL_DEPTH_TEST) != pyglet.gl.GL_TRUE

        self.mock_pause()
        window.draw_pause_menu()
        assert pyglet.gl.glIsEnabled(pyglet.gl.GL_BLEND) == pyglet.gl.GL_TRUE
        assert pyglet.gl.glIsEnabled(pyglet.gl.GL_DEPTH_TEST) == pyglet.gl.GL_TRUE

        self.mock_resume()

    def test_on_mouse_press(self):
        self.mock_pause()
        window.on_mouse_press(window.resume_label.x, window.resume_label.y, 1, 0)
        assert window.paused is False

        self.mock_resume()

    def test_within_label(self):
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
        assert window.within_label(x, y, test_label) is True

        x = window.width + 1
        y = window.height + 1
        assert window.within_label(x, y, test_label) is False

    def test_center_labels(self):
        RESIZE_WIDTH = RESIZE_HEIGHT = 100

        window.on_resize(RESIZE_WIDTH, RESIZE_HEIGHT)
        window.center_labels(RESIZE_WIDTH, RESIZE_HEIGHT)

        assert window.pause_label.x == window.resume_label.x == window.quit_label.x == RESIZE_WIDTH // 2
        assert window.pause_label.y == RESIZE_HEIGHT // 2
        assert window.resume_label.y == RESIZE_HEIGHT // 2 - 50
        assert window.quit_label.y == RESIZE_HEIGHT // 2 - 85
