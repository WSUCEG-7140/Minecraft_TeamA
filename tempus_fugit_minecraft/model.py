import random
import sys
import time

from collections import deque
from pyglet.gl import GL_QUADS
from pyglet.graphics import TextureGroup, Batch
from pyglet import image
from tempus_fugit_minecraft.utilities import *
from tempus_fugit_minecraft.player import Player
from typing import Callable

if sys.version_info[0] >= 3:
    xrange = range


def normalize(position: tuple) -> tuple:
    """Accepts `position` of arbitrary precision and returns the block containing that position.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    block_position : tuple of ints of len 3
    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


def sectorize(position: tuple) -> tuple:
    """Returns a tuple representing the sector for the given `position`.

    Parameters
    ----------
    position : tuple of len 3

    Returns
    -------
    sector : tuple of len 3
    """
    SECTOR_SIZE = 16  # Size of sectors used to ease block loading.

    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, 0, z


class Model(object):
    """A 3D world model for block-based rendering."""

    def __init__(self) -> None:
        TEXTURE_PATH = 'assets/texture.png'
        
        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = Batch()

        # A TextureGroup manages an OpenGL texture.
        self.group = TextureGroup(image.load(TEXTURE_PATH).get_texture())

        # A mapping from position to the texture of the block at that position.
        # This defines all the blocks that are currently in the world.
        self.world = {}

        # Same mapping as `world` but only contains blocks that are shown.
        self.shown = {}

        # Mapping from position to a pyglet `VertexList` for all shown blocks.
        self._shown = {}

        # Mapping from sector to a list of positions inside that sector.
        self.sector = None
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self.player = Player()

        self._initialize()

    def _initialize(self, immediate=False) -> None:
        """Initialize the world by placing all the blocks."""
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer stone and grass everywhere.
                self.add_block((x, y - 2, z), GRASS, immediate=immediate)
                self.add_block((x, y - 3, z), STONE, immediate=immediate)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        self.add_block((x, y + dy, z), STONE, immediate=immediate)

        # generate the hills randomly
        o = n - 10
        for _ in xrange(120):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(1, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
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

        clouds = self.generate_clouds_positions(n, num_of_clouds=150)
        self.place_cloud_blocks(clouds)


    def hit_test(self, position: tuple, vector: tuple, max_distance=8) -> tuple:
        """Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return None, None.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check visibility from.
        vector : tuple of len 3
            The line of sight vector.
        max_distance : int
            How many blocks away to search for a hit.

        Returns
        -------
        previous : tuple of len 3
            The previous block.
        block : tuple of len 3
            The hit block.
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
        """Returns False is given `position` is surrounded on all 6 sides by blocks, True otherwise.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check

        Returns
        -------
        boolean
        """
        x, y, z = position
        for dx, dy, dz in FACES:
            if (x + dx, y + dy, z + dz) not in self.world:
                return True
        return False

    def add_block(self, position: tuple, texture: list, immediate=True) -> None:
        """!
        @brief Add a block with the given `texture` and `position` to the world.

        @param position The (x, y, z) position of the block to add.
        @param texture The coordinates of the texture squares. Use `tex_coords()`
            to generate.
        immediate : bool
            Whether to draw the block immediately.
        """
        if position in self.world:
            self.remove_block(position, immediate)
        self.world[position] = texture
        self.sectors.setdefault(sectorize(position), []).append(position)
        if immediate:
            if self.exposed(position):
                self.show_block(position)
            self.check_neighbors(position)

    def remove_block(self, position: tuple, immediate=True) -> None:
        """Remove the block at the given `position`.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to remove.
        immediate : bool
            Whether to immediately remove block from canvas.
        """
        del self.world[position]
        self.sectors[sectorize(position)].remove(position)
        if immediate:
            if position in self.shown:
                self.hide_block(position)
            self.check_neighbors(position)

    def check_neighbors(self, position: tuple) -> None:
        """Check all blocks surrounding `position` and ensure their visual
        state is current. This means hiding blocks that are not exposed and
        ensuring that all exposed blocks are shown. Usually used after a block
        is added or removed.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check around.
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
        """Show the block at the given `position`. This method assumes the
        block has already been added with add_block()

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        immediate : bool
            Whether to show the block immediately.
        """
        if position not in self.world:
            return
        
        texture = self.world[position]
        self.shown[position] = texture
        if immediate:
            self._show_block(position, texture)
        else:
            self._enqueue(self._show_block, position, texture)

    def _show_block(self, position: tuple, texture: list) -> None:
        """Private implementation of the `show_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to show.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
        """
        x, y, z = position
        vertex_data = cube_vertices(x, y, z, 0.5)
        texture_data = list(texture)
        # create vertex list
        # FIXME Maybe `add_indexed()` should be used instead
        self._shown[position] = self.batch.add(24, GL_QUADS, self.group,
                                               ('v3f/static', vertex_data),
                                               ('t2f/static', texture_data))

    def hide_block(self, position: tuple, immediate=True) -> None:
        """Hide the block at the given `position`. Hiding does not remove the block from the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        immediate : bool
            Whether to immediately remove the block from the canvas.
        """
        self.shown.pop(position)
        if immediate:
            self._hide_block(position)
        else:
            self._enqueue(self._hide_block, position)

    def _hide_block(self, position: tuple) -> None:
        """Private implementation of the `hide_block()` method.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to hide.
        """
        self._shown.pop(position).delete()

    def show_sector(self, sector: tuple) -> None:
        """Ensure all blocks in the given sector that should be shown are drawn to the canvas.

        Parameters
        ----------
        sector : tuple of len 3
            The (x, y, z) coordinates of the sector to show.
        """
        for position in self.sectors.get(sector, []):
            if position not in self.shown and self.exposed(position):
                self.show_block(position, False)

    def hide_sector(self, sector: tuple) -> None:
        """Ensure all blocks in the given sector that should be hidden are removed from the canvas.

        Parameters
        ----------
        sector : tuple of len 3
            The (x, y, z) coordinates of the sector to hide.
        """
        for position in self.sectors.get(sector, []):
            if position in self.shown:
                self.hide_block(position, False)

    def change_sectors(self, before: tuple, after: tuple) -> None:
        """Move from sector `before` to sector `after`. A sector is a
        contiguous x, y sub-region of world. Sectors are used to speed up
        world rendering.

        Parameters
        ----------
        before : tuple of len 3
            The (x, y, z) sector we are moving from.
        after : tuple of len 3
            The (x, y, z) sector we are moving to.
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
        """Add `func` to the internal queue.

        Parameters
        ----------
        func : Callable
            The function to add to the queue.
        args
            The arguments to pass to the function.
        """
        self.queue.append((func, args))

    def _dequeue(self) -> None:
        """Pop the top function from the internal queue and call it."""
        func, args = self.queue.popleft()
        func(*args)

    def process_queue(self) -> None:
        """Process the entire queue while taking periodic breaks. This allows
        the game loop to run smoothly. The queue contains calls to
        _show_block() and _hide_block() so this method should be called if
        add_block() or remove_block() was called with immediate=False.
        """
        start = time.perf_counter()
        while self.queue and time.perf_counter() - start < 1.0 / TICKS_PER_SEC:
            self._dequeue()

    def process_entire_queue(self) -> None:
        """Process the entire queue with no breaks."""
        while self.queue:
            self._dequeue()

    #issue20; #issue28
    @staticmethod
    def generate_clouds_positions(world_size: int, num_of_clouds=250) -> list:
        """!
        @brief Generate sky cloud positions.
        
        @param world_size Half the world's size.
        @param num_of_clouds Number of clouds (default is 250).
        
        @return clouds list of lists representing cloud blocks coordinates.
        """
        game_margin = world_size
        clouds = list()
        for _ in xrange(num_of_clouds):
            cloud_center_x = random.randint(-game_margin, game_margin)  # x position of the cloud
            cloud_center_z = random.randint(-game_margin, game_margin)  # z position of the cloud
            cloud_center_y = 20                     # y position of the cloud (height)
            s = random.randint(3, 6)   # 2 * s is the side length of the cloud

            single_cloud = []
            for x in xrange(cloud_center_x - s, cloud_center_x + s + 1):
                for z in xrange(cloud_center_z - s, cloud_center_z + s + 1):
                    if (x - cloud_center_x) ** 2 + (z - cloud_center_z) ** 2 > (s + 1) ** 2:
                        continue
                    single_cloud.append((x, cloud_center_y, z))
            clouds.append(single_cloud)
        return clouds

    #issue20; #issue28
    def place_cloud_blocks(self, clouds):
        """!
        @breif represent cloud block's coordinates in the sky.

        @param clouds list of lists; each inner list contains cloud block's coordinates.

        @return None, but draw a cloud block at its corresponding coordinates.
        """
        cloud_types = [LIGHT_CLOUD,DARK_CLOUD]
        for cloud in clouds:
            cloud_color = random.choice(cloud_types)
            for x,y,z in cloud:
                self.add_block((x,y,z) , cloud_color , immediate=False)

    #issue57
    def can_pass_through_block(self, player_current_coords):
        """!
        @brief Check if the block at the given palyer_current_coords is a cloud block.
        
        @param player_current_coords Current (x,y,z) corrdinates for the player.
        
        @return True if the coordinates correspond to a cloud block, False otherwise.
        """
        return self.is_a_cloud_block(self.world.get(player_current_coords))
    
    #issue42
    def is_a_cloud_block(self, texture):
        """!
        @brief Check if the texture is of type cloud.
        
        @param texture The texture that was clicked by the mouse left-button.
        
        @return True if the texture belong to clouds' textures, False otherwise.
        """
        return texture in [LIGHT_CLOUD,DARK_CLOUD]
    
    #issue 68
    def handle_secondary_action(self):
        vector = self.player.get_sight_vector()
        block, previous = self.hit_test(self.player.position, vector)
        if previous and block and not self.is_a_cloud_block(self.world.get(block)):
            self.add_block(previous, self.player.block)

    #issue 68
    def handle_primary_action(self):
        vector = self.player.get_sight_vector()
        block, _ = self.hit_test(self.player.position, vector)
        if block:
            texture = self.world[block]
            if texture is not STONE:
                self.remove_block(block)

    #issue 68
    def update(self, dt: float) -> None:
        """This method is scheduled to be called repeatedly by the pyglet clock.

        Parameters
        ----------
        dt : float
            The change in time (seconds) since the last call.
        """
        self.process_queue()
        sector = sectorize(self.player.position)
        if sector != self.sector:
            self.change_sectors(self.sector, sector)
            if self.sector is None:
                self.process_entire_queue()
            self.sector = sector
        moves = 8
        dt = min(dt, 0.2)
        for _ in xrange(moves):
            self.player.update(dt / moves, self.collide)

    #issue 68
    def collide(self, position: tuple, height: int) -> tuple:
        """Checks to see if the player at the given `position` and `height`
        is colliding with any blocks in the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position to check for collisions at.
        height : int or float
            The height of the player.

        Returns
        -------
        position : tuple of len 3
            The new position of the player taking into account collisions.
        """
        # How much overlap with a dimension of a surrounding block you need to
        # have to count as a collision. If 0, touching terrain at all counts as
        # a collision. If .49, you sink into the ground, as if walking through
        # tall grass. If >= .5, you'll fall through the ground.
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
                    block_type = self.world.get(tuple(player_currnet_coords))
                    if block_type is None or self.can_pass_through_block(player_current_coords=tuple(player_currnet_coords)):
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.player.dy = 0
                    break
        return tuple(p)
    
    #issue 68
    def handle_adjust_vision(self, dx, dy):
        self.player.adjust_sight(dx, dy)

    #issue 68
    def handle_change_active_block(self, index):
        self.player.select_active_item(index)

    #issue 68
    def handle_speed_change(self, increase):
        if increase:
            self.player.speed_up()
        else:
            self.player.speed_down()

    #issue 68
    def handle_jump(self):
        self.player.jump()
    
    #issue 68
    def handle_flight_toggle(self):
        self.player.toggle_flight()

    #issue 68
    def handle_movement(self, forward, backward, left, right):
        def handle_movement_for_direction(direction, move, stop):
            if direction != 0:
                if direction == 1:
                    move()
                else:
                    stop()
        
        handle_movement_for_direction(forward, self.player.move_forward, self.player.stop_forward)
        handle_movement_for_direction(backward, self.player.move_backward, self.player.stop_backward)
        handle_movement_for_direction(left, self.player.move_left, self.player.stop_left)
        handle_movement_for_direction(right, self.player.move_right, self.player.stop_right)

