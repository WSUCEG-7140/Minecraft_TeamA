import pytest
from tempus_fugit_minecraft.main import Model,Window
from tempus_fugit_minecraft.main import SAND, GRASS, BRICK, LIGHT_CLOUD, DARK_CLOUD


def test_light_clouds_created_dynamically():
    model = Model()
    model.generate_clouds(80, 100)
    count_clouds = sum(1 for block in model.world.values() if block == LIGHT_CLOUD)
    
    assert  count_clouds >= 1, "LIGHT_CLOUD was not identified"


def test_cloud_positions():
    model = Model()
    model.generate_clouds(80, 100)
    o = 80
    cloud_blocks = [coord for coord, block in model.world.items() if block == LIGHT_CLOUD]
    for block in cloud_blocks:
        assert -o <= block[0] <= o
        assert -o <= block[2] <= o


def test_cloud_height():
    model = Model()
    model.generate_clouds(80, 100)
    clouds = [coord for coord, block in model.world.items() if block == LIGHT_CLOUD]
    for cloud_coordinates in clouds:
        assert cloud_coordinates[1] >= 20


def test_non_overlapping_clouds():
    model = Model()
    model.generate_clouds(80, 100)
    blocks_of_all_clouds = [coordinates for coordinates , block in model.world.items() if block == LIGHT_CLOUD]
    unique_clouds = set(blocks_of_all_clouds)
    assert len(blocks_of_all_clouds) == len(unique_clouds)