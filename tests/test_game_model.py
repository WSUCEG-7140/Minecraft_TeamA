import pyglet
import pytest
from unittest.mock import Mock
from unittest.mock import patch
from tempus_fugit_minecraft.game_model import GameModel
from tempus_fugit_minecraft.player import Player
from tempus_fugit_minecraft.block import Block
from tempus_fugit_minecraft.world import World


@pytest.fixture(scope="class")
def game_model():
    """!
    @brief Creates and initializes a model instance
    """
    pyglet.options['audio'] = ('silent')
    yield GameModel()


class TestGameModel:
    """!
    @brief A test class for the game model
    """
    @pytest.fixture(autouse=True)
    def teardown(self, game_model):
        """!
        @brief Resets an existing model instance
         """
        game_model.world.clear()
        game_model.sector = None
        game_model.player = Player()

    def test_pass_through_clouds(self, game_model):
        """!
        @see [issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """      
        game_model.world[(0,50,0)] = Block.LIGHT_CLOUD
        assert game_model.can_pass_through_block((0,50,0)) == True

        game_model.world[(0,52,0)] = Block.DARK_CLOUD
        assert game_model.can_pass_through_block((0,52,0)) == True

    def test_no_pass_through_objects_not_of_type_clouds(self, game_model):
        """!
        @see [issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        game_model.world[(0,10,0)] = Block.STONE
        assert game_model.can_pass_through_block((0,10,0)) == False

        game_model.world[(0,20,0)] = Block.BRICK
        assert game_model.can_pass_through_block((0,20,0)) == False

        game_model.world[(0,30,0)] = Block.GRASS
        assert game_model.can_pass_through_block((0,30,0)) == False

        game_model.world[(0,40,0)] = Block.SAND
        assert game_model.can_pass_through_block((0,40,0)) == False

    def test__try_pass_through_different_objects_added_at_same_position(self, game_model):
        """!
        @see [issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        block_type = game_model.world.get((0,100,0))
        assert block_type == None

        game_model.world[(0,100,0)] = Block.STONE
        assert game_model.can_pass_through_block((0,100,0)) == False

        game_model.world[(0,100,0)] = Block.LIGHT_CLOUD
        assert game_model.can_pass_through_block((0,100,0)) == True

        game_model.world[(0,100,0)] = Block.DARK_CLOUD
        assert game_model.can_pass_through_block((0,100,0)) == True

    def test_click_mouse_to_add_block_to_clouds(self, game_model):
        """!
        @see [issue#42](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/42)
        """
        clouds = World.generate_clouds(World.WIDTH_FROM_ORIGIN_IN_BLOCKS, 150)
        x, y, z = clouds[0][0][1]

        with patch.object(game_model, 'add_block', return_value=None) as add_block_method:
            game_model.handle_secondary_action()
            assert add_block_method.call_count == 0

    def test_handle_flight_toggle_while_player_not_flying(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.handle_flight_toggle()
        assert game_model.player.flying

    #issue 68
    def test_handle_flight_toggle_while_player_flying(self, game_model):
        game_model.player.flying = True
        game_model.handle_flight_toggle()
        assert not game_model.player.flying

    def test_handle_jump_while_player_not_airborne(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.player.vertical_velocity_in_blocks_per_second = 0
        game_model.handle_jump()
        assert game_model.player.vertical_velocity_in_blocks_per_second == game_model.player.jump_speed_in_blocks_per_second

    def test_handle_jump_while_player_airborne(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.player.vertical_velocity_in_blocks_per_second = 5
        game_model.handle_jump()
        assert game_model.player.vertical_velocity_in_blocks_per_second == 5

    def test_handle_walk_speed_change_increasing(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.handle_walk_speed_change(True)
        assert game_model.player.walking_speed_in_blocks_per_second == 2 * game_model.player.WALK_SPEED_IN_BLOCKS_PER_SECOND

    def test_handle_walk_speed_change_decreasing(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.player.walking_speed_in_blocks_per_second = 2 * game_model.player.WALK_SPEED_IN_BLOCKS_PER_SECOND
        game_model.handle_walk_speed_change(False)
        assert game_model.player.walking_speed_in_blocks_per_second == game_model.player.WALK_SPEED_IN_BLOCKS_PER_SECOND
   
    def test_handle_jump_change_increasing(self, game_model):
        """!
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        game_model.handle_jump_change(True)
        assert int(game_model.player.jump_speed_in_blocks_per_second) == int(game_model.player.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND) + 5

    
    def test_handle_jump_change_decreasing(self, game_model):
        """!
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        game_model.player.jump_speed_in_blocks_per_second = game_model.player.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND
        game_model.handle_jump_change(False)
        assert int(game_model.player.jump_speed_in_blocks_per_second) == int(game_model.player.MIN_JUMP_SPEED_IN_BLOCKS_PER_SECOND)

    def test_handle_secondary_action_no_previous_or_block(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        with patch.object(game_model, 'hit_test', return_value = (None, None)) as hit_test_method:
            with patch.object(game_model, 'add_block', return_value=None) as add_block_method:
                game_model.handle_secondary_action()
                assert add_block_method.call_count == 0

    def test_handle_secondary_action_with_block_and_cloud_no_add(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.world[(0, 0, 0)] = Block.LIGHT_CLOUD
        with patch.object(game_model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(game_model, 'add_block', return_value=None) as add_block_method:
                game_model.handle_secondary_action()
                assert add_block_method.call_count == 0

    #issue 68
    def test_handle_secondary_action_with_block_and_brick_one_add_block_call(self, game_model: GameModel):
        game_model.world[(0, 0, 0)] = Block.BRICK
        with patch.object(game_model, 'hit_test', return_value = ((0, 0, 0), (1, 1, 1))) as hit_test_method:
            with patch.object(game_model, 'add_block', return_value=None) as add_block_method:
                game_model.handle_secondary_action()
                assert add_block_method.call_count == 1

    def test_handle_primary_action_no_block_hit_no_block_removed(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        with patch.object(game_model, 'hit_test', return_value = (None, None)) as hit_test_method:
            with patch.object(game_model, 'remove_block', return_value=None) as remove_block_method:
                game_model.handle_primary_action()
                assert remove_block_method.call_count == 0

    def test_handle_primary_action_block_hit_is_stone_no_block_removed(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.world[(0, 0, 0)] = Block.STONE
        with patch.object(game_model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(game_model, 'remove_block', return_value=None) as remove_block_method:
                game_model.handle_primary_action()
                assert remove_block_method.call_count == 0

    def test_handle_primary_action_block_hit_is_brick_block_removed(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.world[(0, 0, 0)] = Block.BRICK
        with patch.object(game_model, 'hit_test', return_value = ((0, 0, 0), None)) as hit_test_method:
            with patch.object(game_model, 'remove_block', return_value=None) as remove_block_method:
                game_model.handle_primary_action()
                assert remove_block_method.call_count == 1

    def test_handle_change_active_block(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.handle_change_active_block(3)
        assert game_model.player.selected_block == game_model.player.inventory[3]

    def test_collide_not_coliding_result_should_be_input(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        result = game_model.collide((0, 0, 0), game_model.player.PLAYER_HEIGHT_IN_BLOCKS)
        assert result == (0, 0, 0)

    def test_collide_coliding_result_should_be_one_quarter(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.world[(1, 1, 0)] = Block.BRICK
        result = game_model.collide((0.49, 1, 0), game_model.player.PLAYER_HEIGHT_IN_BLOCKS)
        assert result == (0.25, 1, 0)

    def test_handle_movement(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        for forward in [1, 0, -1]:
            for backward in [1, 0, -1]:
                for left in [1, 0, -1]:
                    for right in [1, 0, -1]:
                        game_model.player.strafe_unit_vector = [0, 0]
                        game_model.handle_movement(forward, backward, left, right)
                        assert game_model.player.strafe_unit_vector[0] == backward - forward
                        assert game_model.player.strafe_unit_vector[1] == right - left

    def test_update_calls_player_update_eight_times(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.sector = (0, 0, 0)
        with patch.object(game_model.player, 'update', return_value = None) as player_update:
            game_model.update(1)
            assert player_update.call_count == 8

    def test_update_player_in_different_sector_changes_sectors(self, game_model: GameModel):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.update(1)
        assert game_model.sector is not None

    def test_handle_adjust_vision(self, game_model):
        """!
        @see [issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        game_model.handle_adjust_vision(1, 1)
        assert game_model.player.rotation_in_degrees == (0.15, 0.15)
