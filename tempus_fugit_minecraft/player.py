from typing import Callable
from tempus_fugit_minecraft.utilities import WORLD_SIZE
from tempus_fugit_minecraft.block import BRICK, GRASS, SAND, TREE_TRUNK, TREE_LEAVES
import math


class Player:
    def __init__(self) -> None:
        """!
        @brief Initializes an instance of the Player class
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        # About the height of a block.
        self.MAX_JUMP_HEIGHT = 1.0
        self.MAX_FALL_SPEED = 50
        self.FLYING_SPEED = 15
        self.GRAVITY = 20.0
        # To derive the formula for calculating jump speed, first solve
        #    v_t = v_0 + a * t
        # for the time at which you achieve maximum height, where a is the acceleration
        # due to gravity and v_t = 0. This gives:
        #    t = - v_0 / a
        # Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
        #    s = s_0 + v_0 * t + (a * t^2) / 2
        self.JUMP_SPEED = math.sqrt(2 * self.GRAVITY * self.MAX_JUMP_HEIGHT)
        self.PLAYER_HEIGHT = 2
        self.WALK_SPEED_INCREMENT = 5

        self.walking_speed = self.WALK_SPEED_INCREMENT
        # When flying gravity has no effect and speed is increased.
        self.flying = False
        self.ascend = False
        self.descend = False
        # Strafing is moving lateral to the direction you are facing,
        # e.g. moving to the left or right while continuing to face forward.
        #
        # First element is -1 when moving forward, 1 when moving back, and 0
        # otherwise. The second element is -1 when moving left, 1 when moving
        # right, and 0 otherwise.
        self.strafe = [0, 0]
        # Current (x, y, z) position in the world, specified with floats. Note
        # that, perhaps unlike in math class, the y-axis is the vertical axis.
        self.position = (0, 0, 0)
        # First element is rotation of the player in the x-z plane (ground
        # plane) measured from the z-axis down. The second is the rotation
        # angle from the ground plane up. Rotation is in degrees.
        #
        # The vertical plane rotation ranges from -90 (looking straight down) to
        # 90 (looking straight up). The horizontal rotation range is unbounded.
        self.rotation = (0, 0)
        # Velocity in the y (upward) direction.
        self.dy = 0
        # A list of blocks the player can place. Hit num keys to cycle.
        self.inventory = [BRICK, GRASS, SAND, TREE_TRUNK, TREE_LEAVES]
        # The current block the user can place. Hit num keys to cycle.
        self.block = self.inventory[0]

    def get_sight_vector(self) -> tuple:
        """!
        @brief Returns the current line of sight vector indicating the direction the player is looking.
        @param None
        @return A tuple representing the 3D vector the player is looking toward
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        x, y = self.rotation
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return dx, dy, dz

    def get_motion_vector(self) -> tuple:
        """!
        @brief Returns the current motion vector indicating the velocity of the player.
        @param None
        @return A tuple containing the velocity in x, y, and z respectively.
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        if any(self.strafe):
            x, y = self.rotation
            strafe = math.degrees(math.atan2(*self.strafe))
            y_angle = math.radians(y)
            x_angle = math.radians(x + strafe)
            if self.flying:
                m = math.cos(y_angle)
                dy = math.sin(y_angle)
                if self.strafe[1]:
                    # Moving left or right.
                    dy = 0.0
                    m = 1
                if self.strafe[0] > 0:
                    # Moving backwards.
                    dy *= -1
                # When you are flying up or down, you have less left and right
                # motion.
                dx = math.cos(x_angle) * m
                dz = math.sin(x_angle) * m
            else:
                dy = 0.0
                dx = math.cos(x_angle)
                dz = math.sin(x_angle)
        else:
            dy = 0.0
            dx = 0.0
            dz = 0.0
        return dx, dy, dz

    def speed_up(self) -> None:
        """!
        @brief Increases the walking speed of the player.
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        @see [Issue#38](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/38)
        """
        if self.walking_speed <= 15:
            self.walking_speed += self.WALK_SPEED_INCREMENT

    def speed_down(self) -> None:
        """!
        @brief Decreases the walking speed of the player
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        @see [Issue#38](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/38)
        """
        if self.walking_speed > 5:
            self.walking_speed -= self.WALK_SPEED_INCREMENT

    def move_forward(self) -> None:
        """!
        @brief Move one space to the front
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[0] -= 1
    
    def move_backward(self) -> None:
        """!
        @brief Move one space to the rear
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[0] += 1

    def move_left(self) -> None:
        """!
        @brief Move one space to the left
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[1] -= 1

    def move_right(self) -> None:
        """!
        @brief Move one space to the right
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[1] += 1

    def jump(self) -> None:
        """!
        @brief If the user is grounded, jump
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        if self.dy == 0:
            self.dy = self.JUMP_SPEED

    def select_active_item(self, index: int) -> None:
        """!
        @brief Selects the active item in the player's inventory
        @param index The current index of the inventory
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        selected_index = index % len(self.inventory)
        self.block = self.inventory[selected_index]

    def stop_forward(self) -> None:
        """!
        @brief Stops movement to the front
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[0] += 1
    
    def stop_backward(self) -> None:
        """!
        @brief Stops movement to the rear
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[0] -= 1

    def stop_left(self) -> None:
        """!
        @brief Stops movement to the left
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[1] += 1

    def stop_right(self) -> None:
        """!
        @brief Stops movement to the right
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.strafe[1] -= 1

    def adjust_sight(self, dx: int, dy: int) -> None:
        """!
        @brief Adjusts the sight vector of the player
        @param dx The relative x axis movement of the mouse
        @param dy The relative y axis movement of the mouse
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        x, y = self.rotation
        m = 0.15
        x = dx * m + x
        y = dy * m + y
        y = max(-90, min(90, y))
        self.rotation = (x, y)

    def current_speed(self) -> float:
        """!
        @brief Gets the current walking or flying speed
        @param None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        return self.FLYING_SPEED if self.flying else self.walking_speed
    
    def toggle_flight(self) -> None:
        """! 
        @brief Toggles flight in game
        @params None
        @return None
        @see [Issue#67](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/67)
        """
        self.flying = not self.flying

    def update(self, dt: float, collision_checker: Callable[[tuple, int], tuple]) -> None:
        """!
        @brief Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.
        @param dt : float The change in time (seconds) since the last call.
        @param collision_checker Takes in a new player position and the player height,
        then returns a new position adjusted for any potential block collisions
        @return None
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        @see [Issue#82](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/82)
        """
        # walking
        speed = self.current_speed()
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d

        # gravity
        if not self.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.dy -= dt * self.GRAVITY
            self.dy = max(self.dy, -self.MAX_FALL_SPEED)
            dy += self.dy * dt
        else:
            # The direction will either add or subtract one, or both, if the
            # ascending or descending properties are true, the result of
            # this will be -1, 0 or 1 which will change the direction of dy.
            direction = 0
            direction += 1 if self.ascend else 0
            direction -= 1 if self.descend else 0
            dy += direction * dt * self.FLYING_SPEED

        # collisions
        x, y, z = self.position
        self.position = collision_checker((x + dx, y + dy, z + dz), self.PLAYER_HEIGHT)
    
    def check_player_within_world_boundaries(self) -> None:
        """!
        @brief Ensure that the player character remains within the 
        confines of the defined game world.
        @param None
        @return None
        @see [Issue#25](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/25)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        x,y,z = self.position

        x = self.keep_player_within_coordinates(x , boundary_size=WORLD_SIZE)
        z = self.keep_player_within_coordinates(z , boundary_size=WORLD_SIZE)        
        self.position = (x,y,z)

    def keep_player_within_coordinates(self, dimension, boundary_size=WORLD_SIZE):
        """!
        @brief check whether the dimension (usually x or z) is within the boundary size.
        @param dimension represent a player dimension (x,y, or z)
        @param boundary_size represent the size of the world withing the walls.
        @return The dimension adjusted to be within the boundary size.
        @see [Issue#25](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/25)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        if dimension > boundary_size:
            return boundary_size
        elif dimension < -boundary_size:
            return -boundary_size
        else:
            return dimension