import random
import sys
import time

from collections import deque
from pyglet.gl import GL_QUADS
from pyglet.graphics import TextureGroup, Batch
from pyglet import image
from tempus_fugit_minecraft.block import Block,BRICK, STONE, GRASS, SAND, LIGHT_CLOUD,DARK_CLOUD, TREE_TRUNK, TREE_LEAVES
from tempus_fugit_minecraft.utilities import cube_vertices, WORLD_SIZE, FACES, TICKS_PER_SEC
from tempus_fugit_minecraft.player import Player
from typing import Callable
from tempus_fugit_minecraft import sound_list

if sys.version_info[0] >= 3:
    xrange = range


def normalize(position: tuple) -> tuple:
    """!
    @brief Accepts `position` of arbitrary precision and returns the 
        block containing that position.
    @param position : tuple of len 3
    @returns block_position : tuple of ints of len 3
    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


def sectorize(position: tuple) -> tuple:
    """!
    @brief Returns a tuple representing the sector for the given 
        `position`.
    @param position : tuple of len 3
    @returns sector : tuple of len 3
    """
    SECTOR_SIZE = 16  # Size of sectors used to ease block loading.

    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, 0, z


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

        self._initialize()
        self.sound_effects = sound_list.sound_effects_list
        self.background_noise = sound_list.background_sound_list
        self.current_background_noise = self.background_noise.get_sound('wind_blowing')
        self.current_background_noise.play_sound()

    def _initialize(self, immediate=False) -> None:
        """!
        @brief Initialize the world by placing all the blocks.
        @param immediate True: draw block immediatl; False: do not draw 
            Block immediately. (default=False)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        
        s = 1  # step size
        y = 0  # initial y height
        for x in xrange(-WORLD_SIZE, WORLD_SIZE + 1, s):
            for z in xrange(-WORLD_SIZE, WORLD_SIZE + 1, s):
                # create a layer stone and grass everywhere.
                self.add_block((x, y - 2, z), GRASS, immediate=immediate)
                self.add_block((x, y - 3, z), STONE, immediate=immediate)
                if x in (-WORLD_SIZE, WORLD_SIZE) or z in (-WORLD_SIZE,WORLD_SIZE):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        self.add_block((x, y + dy, z), STONE, immediate=immediate)

        # generate the hills randomly
        o = WORLD_SIZE - 10
        for _ in xrange(int((WORLD_SIZE * 1.5))):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2*s the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice([GRASS, SAND, BRICK])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=immediate)
                s -= d  # decrement side length so hills taper off

        clouds = self.generate_clouds_positions(world_size=WORLD_SIZE)
        self.place_cloud_blocks(clouds)
        self.generate_trees()

    def hit_test(self, position: tuple, vector: tuple, max_distance=8) -> tuple:
        """!
        @brief Line of sight search from current position. If a block is 
            intersected it is returned, along with the block previously 
            in the line of sight. If no block is found, return None, None.
        @param position : tuple of len 3 The (x, y, z) position to check 
            visibility from.
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
        @brief Returns False is given `position` is surrounded on all 6 
            sides by blocks, True otherwise.
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
        @brief Add a block with the given `texture` and `position` to 
            the world.
        @param position The (x, y, z) position of the block to add.
        @param texture The coordinates of the texture squares. Use 
            `tex_coords()` to generate.
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
        @param position : tuple of len 3 The (x, y, z) position of the 
            block to remove.
        @param immediate : bool Whether to immediately remove block from 
            canvas.
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
        @brief Check all blocks surrounding `position` and ensure their 
            visual state is current. This means hiding blocks that are 
            not exposed and ensuring that all exposed blocks are shown. 
            Usually used after a block is added or removed.
        @param position tuple of len 3 The (x, y, z) position to check 
            around.
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
        @brief Show the block at the given `position`. This method 
            assumes the block has already been added with add_block()
        @param position : tuple of len 3 The (x, y, z) position of the 
            block to show.
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
        @param position : tuple of len 3 The (x, y, z) position of the 
            block to show.
        @param texture : list of len 3 The coordinates of the texture 
            squares. Use `tex_coords()` to generate.
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
        @brief Hide the block at the given `position`. Hiding does not 
            remove the block from the world.
        @param position : tuple of len 3 The (x, y, z) position of the 
            block to hide.
        @param immediate : bool Whether to immediately remove the block 
            from the canvas.
        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position: tuple) -> None:
        """!
        @brief Private implementation of the `hide_block()` method.
        @param position : tuple of len 3 The (x, y, z) position of the 
            block to hide.
        """
        self._shown.pop(position).delete()

    def show_sector(self, sector: tuple) -> None:
        """!
        @brief Ensure all blocks in the given sector that should be 
            shown are drawn to the canvas.
        @param sector : tuple of len 3 The (x, y, z) coordinates of the 
            sector to show.
        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector: tuple) -> None:
        """!
        @brief Ensure all blocks in the given sector that should be 
            hidden are removed from the canvas.
        @param sector : tuple of len 3 The (x, y, z) coordinates of the 
            sector to hide.
        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before: tuple, after: tuple) -> None:
        """!
        @brief Move from sector `before` to sector `after`. A sector is 
            a contiguous x, y sub-region of world. Sectors are used to 
            speed up world rendering.
        @param before : tuple of len 3 The (x, y, z) sector we are 
            moving from.
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
        @brief Process the entire queue while taking periodic breaks. 
            This allows the game loop to run smoothly. The queue contains 
            calls to _show_block() and _hide_block() so this method should 
            be called if add_block() or remove_block() was called 
            with immediate=False.
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

    def generate_clouds_positions(self, world_size: int, num_of_clouds=int((WORLD_SIZE * 3.75))) -> list:
        """!
        @brief Generate sky cloud positions.
        @param world_size Half the world's size.
        @param num_of_clouds Number of clouds 
            (default is "WORLD_SIZE * 3.75").
        @return clouds list of lists representing cloud blocks coordinates.
        @see [Issue#20](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/20)
        @see [Issue#28](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/28)
        @see [Issue#44](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/44)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        game_margin = world_size
        clouds = list()
        for _ in xrange(num_of_clouds):
            cloud_center_x = random.randint(-game_margin, game_margin)
            cloud_center_z = random.randint(-game_margin, game_margin)
            cloud_center_y = random.choice([18,20,22,24,26])
            s = random.randint(3, 6) # 2 * s is the length of the cloud 
                                     # from the center of the cloud

            single_cloud = self.generate_single_cloud(cloud_center_x,
                                                      cloud_center_y,
                                                      cloud_center_z,
                                                      s)
            clouds.append(single_cloud)
        return clouds

    
    def place_cloud_blocks(self, clouds) -> None:
        """!
        @brief represent cloud block's coordinates in the sky.
        @param clouds list of lists; each inner list contains cloud 
            block's coordinates.
        @see [Issue#20](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/20)
        @see [Issue#28](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/28)
        """
        cloud_types = [LIGHT_CLOUD, DARK_CLOUD]
        for cloud in clouds:
            cloud_color = random.choice(cloud_types)
            for x, y, z in cloud:
                self.add_block((x, y, z), cloud_color, immediate=False)

    def can_pass_through_block(self, player_current_coords: tuple) -> bool:
        """!
        @brief Check if the block at the given palyer_current_coords is 
            a cloud block.
        @param player_current_coords Current (x,y,z) corrdinates for the 
            player.
        @return True if the coordinates correspond to a cloud block, 
            False otherwise.
        @see [Issue#57](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/57)
        """
        block = self.world.get(player_current_coords)
        return block is None or not block.is_collidable
    
    def handle_secondary_action(self) -> None:
        """!
        @brief Handles the player's secondary action
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        vector = self.player.get_sight_vector()
        position, previous = self.hit_test(self.player.position, vector)
        if previous and position and self.world[position].can_build_on:
            self.add_block(previous, self.player.block)

    def handle_primary_action(self) -> None:
        """!
        @brief Handles the player's primary action
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        vector = self.player.get_sight_vector()
        position, _ = self.hit_test(self.player.position, vector)
        if position and self.world[position].is_breakable:
            self.remove_block(position)

    def update(self, dt: float) -> None:
        """!
        @brief This method is scheduled to be called repeatedly by the 
            pyglet clock.
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
        @brief Checks to see if the player at the given `position` and 
            `height` is colliding with any blocks in the world.
        @param position : tuple of len 3 The (x, y, z) position to check 
            for collisions at.
        @param height : int or float The height of the player.
        @return position : tuple of len 3 The new position of the player 
            taking into account collisions.
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
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
                    player_currnet_coords = list(np)
                    player_currnet_coords[1] -= dy
                    player_currnet_coords[i] += face[i]
                    if self.can_pass_through_block(player_current_coords= tuple(player_currnet_coords)):
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
        @brief Handles the change of the vision field when the player 
            moves their head
        @param dx The x change in the field of vision (relative to the 
            previous motion)
        @param dy The y change in the field of vision (relative to the 
            previous motion)
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        self.player.adjust_sight(dx, dy)

    def handle_change_active_block(self, index: int) -> None:
        """!
        @brief Switches between active blocks held by the player
        @param index The value of the current active block in the 
            player's inventory
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        self.player.select_active_item(index)

    def handle_speed_change(self, increase: bool) -> None:
        """!
        @brief Handles the speed change event
        @param increase A boolean indicator of whether we increase or 
            decrease the speed
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        if increase:
            self.player.speed_up()
        else:
            self.player.speed_down()

    def handle_jump(self) -> None:
        """!
        @brief Handles the jump event
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
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
        @param forward Tri-state value of 1, 0, -1 indicating if we are 
            going to be moving forward, staying constant, or stopping
        @param backward Tri-state value of 1, 0, -1 indicating if we are 
            going to be moving backward staying constant, or stopping
        @param left Tri-state value of 1, 0, -1 indicating if we are 
            going to be moving left, staying constant, or stopping
        @param right Tri-state value of 1, 0, -1 indicating if we are 
            going to be moving right, staying constant, or stopping
        @see [Issue#68](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/68)
        """
        def handle_movement_for_direction(direction, move, stop):
            # private helper for consistently applying direction
            if direction != 0:
                if direction == 1:
                    move()
                else:
                    stop()

        handle_movement_for_direction(forward, self.player.move_forward, self.player.stop_forward)
        handle_movement_for_direction(backward, self.player.move_backward, self.player.stop_backward)
        handle_movement_for_direction(left, self.player.move_left, self.player.stop_left)
        handle_movement_for_direction(right, self.player.move_right, self.player.stop_right)

    #issue 82
    def handle_flight(self, ascending, descending):
        if ascending != 0:
            self.player.ascend = True if ascending == 1 else False
        elif descending != 0:
            self.player.descend = True if descending == 1 else False


    #issue80; #issue84
    def generate_trees(self, num_trees=int((WORLD_SIZE * 3.125))):
        """!
        @brief Generate trees' (trunks and leavs) positions.
        @details single_tree is a list contains 2 lists of coordinates: 
            list of trunks, and list of leaves.
        @details list trees appends each single_tree list.
        @details the trees are set to be built on SAND and GRASS only.
        @param num_trees Number of clouds (default is "WORLD_SIZE * 3.125").
        @return trees list of lists representing trees blocks (single 
        tree=list_trunks , list_leaves) coordinates.
        @see [Issue#80](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/80)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        suggested_places_for_trees = []
        trees = list()
        grass_list = [coords for coords , block in self.world.items() if block == GRASS and coords[1]<=0]
        min_grass_level = min(ground[1] for ground in grass_list)
        ground_grass_list = [ground for ground in grass_list if ground[1] == min_grass_level]

        for coords in ground_grass_list:
            x,y,z = coords
            does_not_grass_have_block_above_it = all([(x, y+j, z) not in self.world for j in range(1,10)])
            if does_not_grass_have_block_above_it:
                suggested_places_for_trees.append(coords)

        for _ in range(num_trees):
            if suggested_places_for_trees:
                single_tree=[]
                base_x, base_y, base_z = random.choice(suggested_places_for_trees)
                suggested_places_for_trees.remove((base_x, base_y, base_z))
                single_tree = self.generate_single_tree(base_x,base_y+1,base_z, trunk_height=5)
                trees.append(single_tree)
            else:
                break
        return trees
    
    def generate_single_tree(self, x, y, z, trunk_height=4):
        """!
        @brief represent trees' components.
        
        @details Tree components are Trunks and Leaves.
        @details The function returns 2 lists: list of trunks, list 
            of leaves.
        @param x,y,z The coordinates of the position of the tree to be 
            built at.
        @param trunk_height Number of trunks (stems) in the tree 
            (default=4).
        @return [single_stem,single_leaves], coordinates for the tree 
            components.
        @see [Issue#80](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/80)
        """
        single_stem = []
        single_leaves = []

        for stem in range(trunk_height):
            self.add_block((x, y + stem, z), TREE_TRUNK, immediate=False)
            single_stem.append((x, y + stem, z))

        for dx in range(-2,3):
            for dy in range(0,3):
                for dz in range(-2,3):
                    self.add_block((x + dx, y + trunk_height + dy, z + dz), TREE_LEAVES, immediate=False)
                    single_leaves.append((x + dx, y + trunk_height + dy, z + dz))
        return [single_stem,single_leaves]
    
    def generate_single_cloud(self, cloud_center_x,cloud_center_y, cloud_center_z,s) -> list:
        """!
        @brief generate a single cloud (list of cloud blocks).
        
        @param cloud_center_x Represents the x-coordinate center of the 
            cloud.
        @param cloud_center_x Represents the y-coordinate (height) 
            center of the cloud.
        @param cloud_center_x Represents the z-coordinate center of the 
            cloud.
        @param s represent number of blocks drawn from center - goes in 
            each direction around the center.
        
        @return single_cloud A list that contains list of blocks' 
            coordinates that represent a cloud.
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        """
        
        single_cloud = []
        for x in xrange(cloud_center_x - s, cloud_center_x + s + 1):
                for z in xrange(cloud_center_z - s, cloud_center_z + s + 1):
                    if (x - cloud_center_x) ** 2 + (z - cloud_center_z) ** 2 > (s + 1) ** 2:
                        continue
                    single_cloud.append((x, cloud_center_y, z))
        
        return single_cloud