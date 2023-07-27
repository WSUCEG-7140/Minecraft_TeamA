import pytest
import math
from tempus_fugit_minecraft.player import Player
from tempus_fugit_minecraft.world import World
from tempus_fugit_minecraft.block import BRICK, GRASS, SAND, LIGHT_CLOUD, DARK_CLOUD, TREE_TRUNK, TREE_LEAVES


@pytest.fixture(scope = "class")
def player():
    yield Player()


class TestPlayer:
    @pytest.fixture(autouse=True)
    def teardown(self, player):
        player.rotation = (0, 0)
        player.flying = False
        player.strafe = [0, 0]
        player.walking_speed = 5
        player.dy = 0

    def test_new_player_construction(self, player):
        assert player.flying == False
        assert len(player.strafe) == 2
        assert player.strafe[0] == 0
        assert player.strafe[1] == 0
        assert player.position == (0, 0, 0)
        assert player.rotation == (0, 0)
        assert player.dy == 0
        assert len(player.inventory) == 5
        assert BRICK in player.inventory
        assert GRASS in player.inventory
        assert SAND in player.inventory
        assert TREE_TRUNK in player.inventory
        assert TREE_LEAVES in player.inventory
        assert BRICK == player.block
        assert player.walking_speed == 5

    def test_get_sight_vector_no_rotation(self, player):
        player.rotation = (0, 0)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, -1)

    def test_get_sight_vector_backwards(self, player):
        player.rotation = (180, 0)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, 1)

    def test_get_sight_vector_full_rotation(self, player):
        player.rotation = (360, 0)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, -1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, -1)

    def test_get_sight_vector_facing_right(self, player):
        player.rotation = (90, 0)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1)
        assert dy == 0
        assert math.isclose(dz, 1e-15, abs_tol=1e-15)

    def test_get_sight_vector_facing_left(self, player):
        player.rotation = (270, 0)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, -1)
        assert dy == 0
        assert math.isclose(dz, 1e-15, abs_tol=1e-15)

    def test_get_sight_vector_facing_up(self, player):
        player.rotation = (0, 90)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, -1e-15, abs_tol=1e-15)
        assert dy == 1
        assert math.isclose(dz, -1e-15, abs_tol=1e-15)

    def test_get_sight_vector_facing_down(self, player):
        player.rotation = (0, -90)
        result = player.get_sight_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, -1e-15, abs_tol=1e-15)
        assert dy == -1
        assert math.isclose(dz, -1e-15, abs_tol=1e-15)

    def test_get_movement_vector_forward_movement(self, player):
        player.flying = False
        player.strafe = [-1, 0]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, -1)

    def test_get_movement_vector_backwward_movement(self, player):
        player.flying = False
        player.strafe = [1, 0]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, 1)

    def test_get_movement_vector_right_movement(self, player):
        player.flying = False
        player.strafe = [0, 1]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1)
        assert dy == 0
        assert math.isclose(dz, 1e-15, abs_tol=1e-15)

    def test_get_movement_vector_left_movement(self, player):
        player.flying = False
        player.strafe = [0, -1]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, -1)
        assert dy == 0
        assert math.isclose(dz, 1e-15, abs_tol=1e-15)

    def test_get_movement_vector_forward_movement_with_flight(self, player):
        player.flying = True
        player.strafe = [-1, 0]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, -1)

    def test_get_movement_vector_backwward_movement_with_flight(self, player):
        player.flying = True
        player.strafe = [1, 0]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1e-15, abs_tol=1e-15)
        assert dy == 0
        assert math.isclose(dz, 1)

    def test_get_movement_vector_right_movement_with_flight(self, player):
        player.flying = True
        player.strafe = [0, 1]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, 1)
        assert dy == 0
        assert math.isclose(dz, 1e-15, abs_tol=1e-15)

    def test_get_movement_vector_left_movement_with_flight(self, player):
        player.flying = True
        player.strafe = [0, -1]
        result = player.get_motion_vector()
        assert len(result) == 3
        dx, dy, dz = result
        assert math.isclose(dx, -1)
        assert dy == 0
        assert math.isclose(dz, 1e-15, abs_tol=1e-15)

    def test_increase_speed_no_call_should_be_default_speed(self, player):
        assert player.walking_speed == player.WALK_SPEED_INCREMENT

    def test_increase_speed_called_one_time_should_be_double_initial_speed(self, player):
        player.increase_speed()
        assert player.walking_speed == 2 * player.WALK_SPEED_INCREMENT

    def test_increase_speed_called_two_times_should_be_triple_initial_speed(self, player):
        player.increase_speed()
        player.increase_speed()
        assert player.walking_speed == 3 * player.WALK_SPEED_INCREMENT

    def test_increase_speed_called_three_times_should_be_quadruple_initial_speed(self, player):
        player.increase_speed()
        player.increase_speed()
        player.increase_speed()
        assert player.walking_speed == 4 * player.WALK_SPEED_INCREMENT

    def test_increase_speed_called_four_times_should_be_maxed_at_twenty(self, player):
        player.increase_speed()
        player.increase_speed()
        player.increase_speed()
        player.increase_speed()
        assert player.walking_speed == 4 * player.WALK_SPEED_INCREMENT

    def test_decrease_speed_called_one_time_should_be_triple_initial_speed(self, player):
        player.walking_speed = 4 * player.WALK_SPEED_INCREMENT
        player.decrease_speed()
        assert player.walking_speed == 3 * player.WALK_SPEED_INCREMENT

    def test_decrease_speed_called_two_times_should_be_double_initial_speed(self, player):
        player.walking_speed = 4 * player.WALK_SPEED_INCREMENT
        player.decrease_speed()
        player.decrease_speed()
        assert player.walking_speed == 2 * player.WALK_SPEED_INCREMENT

    def test_decrease_speed_called_three_times_should_be_initial_speed(self, player):
        player.walking_speed = 4 * player.WALK_SPEED_INCREMENT
        player.decrease_speed()
        player.decrease_speed()
        player.decrease_speed()
        assert player.walking_speed == 1 * player.WALK_SPEED_INCREMENT

    def test_decrease_speed_called_four_times_should_be_initial_speed(self, player):
        player.walking_speed = 4 * player.WALK_SPEED_INCREMENT
        player.decrease_speed()
        player.decrease_speed()
        player.decrease_speed()
        player.decrease_speed()
        assert player.walking_speed == 1 * player.WALK_SPEED_INCREMENT

    def test_jump_no_vertical_velocity(self, player):
        player.jump()
        assert player.dy == player.jump_speed

    def test_jump_with_vertical_velocity(self, player):
        player.dy = 5
        player.jump()
        assert player.dy == 5

    def test_move_forward(self, player):
        player.move_forward()
        assert player.strafe[0] == -1

    def test_move_backward(self, player):
        player.move_backward()
        assert player.strafe[0] == 1

    def test_move_left(self, player):
        player.move_left()
        assert player.strafe[1] == -1

    def test_move_right(self, player):
        player.move_right()
        assert player.strafe[1] == 1

    def test_select_active_item_index_zero_first_item(self, player):
        player.select_active_item(0)
        assert player.block == player.inventory[0]

    def test_select_active_item_index_one_greater_than_inventory_length(self, player):
        player.select_active_item(len(player.inventory) + 1)
        assert player.block == player.inventory[1]

    def test_select_active_item_negative_index(self, player):
        player.select_active_item(-1)
        assert player.block == player.inventory[(len(player.inventory) - 1)]

    def test_stop_forward(self, player):
        player.strafe[0] = -1
        player.stop_forward()
        assert player.strafe[0] == 0

    def test_stop_backward(self, player):
        player.strafe[0] = 1
        player.stop_backward()
        assert player.strafe[0] == 0

    def test_stop_left(self, player):
        player.strafe[1] = -1
        player.stop_left()
        assert player.strafe[1] == 0

    def test_stop_right(self, player):
        player.strafe[1] = 1
        player.stop_right()
        assert player.strafe[1] == 0

    def test_adjust_sight_by_one_in_x_dir(self, player):
        player.adjust_sight(1, 0)
        x, _ = player.rotation
        assert x == 0.15

    def test_adjust_sight_by_one_in_y_dir(self, player):
        player.adjust_sight(0, 1)
        _, y = player.rotation
        assert y == 0.15

    def test_adjust_sight_y_clamping_to_positive_90(self, player):
        player.adjust_sight(0, 700)
        _, y = player.rotation
        assert y == 90

    def test_adjust_sight_y_clamping_to_negative_90(self, player):
        player.adjust_sight(0, -700)
        _, y = player.rotation
        assert y == -90

    def test_current_speed_flying(self, player):
        player.flying = True
        assert player.current_speed() == player.FLYING_SPEED

    def test_current_speed_walking(self, player):
        player.flying = False
        player.walking_speed = 10
        assert player.current_speed() == 10

    def test_toggle_flight_on(self, player):
        player.toggle_flight()
        assert player.flying

    def test_toggle_flight_off(self, player):
        player.toggle_flight()
        player.toggle_flight()
        assert not player.flying

    def test_update_with_no_flying(self, player: Player):
        for x in [-1, 0, 1]:
            for z in [-1, 0, 1]:
                player.position = (0, 0, 0)
                player.rotation = (0, 0)
                player.dy = 0
                player.strafe = [x, z]

                player.update(1, lambda pos, _: pos)

                p_x, p_y, p_z = player.position
                m_x, _, m_z = player.get_motion_vector()

                assert p_x == m_x * player.current_speed()
                assert p_z == m_z * player.current_speed()

                assert p_y == -player.GRAVITY
                assert player.dy == -player.GRAVITY

    def test_update_with_flying(self, player: Player):
        player.flying = True
        for x in [-1, 0, 1]:
            for y in [-90, -45, 0, 45, 90]:
                for z in [-1, 0, 1]:
                    player.position = (0, 0, 0)
                    player.rotation = (0,y)
                    player.dy = 0
                    player.strafe = [x, z]
                    player.update(1, lambda pos, _: pos)
                    p_x, p_y, p_z = player.position
                    m_x, m_y, m_z = player.get_motion_vector()
                    assert p_x == m_x * player.current_speed()
                    assert p_y == m_y * player.current_speed()
                    assert p_z == m_z * player.current_speed()

    def test_player_within_world_boundaries(self, player: Player):
        player.position = (10,5,15)
        player.check_player_within_world_boundaries()
        assert player.position == (10,5,15)

    def test_check_player_at_boundaries(self, player: Player):
        player.position = (World.WIDTH_FROM_ORIGIN_IN_BLOCKS , 20, World.WIDTH_FROM_ORIGIN_IN_BLOCKS)
        player.check_player_within_world_boundaries()
        assert player.position == (World.WIDTH_FROM_ORIGIN_IN_BLOCKS , 20, World.WIDTH_FROM_ORIGIN_IN_BLOCKS)

    def test_player_out_of_world_boundaries(self, player: Player):
        player.position = ((-World.WIDTH_FROM_ORIGIN_IN_BLOCKS-100) , 25 , (World.WIDTH_FROM_ORIGIN_IN_BLOCKS+120))
        player.check_player_within_world_boundaries()
        assert player.position == (-World.WIDTH_FROM_ORIGIN_IN_BLOCKS , 25 , World.WIDTH_FROM_ORIGIN_IN_BLOCKS)

        player.position = ((World.WIDTH_FROM_ORIGIN_IN_BLOCKS+25) , 25 , (-World.WIDTH_FROM_ORIGIN_IN_BLOCKS-5))
        player.check_player_within_world_boundaries()
        assert player.position == (World.WIDTH_FROM_ORIGIN_IN_BLOCKS , 25 , -World.WIDTH_FROM_ORIGIN_IN_BLOCKS)

    def test_player_out_of_world_in_x_coordinate(self, player: Player):
        player.position = ((World.WIDTH_FROM_ORIGIN_IN_BLOCKS+2) , 125 , 15)
        player.check_player_within_world_boundaries()
        assert player.position == (World.WIDTH_FROM_ORIGIN_IN_BLOCKS , 125 , 15)

        player.position = ((-World.WIDTH_FROM_ORIGIN_IN_BLOCKS-200) , 125 , 15)
        player.check_player_within_world_boundaries()
        assert player.position == (-World.WIDTH_FROM_ORIGIN_IN_BLOCKS , 125 , 15)

    def test_player_out_of_world_in_z_coordinate(self, player: Player):
        player.position = (79 , 125 , (World.WIDTH_FROM_ORIGIN_IN_BLOCKS+2))
        player.check_player_within_world_boundaries()
        assert player.position == (79 , 125 , World.WIDTH_FROM_ORIGIN_IN_BLOCKS)

        player.position = (79 , 125 , (-World.WIDTH_FROM_ORIGIN_IN_BLOCKS-120))
        player.check_player_within_world_boundaries()
        assert player.position == (79 , 125 , -World.WIDTH_FROM_ORIGIN_IN_BLOCKS)

    def test_player_in_y_coordinate(self, player: Player):
        player.position = (79 , (World.WIDTH_FROM_ORIGIN_IN_BLOCKS+1000) , 0)
        player.check_player_within_world_boundaries()
        assert player.position == (79 , (World.WIDTH_FROM_ORIGIN_IN_BLOCKS+1000) , 0)

    #issue97
    def test_slow_walk(self, player):
        assert player.walking_speed == 5
        player.slow_walking_speed()
        assert player.walking_speed == 5/3

    #issue98
    def test_sprint(self, player):
        assert player.walking_speed == 5
        player.start_sprinting()
        assert player.walking_speed == 10

    #issue97; #issue98
    def test_reset_walk_speed(self, player):
        player.walking_speed = 10
        player.reset_walking_speed()
        assert player.walking_speed == 5
