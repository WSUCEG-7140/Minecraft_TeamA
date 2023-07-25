import pyglet
import pytest
from unittest.mock import Mock
from unittest.mock import patch
from tempus_fugit_minecraft.model import Model
from tempus_fugit_minecraft.player import Player
from tempus_fugit_minecraft.block import Block
from tempus_fugit_minecraft.world import World


@pytest.fixture(scope="class")
def model():
    """!
    @brief Creates and initializes a model instance
    """
    pyglet.options['audio'] = ('silent')
    yield Model()


class TestModel:
    """!
    @brief A test class for the game model
    """
    @pytest.fixture(autouse=True)
    def teardown(self, model):
        """!
        @brief Resets an existing model instance
         """
        model.world.clear()
        model.sector = None
        model.player = Player()

    def test_pass_through_clouds(self, model):
        """!
        @see [issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """      
        model.world[(0,50,0)] = Block.LIGHT_CLOUD
        assert model.can_pass_through_block((0,50,0)) == True

        model.world[(0,52,0)] = Block.DARK_CLOUD
        assert model.can_pass_through_block((0,52,0)) == True

    def test_no_pass_through_objects_not_of_type_clouds(self, model):
        """!
        @see [issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        model.world[(0,10,0)] = Block.STONE
        assert model.can_pass_through_block((0,10,0)) == False

        model.world[(0,20,0)] = Block.BRICK
        assert model.can_pass_through_block((0,20,0)) == False

        model.world[(0,30,0)] = Block.GRASS
        assert model.can_pass_through_block((0,30,0)) == False

        model.world[(0,40,0)] = Block.SAND
        assert model.can_pass_through_block((0,40,0)) == False

    def test__try_pass_through_different_objects_added_at_same_position(self, model):
        """!
        @see [issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        block_type = model.world.get((0,100,0))
        assert block_type == None

        model.world[(0,100,0)] = Block.STONE
        assert model.can_pass_through_block((0,100,0)) == False

        model.world[(0,100,0)] = Block.LIGHT_CLOUD
        assert model.can_pass_through_block((0,100,0)) == True

        model.world[(0,100,0)] = Block.DARK_CLOUD
        assert model.can_pass_through_block((0,100,0)) == True

    def test_click_mouse_to_add_block_to_clouds(self, model):
        """!
        @see [issue#42](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/42)
        """
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS, 150)
        block, position = clouds[0][0]

        with patch.object(model, 'add_block', return_value=None) as add_block_method:
            model.handle_secondary_action()
            assert add_block_method.call_count == 0

    def test_handle_flight_toggle_while_player_not_flying(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.handle_flight_toggle()
        assert model.player.flying

    #issue 68
    def test_handle_flight_toggle_while_player_flying(self, model):
        model.player.flying = True
        model.handle_flight_toggle()
        assert not model.player.flying

    def test_handle_jump_while_player_not_airborne(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.player.vertical_velocity_in_blocks_per_second = 0
        model.handle_jump()
        assert model.player.vertical_velocity_in_blocks_per_second == model.player.jump_speed_in_blocks_per_second

    def test_handle_jump_while_player_airborne(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.player.vertical_velocity_in_blocks_per_second = 5
        model.handle_jump()
        assert model.player.vertical_velocity_in_blocks_per_second == 5

    def test_handle_walk_speed_change_increasing(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.handle_walk_speed_change(True)
        assert model.player.walking_speed_in_blocks_per_second == 2 * model.player.WALK_SPEED_IN_BLOCKS_PER_SECOND

    def test_handle_walk_speed_change_decreasing(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.player.walking_speed_in_blocks_per_second = 2 * model.player.WALK_SPEED_IN_BLOCKS_PER_SECOND
        model.handle_walk_speed_change(False)
        assert model.player.walking_speed_in_blocks_per_second == model.player.WALK_SPEED_IN_BLOCKS_PER_SECOND
   
    def test_handle_jump_change_increasing(self, model):
        """!
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        model.handle_jump_change(True)
        assert int(model.player.jump_speed_in_blocks_per_second) == int(model.player.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND) + 5

    
    def test_handle_jump_change_decreasing(self, model):
        """!
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        model.player.jump_speed_in_blocks_per_second = model.player.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND
        model.handle_jump_change(False)
        assert int(model.player.jump_speed_in_blocks_per_second) == int(model.player.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND)

    def test_handle_secondary_action_no_previous_or_block(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        with patch.object(model, 'hit_test', return_value = (None, None)) as hit_test_method:
            with patch.object(model, 'add_block', return_value=None) as add_block_method:
                model.handle_secondary_action()
                assert add_block_method.call_count == 0

    def test_handle_secondary_action_with_block_and_cloud_no_add(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.world[(0, 0, 0)] = Block.LIGHT_CLOUD
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(model, 'add_block', return_value=None) as add_block_method:
                model.handle_secondary_action()
                assert add_block_method.call_count == 0

    #issue 68
    def test_handle_secondary_action_with_block_and_brick_one_add_block_call(self, model: Model):
        model.world[(0, 0, 0)] = Block.BRICK
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), (1, 1, 1))) as hit_test_method:
            with patch.object(model, 'add_block', return_value=None) as add_block_method:
                model.handle_secondary_action()
                assert add_block_method.call_count == 1

    def test_handle_primary_action_no_block_hit_no_block_removed(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        with patch.object(model, 'hit_test', return_value = (None, None)) as hit_test_method:
            with patch.object(model, 'remove_block', return_value=None) as remove_block_method:
                model.handle_primary_action()
                assert remove_block_method.call_count == 0

    def test_handle_primary_action_block_hit_is_stone_no_block_removed(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.world[(0, 0, 0)] = Block.STONE
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(model, 'remove_block', return_value=None) as remove_block_method:
                model.handle_primary_action()
                assert remove_block_method.call_count == 0

    def test_handle_primary_action_block_hit_is_brick_block_removed(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.world[(0, 0, 0)] = Block.BRICK
        with patch.object(model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(model, 'remove_block', return_value=None) as remove_block_method:
                model.handle_primary_action()
                assert remove_block_method.call_count == 1

    def test_handle_change_active_block(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.handle_change_active_block(3)
        assert model.player.selected_block == model.player.inventory[3]

    def test_collide_not_coliding_result_should_be_input(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        result = model.collide((0, 0, 0), model.player.PLAYER_HEIGHT_IN_BLOCKS)
        assert result == (0, 0, 0)

    def test_collide_coliding_result_should_be_one_quarter(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.world[(1, 1, 0)] = Block.BRICK
        result = model.collide((0.49, 1, 0), model.player.PLAYER_HEIGHT_IN_BLOCKS)
        assert result == (0.25, 1, 0)

    def test_handle_movement(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        for forward in [1, 0, -1]:
            for backward in [1, 0, -1]:
                for left in [1, 0, -1]:
                    for right in [1, 0, -1]:
                        model.player.strafe_unit_vector = [0, 0]
                        model.handle_movement(forward, backward, left, right)
                        assert model.player.strafe_unit_vector[0] == backward - forward
                        assert model.player.strafe_unit_vector[1] == right - left

    def test_update_calls_player_update_eight_times(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.sector = (0, 0, 0)
        with patch.object(model.player, 'update', return_value = None) as player_update:
            model.update(1)
            assert player_update.call_count == 8

    def test_update_player_in_different_sector_changes_sectors(self, model: Model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.update(1)
        assert model.sector is not None

    def test_handle_adjust_vision(self, model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        model.handle_adjust_vision(1, 1)
        assert model.player.rotation_in_degrees == (0.15, 0.15)
