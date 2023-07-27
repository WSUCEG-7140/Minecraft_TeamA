import random

import pytest

from tempus_fugit_minecraft.block import Block
from tempus_fugit_minecraft.game_model import GameModel
from tempus_fugit_minecraft.world import World


@pytest.fixture(scope='class')
def game_model():
    game_model = GameModel()
    game_model.world.clear()
    yield game_model

class TestWorld:
    @pytest.fixture(autouse=True)
    def teardown(self, game_model):
        game_model.world.clear()

    #issue20; #issue28
    def test_cloud_height(self):
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS, 100)
        for cloud in clouds:
            for _, (_, y, _) in cloud:
                assert y >= 18

    #issue20; #issue28
    def test_non_overlapping_clouds(self, game_model: GameModel):
        clouds = World.generate_clouds(80, 100)
        assert len(clouds) == 100

        for cloud in clouds:
            for block, position in cloud:
                game_model.add_block(position, block, immediate=False)

        positions_of_all_cloud_blocks = [ position for position in game_model.world ]
        unique_clouds_positions = set(positions_of_all_cloud_blocks)
        assert len(positions_of_all_cloud_blocks) == len(unique_clouds_positions)

    #issue20, issue28
    def test_clouds_created_dynamically(self):
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS, 100)
        unique_cloud_types = set([ block for cloud in clouds for block, _ in cloud ])
        assert Block.LIGHT_CLOUD in unique_cloud_types
        assert Block.DARK_CLOUD in unique_cloud_types

    #issue20; #issue28
    def test_cloud_positions(self):
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS, 100)
        clouds_limitations = World.WIDTH_FROM_ORIGIN_IN_BLOCKS + 2 * 6  # + 2*6 to ensure that the test will cover cloud block outside the world
        cloud_blocks = [ position for cloud in clouds for _, position in cloud ]
        for x, _, z in cloud_blocks:
            assert -clouds_limitations <= x <= clouds_limitations
            assert -clouds_limitations <= z <= clouds_limitations

    #issue20; #issue28
    def test_draw_clouds_in_the_sky_and_count_blocks(self, game_model):
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS, 150)
        for cloud in clouds:
            for block, position in cloud:
                game_model.add_block(position, block, immediate=False)

        cloud_blocks = [ coordinates for coordinates in game_model.world ]
        assert len(cloud_blocks) <= sum(len(cloud) for cloud in clouds)

    #issue44; #issue84
    def test_generate_clouds_in_one_of_different_layers_in_the_sky(self):
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS)
        for cloud in clouds:
            _, (_, y, _) = cloud[0]
            assert y in [18, 20, 22, 24, 26]

    #issue44; #issue84
    def test_generate_clouds_appear_in_different_layers_of_sky(self):
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS)
        cloud_layers = set([ y for cloud in clouds for _, (_, y, _) in cloud ])
        assert cloud_layers == { 18, 20, 22, 24, 26 } 

    #issue80
    def test_generate_single_tree_default_values(self):
        tree = World.generate_single_tree(10,0,10)
        trunk = [ (block, position) for block, position in tree if block == Block.TREE_TRUNK ]
        leaves = [ (block, position) for block, position in tree if block == Block.TREE_LEAVES ]
        assert (Block.TREE_TRUNK, (10,0,10)) in trunk
        assert len(trunk) == 4

        assert len(leaves) == len(tree) - len(trunk)

    #issue80
    def test_generate_single_tree_custom_values(self):
        x,y,z = 15,0,30
        trunk_height = 7
        tree = World.generate_single_tree(x,y,z, trunk_height=trunk_height)

        trunk = [ (block, position) for block, position in tree if block == Block.TREE_TRUNK ]
        leaves = [ (block, position) for block, position in tree if block == Block.TREE_LEAVES ]

        assert (Block.TREE_TRUNK, (x,y,z)) in trunk
        assert len(trunk) == trunk_height        
        assert len(leaves) == len(tree) - trunk_height

    #issue84
    def test_generate_single_cloud_blocks_at_a_specific_height(self):
        y = 100
        cloud = World.generate_single_cloud(cloud_center_x=0,cloud_center_y=y,cloud_center_z=0,s=3)
        for _, (_, block_y, _) in cloud:
            assert block_y == y

    def test_generate_cloud_returns_list_of_tuples(self):
        x,y,z = 4,5,3
        cloud = World.generate_single_cloud(x, y, z, s=3)
        assert isinstance(cloud,list)
        for block, position in cloud:
            assert isinstance(block, Block)
            assert isinstance(position, tuple) and len(position) == 3

    #issue80
    def test_generate_trees_default_values(self, game_model):
        self.__generate_test_terrain(game_model)

        trees = World.generate_trees(game_model)
        assert 350 <= len(trees) <= 500
        
        for tree in trees:
            for block, position in tree:
                game_model.add_block(position, block, immediate=False)

        for tree in trees:
            block, (x, y, z) = tree[0]
            assert block == Block.TREE_TRUNK

            grass_pos = (x, y - 1, z)
            assert game_model.world[grass_pos] in [Block.GRASS, Block.SAND]

            trunks = [ position for block, position in tree if block == Block.TREE_TRUNK ]
            leaves = [ position for block, position in tree if block == Block.TREE_LEAVES ]

            assert all([ game_model.world[position] == Block.TREE_TRUNK for position in trunks ])
            assert all([ game_model.world[position] == Block.TREE_LEAVES for position in leaves ])

    # issue80
    def test_generate_trees_custom_values(self, game_model):
        self.__generate_test_terrain(game_model)

        trees = World.generate_trees(game_model, 250)
        assert len(trees) == 250

        for tree in trees:
            for block, position in tree:
                game_model.add_block(position, block, immediate=False)

        for tree in trees:
            block, (x, y, z) = tree[0]
            assert block == Block.TREE_TRUNK

            grass_pos = (x, y - 1, z)
            assert game_model.world[grass_pos] in [Block.GRASS, Block.SAND]

            trunks = [ position for block, position in tree if block == Block.TREE_TRUNK ]
            leaves = [ position for block, position in tree if block == Block.TREE_LEAVES ]

            assert all([ game_model.world[position] == Block.TREE_TRUNK for position in trunks ])
            assert all([ game_model.world[position] == Block.TREE_LEAVES for position in leaves ])

    # issue80
    def test_check_tree_built_on_grass_or_sand(self, game_model):
        self.__generate_test_terrain(game_model)

        trees = World.generate_trees(game_model, 50)
        assert len(trees) == 50

        for tree in trees:
            block, (x, y, z) = tree[0]  
            assert block == Block.TREE_TRUNK

            grass_pos = (x, y - 1, z)
            assert game_model.world[grass_pos] in [Block.GRASS, Block.SAND]

    # issue80
    def test_tree_built_on_top_of_ground_level_grass_or_sand(self, game_model):
        self.__generate_test_terrain(game_model)

        trees = World.generate_trees(game_model, 50)
        for single_tree in trees:
            _, (x, y, z) = single_tree[0]
            assert game_model.world[(x, y - 1, z)] in [Block.GRASS,Block.SAND]

    def test_generate_hill_blocks_are_either_grass_sand_brick(self):
        hill = World.generate_hill(0, 0)
        block_types = set([ block for block, _ in hill ])
        assert len(block_types) == 1
        assert list(block_types)[0] in [Block.GRASS, Block.BRICK, Block.SAND]

    def test_generate_hill_blocks_y_position_between_minus_one_and_five(self):
        hill = World.generate_hill(0, 0)
        for _, (_, y, _) in hill:
            assert -1 <= y <= 5

    def test_generate_hill_blocks_x_and_z_positions_are_between_minus_eight_and_eight(self):
        hill = World.generate_hill(0, 0)
        for _, (x, _, z) in hill:
            assert -8 <= x <= 8
            assert -8 <= z <= 8

    def test_generate_hill_at_least_a_block_at_y_equals_minus_one(self):
        hill = World.generate_hill (0, 0)
        _, (_, y, _) = hill[0] 
        assert y == -1

    def test_generate_hills_with_default_params_get_one_half_x_world_width_from_origin_hills(self):
        numberOfHills = int(1.5 * World.WIDTH_FROM_ORIGIN_IN_BLOCKS)
        hills = World.generate_hills()
        assert len(hills) == numberOfHills

    def test_generate_hills_with_one_hill_get_one_hill(self):
        numberOfHills = 1
        hills = World.generate_hills(num_hills=1)
        assert len(hills) == numberOfHills

    def test_generate_hills_with_default_params_all_hills_between_minus_world_width_from_origin_and_world_width_from_origin(self):
        hills = World.generate_hills()
        for hill in hills:
            for _, (x, _, z) in hill:
                assert -World.WIDTH_FROM_ORIGIN_IN_BLOCKS <= x <= World.WIDTH_FROM_ORIGIN_IN_BLOCKS
                assert -World.WIDTH_FROM_ORIGIN_IN_BLOCKS <= z <= World.WIDTH_FROM_ORIGIN_IN_BLOCKS

    def test_generate_hills_with_custom_world_width_from_origin_all_hills_between_minus_specified_and_positive_specified(self):
        hills = World.generate_hills(world_size=50)
        for hill in hills:
            for _, (x, _, z) in hill:
                assert -50 <= x <= 50
                assert -50 <= z <= 50

    def test_generate_base_layer(self):
        base_layer = World.generate_base_layer()
        grass = [position for block, position in base_layer if block == Block.GRASS]
        assert len(grass) == (1 + 2 * World.WIDTH_FROM_ORIGIN_IN_BLOCKS) ** 2
        stone = [position for block, position in base_layer if block == Block.STONE]
        assert len(stone) > (1 + 2 * World.WIDTH_FROM_ORIGIN_IN_BLOCKS) ** 2
        for (_, y, _) in grass:
            assert y == -2
        for (_, y, _) in stone:
            assert -3 <= y <= 3

    # issue86
    def __generate_test_terrain(self, game_model:GameModel):
        for x in range(-World.WIDTH_FROM_ORIGIN_IN_BLOCKS, World.WIDTH_FROM_ORIGIN_IN_BLOCKS):
            for z in range(-World.WIDTH_FROM_ORIGIN_IN_BLOCKS, World.WIDTH_FROM_ORIGIN_IN_BLOCKS):
                game_model.add_block((x, 0, z), random.choice([Block.GRASS,Block.SAND]), immediate=False)