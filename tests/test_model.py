import pyglet
import pytest
from unittest.mock import Mock
from unittest.mock import patch
from tempus_fugit_minecraft.model import Model
from tempus_fugit_minecraft.player import Player
from tempus_fugit_minecraft.block import DARK_CLOUD, LIGHT_CLOUD, STONE, BRICK, GRASS, SAND, TREE_TRUNK, TREE_LEAVES
from tempus_fugit_minecraft.utilities import WORLD_SIZE, WHOLE_WORLD_SIZE
import random


@pytest.fixture(scope="class")
def model():
    pyglet.options['audio'] = ('silent')
    yield Model()


class TestModel:
    @pytest.fixture(autouse=True)
    def teardown(self, model):
        model.world.clear()
        model.sector = None
        model.player = Player()
        model.clouds = {}
        model.trees = {}

    #issue20
    def test_light_clouds_created_dynamically(self, model):
        clouds = model.generate_clouds_positions(WHOLE_WORLD_SIZE, 100)
        for cloud in clouds:
            for x, c, z in cloud:
                model.add_block((x, c, z), LIGHT_CLOUD, immediate=True)
        assert LIGHT_CLOUD in model.world.values()

    #issue20; #issue28
    def test_cloud_positions(self):
        model = Model()
        model.generate_clouds_positions(WHOLE_WORLD_SIZE, 100)
        clouds_limitations = WHOLE_WORLD_SIZE + 2*6  # + 2*6 to ensure that the test will cover cloud block outside the world
        cloud_blocks = [coord for coord, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        for block in cloud_blocks:
            assert -clouds_limitations <= block[0] <= clouds_limitations
            assert -clouds_limitations <= block[2] <= clouds_limitations

    #issue20; #issue28
    def test_cloud_height(self):
        model = Model()
        model.generate_clouds_positions(WHOLE_WORLD_SIZE, 100)
        clouds = [coord for coord, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        for cloud_coordinates in clouds:
            assert cloud_coordinates[1] >= 18

    #issue20; #issue28
    def test_non_overlapping_clouds(self, model):
        model.generate_clouds_positions(80, 100)
        blocks_of_all_clouds = [coordinates for coordinates, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        unique_clouds = set(blocks_of_all_clouds)
        assert len(blocks_of_all_clouds) == len(unique_clouds)

    #issue28
    def test_dark_clouds_created_dynamically(self, model):
        clouds = model.generate_clouds_positions(WHOLE_WORLD_SIZE, 200)
        for cloud in clouds:
            for x, c, z in cloud:
                model.add_block((x, c, z), DARK_CLOUD, immediate=True)
        assert DARK_CLOUD in model.world.values()

    #issue20; #issue28
    def test_draw_clouds_in_the_sky_and_count_blocks(self):
        model = Model()
        clouds = model.generate_clouds_positions(WHOLE_WORLD_SIZE, 150)
        model.place_cloud_blocks(clouds)
        cloud_blocks = [coordinates for coordinates, block in model.world.items() if block in [LIGHT_CLOUD, DARK_CLOUD]]
        assert len(cloud_blocks) >= sum(len(cloud) for cloud in clouds)

    #issue57
    def test_pass_through_clouds(self, model):
        model.world[(0,50,0)] = LIGHT_CLOUD
        assert model.can_pass_through_block((0,50,0)) == True

        model.world[(0,52,0)] = DARK_CLOUD
        assert model.can_pass_through_block((0,52,0)) == True

    #issue57
    def test_no_pass_through_objects_not_of_type_clouds(self, model):
        model.world[(0,10,0)] = STONE
        assert model.can_pass_through_block((0,10,0)) == False

        model.world[(0,20,0)] = BRICK
        assert model.can_pass_through_block((0,20,0)) == False

        model.world[(0,30,0)] = GRASS
        assert model.can_pass_through_block((0,30,0)) == False

        model.world[(0,40,0)] = SAND
        assert model.can_pass_through_block((0,40,0)) == False

    #issue57;
    def test__try_pass_through_different_objects_added_at_same_position(self, model):
        block_type = model.world.get((0,100,0))
        assert block_type == None

        model.world[(0,100,0)] = STONE
        assert model.can_pass_through_block((0,100,0)) == False

        model.world[(0,100,0)] = LIGHT_CLOUD
        assert model.can_pass_through_block((0,100,0)) == True

        model.world[(0,100,0)] = DARK_CLOUD
        assert model.can_pass_through_block((0,100,0)) == True

    #issue42
    def test_click_mouse_to_add_block_to_clouds(self, model):
        model.clouds = model.generate_clouds_positions(WHOLE_WORLD_SIZE, 150)
        x, y, z = model.clouds[0][0]

        with patch.object(model, 'add_block', return_value=None) as add_block_method:
            model.handle_secondary_action()
            assert add_block_method.call_count == 0

    #issue 68
    def test_handle_flight_toggle_while_player_not_flying(self, model):
        model.handle_flight_toggle()
        assert model.player.flying

    #issue 68
    def test_handle_flight_toggle_while_player_flying(self, model):
        model.player.flying = True
        model.handle_flight_toggle()
        assert not model.player.flying

    #issue 68
    def test_handle_jump_while_player_not_airborne(self, model):
        model.player.dy = 0
        model.handle_jump()
        assert model.player.dy == model.player.JUMP_SPEED

    #issue 68
    def test_handle_jump_while_player_airborne(self, model):
        model.player.dy = 5
        model.handle_jump()
        assert model.player.dy == 5

    #issue 68
    def test_handle_speed_change_increasing(self, model):
        model.handle_speed_change(True)
        assert model.player.walking_speed == 2 * model.player.WALK_SPEED_INCREMENT

    #issue 68
    def test_handle_speed_change_decreasing(self, model):
        model.player.walking_speed = 2 * model.player.WALK_SPEED_INCREMENT
        model.handle_speed_change(False)
        assert model.player.walking_speed == model.player.WALK_SPEED_INCREMENT

    #issue 68
    def test_handle_secondary_action_no_previous_or_block(self, model: Model):
        with patch.object(model, 'hit_test', return_value = (None, None)) as hit_test_method:
            with patch.object(model, 'add_block', return_value=None) as add_block_method:
                model.handle_secondary_action()
                assert add_block_method.call_count == 0

    #issue 68
    def test_handle_secondary_action_with_block_and_cloud_no_add(self, model: Model):
        model.world[(0, 0, 0)] = LIGHT_CLOUD
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(model, 'add_block', return_value=None) as add_block_method:
                model.handle_secondary_action()
                assert add_block_method.call_count == 0

    #issue 68
    def test_handle_secondary_action_with_block_and_brick_one_add_block_call(self, model: Model):
        model.world[(0, 0, 0)] = BRICK
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), (1, 1, 1))) as hit_test_method:
            with patch.object(model, 'add_block', return_value=None) as add_block_method:
                model.handle_secondary_action()
                assert add_block_method.call_count == 1

    #issue 68
    def test_handle_primary_action_no_block_hit_no_block_removed(self, model: Model):
        with patch.object(model, 'hit_test', return_value = (None, None)) as hit_test_method:
            with patch.object(model, 'remove_block', return_value=None) as remove_block_method:
                model.handle_primary_action()
                assert remove_block_method.call_count == 0

    #issue 68
    def test_handle_primary_action_block_hit_is_stone_no_block_removed(self, model: Model):
        model.world[(0, 0, 0)] = STONE
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(model, 'remove_block', return_value=None) as remove_block_method:
                model.handle_primary_action()
                assert remove_block_method.call_count == 0

    #issue 68
    def test_handle_primary_action_block_hit_is_brick_block_removed(self, model: Model):
        model.world[(0, 0, 0)] = BRICK
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(model, 'remove_block', return_value=None) as remove_block_method:
                model.handle_primary_action()
                assert remove_block_method.call_count == 1

    #issue 68
    def test_handle_change_active_block(self, model):
        model.handle_change_active_block(3)
        assert model.player.block == model.player.inventory[3]

    #issue 68
    def test_collide_not_coliding_result_should_be_input(self, model):
        result = model.collide((0, 0, 0), model.player.PLAYER_HEIGHT)
        assert result == (0, 0, 0)

    #issue 68
    def test_collide_coliding_result_should_be_one_quarter(self, model: Model):
        model.world[(1, 1, 0)] = BRICK
        result = model.collide((0.49, 1, 0), model.player.PLAYER_HEIGHT)
        assert result == (0.25, 1, 0)

    #issue 68
    def test_handle_movement(self, model):
        for forward in [1, 0, -1]:
            for backward in [1, 0, -1]:
                for left in [1, 0, -1]:
                    for right in [1, 0, -1]:
                        model.player.strafe = [0, 0]
                        model.handle_movement(forward, backward, left, right)
                        assert model.player.strafe[0] == backward - forward
                        assert model.player.strafe[1] == right - left

    #issue 68
    def test_update_calls_player_update_eight_times(self, model):
        model.sector = (0, 0, 0)
        with patch.object(model.player, 'update', return_value = None) as player_update:
            model.update(1)
            assert player_update.call_count == 8

    #issue 68
    def test_update_player_in_different_sector_changes_sectors(self, model: Model):
        model._initialize(immediate=True)
        model.update(1)
        assert model.sector is not None

    #issue 68
    def test_handle_adjust_vision(self, model):
        model.handle_adjust_vision(1, 1)
        assert model.player.rotation == (0.15, 0.15)

    #issue80
    def test_generate_single_tree_default_values(self, model):
        trunks , leaves = model.generate_single_tree(10,0,10)
        assert (10,0,10) in trunks
        assert len(trunks) == 4

        for trunk_position in range(4):
            assert model.world[(10,0+trunk_position,10)] == TREE_TRUNK

        # Check leaf blocks
        for dx in range(-2, 3):
            for dy in range(0,3):
                for dz in range(-2, 3):
                    assert model.world[(10 + dx, 0 + dy+4, 10 + dz)] == TREE_LEAVES

    #issue80
    def test_generate_single_tree_custom_values(self, model):
        x,y,z = 15,0,30
        trunk_height=7
        trunks , leaves = model.generate_single_tree(x,y,z, trunk_height=trunk_height)
        assert (x,y,z) in trunks
        assert len(trunks) == trunk_height
        
        # Check leaf blocks
        for dx in range(-2, 3):
            for dy in range(0,3):
                for dz in range(-2, 3):
                    assert model.world[(x + dx, y + dy+trunk_height, z + dz)] == TREE_LEAVES
    
    #issue80
    def test_generate_trees_default_values(self, model):
        model.world.clear()
        for x in range(-WORLD_SIZE,WORLD_SIZE):
            for z in range(-WORLD_SIZE,WORLD_SIZE):
                model.add_block((x, 0, z), random.choice([GRASS,SAND]), immediate=False)


        trees = model.generate_trees()
        assert 350 <= len(trees) <= 500
        
        for single_tree in trees:
            assert all(model.world[trunk_coord] == TREE_TRUNK for trunk_coord in single_tree[0])
            assert all(model.world[trunk_leaf]  == TREE_LEAVES for trunk_leaf in single_tree[1])


    # #issue80
    def test_generate_trees_custom_values(self, model):
        for x in range(-WORLD_SIZE,WORLD_SIZE):
            for z in range(-WORLD_SIZE,WORLD_SIZE):
                model.add_block((x, 0, z), random.choice([GRASS,SAND]), immediate=False)

        trees = model.generate_trees(250)
        assert len(trees) == 250

        for single_tree in trees:
            assert all(model.world[trunk_coord] == TREE_TRUNK for trunk_coord in single_tree[0])
            assert all(model.world[trunk_leaf]  == TREE_LEAVES for trunk_leaf in single_tree[1])

    # #issue80
    def test_check_tree_built_on_grass_or_sand(self, model):
        for x in range(-WORLD_SIZE,WORLD_SIZE):
            for z in range(-WORLD_SIZE,WORLD_SIZE):
                model.add_block((x, 0, z), random.choice([GRASS,SAND]), immediate=False)

        trees = model.generate_trees()

        for single_tree in trees:
            base_trunk_x , base_trunk_y , base_trunk_z = single_tree[0][0]
            assert model.world[(base_trunk_x , base_trunk_y , base_trunk_z)] == TREE_TRUNK
            assert model.world[(base_trunk_x , base_trunk_y-1 , base_trunk_z)] in [GRASS , SAND]

    # #issue80
    def test_tree_built_on_top_of_ground_level_grass_or_sand(self, model):
        for x in range(-WORLD_SIZE,WORLD_SIZE):
            for z in range(-WORLD_SIZE,WORLD_SIZE):
                model.add_block((x, 0, z), random.choice([GRASS,SAND]), immediate=False)

        trees = model.generate_trees(50)
        for single_tree in trees:
            trunks , leaves = single_tree
            assert model.world[(trunks[0][0],trunks[0][1]-1,trunks[0][2])] in [GRASS,SAND]
