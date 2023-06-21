import pytest
from tempus_fugit_minecraft.main import Model
from tempus_fugit_minecraft.main import LIGHT_CLOUD


model = Model()


class TestClouds:
    def test_light_clouds_created_dynamically(self):
        model.generate_clouds(80, 100)
        count_clouds = sum(1 for block in model.world.values() if block == LIGHT_CLOUD)
        
        assert  count_clouds >= 1, "LIGHT_CLOUD was not identified"

    def test_cloud_positions(self):
        model.generate_clouds(80, 100)
        o = 80
        cloud_blocks = [coord for coord, block in model.world.items() if block == LIGHT_CLOUD]
        for block in cloud_blocks:
            assert -o <= block[0] <= o
            assert -o <= block[2] <= o

    def test_cloud_height(self):
        model.generate_clouds(80, 100)
        clouds = [coord for coord, block in model.world.items() if block == LIGHT_CLOUD]
        for cloud_coordinates in clouds:
            assert cloud_coordinates[1] >= 20

    def test_non_overlapping_clouds(self):
        model.generate_clouds(80, 100)
        blocks_of_all_clouds = [coordinates for coordinates , block in model.world.items() if block == LIGHT_CLOUD]
        unique_clouds = set(blocks_of_all_clouds)
        assert len(blocks_of_all_clouds) == len(unique_clouds)
