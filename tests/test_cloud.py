import pyglet
import pytest
from unittest.mock import Mock
from tempus_fugit_minecraft.window import Window
from tempus_fugit_minecraft.model import Model
from tempus_fugit_minecraft.utilities import DARK_CLOUD, LIGHT_CLOUD, STONE, BRICK, GRASS, SAND


@pytest.fixture(scope="class")
def model():
    yield Model()


@pytest.fixture(scope="class")
def window():
    yield Window()


class TestClouds:
    @pytest.fixture(autouse=True)
    def teardown(self, model, window):
        model.world.clear()
        window.model = model

    def test_light_clouds_created_dynamically(self, model):
        clouds = model.generate_clouds_positions(80, 100)
        for cloud in clouds:
            for x, c, z in cloud:
                model.add_block((x, c, z), LIGHT_CLOUD, immediate=True)
        assert LIGHT_CLOUD in model.world.values()

    def test_cloud_positions(self):
        model = Model()
        model.generate_clouds_positions(80, 100)
        o = 80 + 2*6  # + 2*6 to ensure that the test will cover cloud block outside the world
        cloud_blocks = [coord for coord, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        for block in cloud_blocks:
            assert -o <= block[0] <= o
            assert -o <= block[2] <= o

    def test_cloud_height(self):
        model = Model()
        model.generate_clouds_positions(80, 100)
        clouds = [coord for coord, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        for cloud_coordinates in clouds:
            assert cloud_coordinates[1] >= 20

    def test_non_overlapping_clouds(self, model):
        model.generate_clouds_positions(80, 100)
        blocks_of_all_clouds = [coordinates for coordinates, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
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

    def test_pass_through_clouds(self, model, window):
        model.world[(0,50,0)] = LIGHT_CLOUD
        assert window.is_it_cloud_block((0,50,0)) == True

        model.world[(0,52,0)] = DARK_CLOUD
        assert window.is_it_cloud_block((0,52,0)) == True

    def test_no_pass_through_objects_not_of_type_clouds(self, model, window):
        model.world[(0,10,0)] = STONE
        assert window.is_it_cloud_block((0,10,0)) == False

        model.world[(0,20,0)] = BRICK
        assert window.is_it_cloud_block((0,20,0)) == False

        model.world[(0,30,0)] = GRASS
        assert window.is_it_cloud_block((0,30,0)) == False

        model.world[(0,40,0)] = SAND
        assert window.is_it_cloud_block((0,40,0)) == False

    def test__try_pass_through_different_objects_added_at_same_position(self, model, window):
        block_type = model.world.get((0,100,0))
        assert block_type == None

        model.world[(0,100,0)] = STONE
        assert window.is_it_cloud_block((0,100,0)) == False

        model.world[(0,100,0)] = LIGHT_CLOUD
        assert window.is_it_cloud_block((0,100,0)) == True

        model.world[(0,100,0)] = DARK_CLOUD
        assert window.is_it_cloud_block((0,100,0)) == True
