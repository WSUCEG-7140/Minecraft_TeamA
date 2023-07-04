from unittest.mock import Mock

import pyglet
import pytest

from tempus_fugit_minecraft.main import Window, Model, LIGHT_CLOUD, DARK_CLOUD


@pytest.fixture(scope="class")
def window():
    yield Window()


@pytest.fixture(scope="class")
def model():
    yield Model()

class TestSpeed:
    @pytest.fixture(autouse=True)
    def teardown(self, window):
        window.walking_speed = 5

    def test_speed_up(self, window):
        assert window.walking_speed == 5

        window.speed_up()
        assert window.walking_speed == 10

        window.speed_up()
        assert window.walking_speed == 15

        for _ in range(0, 9):
            window.speed_up()
        assert window.walking_speed == 20  # 20 is the maximum speed

    def test_speed_down(self, window):
            window = Window()
            window.speed_up()
            
            assert window.walking_speed == 10

            window.speed_down() 
            assert window.walking_speed == 5      
            
            for _ in range(0,9):
                window.speed_down()

            assert window.walking_speed > 0 # Player will NOT stop walking

    def test_up_key(self, window):
        assert window.walking_speed == 5

        window.on_key_press(pyglet.window.key.UP, Mock())
        assert window.walking_speed == 10

        window.on_key_press(pyglet.window.key.UP, Mock())
        assert window.walking_speed == 15

        for _ in range(0, 9):
            window.on_key_press(pyglet.window.key.UP, Mock())
        assert window.walking_speed == 20

    

class TestClouds:
    @pytest.fixture(autouse=True)
    def teardown(self, model):
        model.world.clear()

    def test_light_clouds_created_dynamically(self, model):
        clouds = model.generate_clouds_positions(80, 100)
        for cloud in clouds:
            for x, c, z in cloud:
                model.add_block((x, c, z), LIGHT_CLOUD, immediate=True)
        assert LIGHT_CLOUD in model.world.values()

    def test_cloud_positions(self, model):
        model.generate_clouds_positions(80, 100)
        o = 80 + 2*6  # + 2*6 to ensure that the test will cover cloud block outside the world
        cloud_blocks = [coord for coord, block in model.world.items() if block == LIGHT_CLOUD]
        for block in cloud_blocks:
            assert -o <= block[0] <= o
            assert -o <= block[2] <= o

    def test_cloud_height(self, model):
        model.generate_clouds_positions(80, 100)
        clouds = [coord for coord, block in model.world.items() if block == LIGHT_CLOUD]
        for cloud_coordinates in clouds:
            assert cloud_coordinates[1] >= 20

    def test_non_overlapping_clouds(self, model):
        model.generate_clouds_positions(80, 100)
        blocks_of_all_clouds = [coordinates for coordinates, block in model.world.items() if block == LIGHT_CLOUD]
        unique_clouds = set(blocks_of_all_clouds)
        assert len(blocks_of_all_clouds) == len(unique_clouds)

    def test_dark_clouds_created_dynamically(self, model):
        clouds = model.generate_clouds_positions(80, 200)
        for cloud in clouds:
            for x, c, z in cloud:
                model.add_block((x, c, z), DARK_CLOUD, immediate=True)
        assert DARK_CLOUD in model.world.values()

    def test_draw_clouds_in_the_sky_and_count_blocks(self):
        model = Model()
        clouds = model.generate_clouds_positions(80, 150)
        model.place_cloud_blocks(clouds)
        cloud_blocks = [coordinates for coordinates, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        assert len(cloud_blocks) >= sum(len(cloud) for cloud in clouds)


class TestPauseMenu:
    @pytest.fixture(autouse=True)
    def teardown(self, window):
        window.paused = False
        window.exclusive = True

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

    def test_on_mouse_press(self, window):
        self.mock_pause(window)
        window.on_mouse_press(window.resume_label.x, window.resume_label.y, 1, 0)
        assert not window.paused

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
        assert window.resume_label.y == RESIZE_HEIGHT // 2 - 45
        assert window.quit_label.y == RESIZE_HEIGHT // 2 - 90

    def test_on_mouse_motion(self, window):
        self.mock_pause(window)
        assert window.resume_label.color == (255, 255, 255, 255)
        assert isinstance(window._mouse_cursor, type(window.get_system_mouse_cursor(window.CURSOR_DEFAULT)))

        window.on_mouse_motion(window.resume_label.x, window.resume_label.y, 1, 0)
        assert window.resume_label.color == (150, 150, 150, 255)
        assert isinstance(window._mouse_cursor, type(window.get_system_mouse_cursor(window.CURSOR_HAND)))
