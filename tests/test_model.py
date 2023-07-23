import pyglet
import pytest
from unittest.mock import Mock
from unittest.mock import patch
from tempus_fugit_minecraft.model import Model
from tempus_fugit_minecraft.player import Player
from tempus_fugit_minecraft.world import World
from tempus_fugit_minecraft.block import DARK_CLOUD, LIGHT_CLOUD, STONE, BRICK, GRASS, SAND, TREE_TRUNK, TREE_LEAVES
from tempus_fugit_minecraft.utilities import WORLD_SIZE
import random


@pytest.fixture(scope="class")
def model():
    pyglet.options['audio'] = ('silent')
    yield Model()


class TestModel:
    @pytest.fixture(autouse=True)
    def teardown(self, model):
        model.player = Player()
        model.world.clear()        

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
        clouds = World.generate_clouds(WORLD_SIZE, 150)
        block, position = clouds[0][0]

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
        assert model.player.dy == model.player.jump_speed

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
   
    def test_handle_jump_change_increasing(self, model):
        """!
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        model.handle_jump_change(True)
        assert int(model.player.jump_speed) == int(model.player.MIN_JUMP_SPEED) + 5

    
    def test_handle_jump_change_decreasing(self, model):
        """!
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        model.player.jump_speed = model.player.MIN_JUMP_SPEED
        model.handle_jump_change(False)
        assert int(model.player.jump_speed) == int(model.player.MIN_JUMP_SPEED)

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
        model.update(1)
        assert model.sector is not None

    #issue 68
    def test_handle_adjust_vision(self, model):
        model.handle_adjust_vision(1, 1)
        assert model.player.rotation == (0.15, 0.15)
