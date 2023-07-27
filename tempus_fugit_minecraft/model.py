import random
import sys
import time
from collections import deque
from typing import Callable

from pyglet.gl import GL_QUADS
from pyglet.graphics import TextureGroup, Batch
from pyglet import image

from tempus_fugit_minecraft import sound_list
from tempus_fugit_minecraft.block import Block
from tempus_fugit_minecraft.player import Player
from tempus_fugit_minecraft.utilities import FACES, TICKS_PER_SEC, cube_vertices
from tempus_fugit_minecraft.world import World, normalize, sectorize, Position

if sys.version_info[0] >= 3:
    xrange = range


class Model(object):
    """!
    @brief A 3D world model for block-based rendering.
    @return model an instance of Model class.
    """
    def __init__(self) -> None:
        """!
        @brief init function for Model class
        """
        TEXTURE_PATH = 'assets/texture.png'

        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are
        # shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertexList` for all shown
        # blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sector = None
        self.sectors = {}

        # Simple function queue implementation. The queue is populated
        # with _show_block() and _hide_block() calls
        self.queue = deque()

        self.player = Player()
        self.generate()

        self._initialize()
        self.sound_effects = sound_list.sound_effects_list
        self.background_noise = sound_list.background_sound_list
        self.current_background_noise = self.background_noise.get_sound('wind_blowing')
        self.current_background_noise.play_sound()

    def generate(self) -> None:
        """!
        @brief Initialize the world by placing all the blocks.
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        def add_blocks(blockList: list[tuple[Block, Position]]):
            for block, position in blockList:
                self.add_block(position, block, immediate=False)
                
        add_blocks(World.generate_base_layer())
        for hill in World.generate_hills():
            add_blocks(hill)        
        for cloud in World.generate_clouds():
            add_blocks(cloud)
        for tree in World.generate_trees(self):
            add_blocks(tree)

    def hit_test(self, position: tuple, vector: tuple, max_distance=8) -> tuple:
        """!
        @brief Line of sight search from current position. If a block is intersected it is returned, along with the
            block previously in the line of sight. If no block is found,  return None, None.
        @param position : tuple of len 3 The (x, y, z) position to check visibility from.
        @param vector : tuple of len 3 The line of sight vector.
        @param max_distance : int How many blocks away to search for a hit.
        @returns previous : tuple of len 3 The previous block.
        @returns block : tuple of len 3 The hit block.
        """
        m = 8
        x, y, z = position
        dx, dy, dz = vector
        previous = None
        for _ in xrange(max_distance * m):
            key = normalize((x, y, z))
            if key != previous and key in self.world:
                return key, previous
            previous = key
            x, y, z = x + dx / m, y + dy / m, z + dz / m
        return None, None

    def exposed(self, position: tuple) -> bool:
        """!
        @brief Returns False is given `position` is surrounded on all 6 sides by blocks, True otherwise.
        @param position : tuple of len 3 The (x, y, z) position to check
        @returns boolean
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position: tuple, block: Block, immediate=True) -> None:
        """!
        @brief Add a block with the given `texture` and `position` to the world.
        @param position : The (x, y, z) position of the block to add.
        @param block : The coordinates of the texture squares. Use `tex_coords()` to generate.
        @param immediate : bool Whether to draw the block immediately.
        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = block
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position: tuple, immediate=True) -> None:
        """!
        @brief Remove the block at the given `position`.
        @param position : tuple of len 3 The (x, y, z) position of the block to remove.
        @param immediate : bool Whether to immediately remove block from canvas.
        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
                self.sound_effects.get_sound('rock_hit').play_sound()
            self.check_neighbors(position)

    def check_neighbors(self, position: tuple) -> None:
        """!
        @brief Check all blocks surrounding `position` and ensure their visual state is current. This means hiding
            blocks that are not exposed and ensuring that all exposed blocks are shown. Usually used after a block is
            added or removed.
        @param position tuple of len 3 The (x, y, z) position to check around.
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            key = (x + dx, y + dy, z + dz)
            if key not in self.world:
                continue
            if self.exposed(key):
                if key not in self.shown:
                    self.show_block(key)
            else:
                if key in self.shown:
                    self.hide_block(key)

    def show_block(self, position: tuple, immediate=True) -> None:
        """!
        @brief Show the block at the given `position`. This method assumes the block has already been added with
            add_block()
        @param position : tuple of len 3 The (x, y, z) position of the block to show.
        @param immediate : bool Whether to show the block immediately.
        """
        if position not in self.world:
            return

        block = self.world[position]
        self.shown[position] = block
        if immediate:
            self._show_block(position, block)
        else:
            self._enqueue(self._show_block, position, block)

    def _show_block(self, position: tuple, block: Block) -> None:
        """!
        @brief Private implementation of the `show_block()` method.
        @param position : tuple of len 3 The (x, y, z) position of the block to show.
        @param block : list of len 3 The coordinates of the texture squares. Use `tex_coords()` to generate.
        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(block.texture_coordinates)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
                                               ('v3f/static', vertex_data),
                                               ('t2f/static', texture_data))

    def hide_block(self, position: tuple, immediate=True) -> None:
        """!
        @brief Hide the block at the given `position`. Hiding does not remove the block from the world.
        @param position : tuple of len 3 The (x, y, z) position of the block to hide.
        @param immediate : bool Whether to immediately remove the block from the canvas.
        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position: tuple) -> None:
        """!
        @brief Private implementation of the `hide_block()` method.
        @param position : tuple of len 3 The (x, y, z) position of the block to hide.
        """
        self._shown.pop(position).delete()

    def show_sector(self, sector: tuple) -> None:
        """!
        @brief Ensure all blocks in the given sector that should be shown are drawn to the canvas.
        @param sector : tuple of len 3 The (x, y, z) coordinates of the sector to show.
        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector: tuple) -> None:
        """!
        @brief Ensure all blocks in the given sector that should be hidden are removed from the canvas.
        @param sector : tuple of len 3 The (x, y, z) coordinates of the sector to hide.
        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before: tuple, after: tuple) -> None:
        """!
        @brief Move from sector `before` to sector `after`. A sector is a contiguous x, y sub-region of world.
            Sectors are used to speed up world rendering.
        @param before : tuple of len 3 The (x, y, z) sector we are moving from.
        @param after : tuple of len 3 The (x, y, z) sector we are moving to.
        """
        before_set = set()
        after_set = set()
        pad = 4
        for dx in xrange(-pad, pad + 1):
            for dy in [0]:  # xrange(-pad, pad + 1):
                for dz in xrange(-pad, pad + 1):
                    if dx ** 2 + dy ** 2 + dz ** 2 > (pad + 1) ** 2:
                        continue
                    if before:
                        x, y, z = before
                        before_set.add((x + dx, y + dy, z + dz))
                    if after:
                        x, y, z = after
                        after_set.add((x + dx, y + dy, z + dz))
        show = after_set - before_set
        hide = before_set - after_set
        for sector in show:
            self.show_sector(sector)
        for sector in hide:
            self.hide_sector(sector)

    def _enqueue(self, func: Callable, *args) -> None:
        """!
        @brief Add `func` to the internal queue.
        @param func : Callable The function to add to the queue.
        @param args The arguments to pass to the function.
        """
        self.queue.append((func, args))

    def _dequeue(self) -> None:
        """!
        @brief Pop the top function from the internal queue and call it.
        """
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self) -> None:
        """!
        @brief Process the entire queue while taking periodic breaks. This allows the game loop to run smoothly. The
            queue contains calls to _show_block() and _hide_block() so this method should be called if add_block() or
            remove_block() was called with immediate=False.
         """
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self) -> None:
        """!
        @brief Process the entire queue with no breaks.
        """
        while self.queue:
            self._dequeue()

    def can_pass_through_block(self, player_current_coords: tuple) -> bool:
        """!
        @brief Check if the block at the given player_current_coords is a cloud block.
        @param player_current_coords Current (x,y,z) coordinates for the player.
        @return True if the coordinates correspond to a cloud block, False otherwise.
        @see [Issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        block = self.world.get(player_current_coords)
        return block is None or not block.is_collidable

    def handle_secondary_action(self) -> None:
        """!
        @brief Handles the player's secondary action, adding a block.
        @see [Issue#42](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/42)
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        @see [Issue#42](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/42)
        """
        vector = self.player.get_sight_vector()
        position, previous = self.hit_test(self.player.position, vector)
        if previous and position and self.world[position].can_build_on:
            self.add_block(previous, self.player.block)

    def handle_primary_action(self) -> None:
        """!
        @brief Handles the player's primary action, breaking a block
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        vector = self.player.get_sight_vector()
        position, _ = self.hit_test(self.player.position, vector)
        if position and self.world[position].is_breakable:
            self.remove_block(position)

    def update(self, dt: float) -> None:
        """!
        @brief This method is scheduled to be called repeatedly by the pyglet clock.
        @param dt : float The change in time (seconds) since the last call.
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        self.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.sector:
            self.change_sectors(self.sector, sector)
            if self.sector is None:
                self.process_entire_queue()
            self.sector = sector

        self.player.check_player_within_world_boundaries()

        moves = 8
        dt = min(dt, 0.2)
        for _ in xrange(moves):
            self.player.update(dt / moves, self.collide)

    def collide(self, position: tuple, height: int) -> tuple:
        """!
        @brief Checks to see if the player at the given `position` and `height` is colliding with any blocks in the
            world.
        @param position : tuple of len 3 The (x, y, z) position to check for collisions at.
        @param height : int or float The height of the player.
        @return position : tuple of len 3 The new position of the player taking into account collisions.
        @see [Issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57) 
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        @see [Issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        # How much overlap with a dimension of a surrounding block you
        # need to have to count as a collision. If 0, touching terrain
        # at all counts as a collision. If .49, you sink into the
        # ground, as if walking through tall grass. If >= .5, you'll
        # fall through the ground.
        pad = 0.25
        p = list(position)
        np = normalize(position)
        for face in FACES:  # check all surrounding blocks
            for i in xrange(3):  # check each dimension independently
                if not face[i]:
                    continue
                # How much overlap you have with this dimension.
                d = (p[i] - np[i]) * face[i]
                if d < pad:
                    continue
                for dy in xrange(height):  # check each height
                    player_current_coords = list(np)
                    player_current_coords[1] -= dy
                    player_current_coords[i] += face[i]
                    if self.can_pass_through_block(player_current_coords=tuple(player_current_coords)):
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.player.dy = 0
                    break
        return tuple(p)

    def handle_adjust_vision(self, dx: int, dy: int) -> None:
        """!
        @brief Handles the change of the vision field when the player moves their head
        @param dx The x change in the field of vision (relative to the previous motion)
        @param dy The y change in the field of vision (relative to the previous motion)
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        self.player.adjust_sight(dx, dy)

    def handle_change_active_block(self, index: int) -> None:
        """!
        @brief Switches between active blocks held by the player
        @param index The value of the current active block in the player's inventory
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        self.player.select_active_item(index)

    def handle_speed_change(self, increase: bool) -> None:
        """!
        @brief Handles the speed change event
        @param increase A boolean indicator of whether we increase or decrease the speed
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        if increase:
            self.player.increase_speed()
        else:
            self.player.decrease_speed()

    def handle_jump(self) -> None:
        """!
        @brief Handles the jump event
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
     
    def handle_jump_change(self, increase: bool) -> None:
        """!
        @brief Handles the jump speed change event
        @param increase A boolean indicator of whether we increase or decrease the jump speed
        @see [issue#39](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/39)
        """
        if increase:
            self.player.increase_jump_speed()
        else:
            self.player.decrease_jump_speed()

    #Issue 68
    def handle_jump(self):
        self.player.jump()

    def handle_flight_toggle(self) -> None:
        """!
        @brief Handles the flight toggle event
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        self.player.toggle_flight()

    def handle_movement(self, forward, backward, left, right) -> None:
        """!
        @brief Movement handler (directs the movement of the player)
        @param forward Tri-state value of 1, 0, -1 indicating if we are going to be moving forward, staying constant, or
            stopping
        @param backward Tri-state value of 1, 0, -1 indicating if we are going to be moving backward staying
            constant, or stopping
        @param left Tri-state value of 1, 0, -1 indicating if we are going to be moving left, staying constant,
            or stopping
        @param right Tri-state value of 1, 0, -1 indicating if we are going to be moving right, staying constant,
            or stopping
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        def handle_movement_for_direction(direction, move, stop):
            """!
            @brief Private helper for consistently applying direction
            @param direction : The direction to apply the movement to
            @param move : The function to call when we are moving in the given direction
            @param stop : The function to call when we are stopping in the given direction
            """
            if direction != 0:
                if direction == 1:
                    move()
                else:
                    stop()

        handle_movement_for_direction(forward, self.player.move_forward, self.player.stop_forward)
        handle_movement_for_direction(backward, self.player.move_backward, self.player.stop_backward)
        handle_movement_for_direction(left, self.player.move_left, self.player.stop_left)
        handle_movement_for_direction(right, self.player.move_right, self.player.stop_right)

    def handle_flight(self, ascending, descending):
        """!
        @brief Handles the flight event
        @param ascending : Tri-state value of 1, 0, -1 indicating if we are going to be moving up, staying constant, or
            stopping
        @param descending : Tri-state value of 1, 0, -1 indicating if we are going to be moving down, staying constant,
            or stopping
        @see [Issue#82](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/82)
        """
        if ascending != 0:
            self.player.ascend = True if ascending == 1 else False
        elif descending != 0:
            self.player.descend = True if descending == 1 else False
