from __future__ import division

import math
import random
import sys
import time
from collections import deque
from typing import Callable

from pyglet import image
from pyglet.gl import *
from pyglet.graphics import TextureGroup
from pyglet.window import key, mouse

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
TICKS_PER_SEC = 60
SECTOR_SIZE = 16  # Size of sectors used to ease block loading.

if sys.version_info[0] >= 3:
    xrange = range


def cube_vertices(x: float, y: float, z: float, n: float) -> list:
    """Return the vertices of the cube at position x, y, z with size 2*n.

    Parameters
    ----------
    x, y, z : float
        Coordinates of the cube's center.
    n : float
        Size of the cube.

    Returns
    -------
    vertices : list
        The vertices of the cube.
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]


def tex_coord(x: int, y: int, n=4) -> tuple:
    """Return the bounding vertices of the texture square.

    Parameters
    ----------
    x, y : int
        The x, y coordinates of the texture square.
    n : int
        The size of the texture atlas (default 4).

    Returns
    -------
    vertices : tuple
        The vertices of the texture square.
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top: tuple, bottom: tuple, side: tuple) -> list:
    """Return a list of the texture squares for the top, bottom and side.

    Parameters
    ----------
    top, bottom, side : tuple of len 2
        The x, y coordinates of the top left corner of the texture square.

    Returns
    -------
    tex_coords : list
        The texture coordinates for the top, bottom and side.
    """
    top = tex_coord(*top)
    bottom = tex_coord(*bottom)
    side = tex_coord(*side)
    result = []
    result.extend(top)
    result.extend(bottom)
    result.extend(side * 4)
    return result


TEXTURE_PATH = 'assets/texture.png'

GRASS = tex_coords((1, 0), (0, 1), (0, 0))
SAND = tex_coords((1, 1), (1, 1), (1, 1))
BRICK = tex_coords((2, 0), (2, 0), (2, 0))
STONE = tex_coords((2, 1), (2, 1), (2, 1))
LIGHT_CLOUD = tex_coords((3, 0), (3, 0), (3, 0))
DARK_CLOUD = tex_coords((3, 1), (3, 1), (3, 1))

FACES = [
    (0, 1, 0),
    (0, -1, 0),
    (-1, 0, 0),
    (1, 0, 0),
    (0, 0, 1),
    (0, 0, -1),
]


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
    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, 0, z


class Model(object):
    """A 3D world model for block-based rendering."""

    def __init__(self) -> None:
        # A Batch is a collection of vertex lists for batched rendering.
        self.batch = pyglet.graphics.Batch()

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
        self.sectors = {}

        # Simple function queue implementation. The queue is populated with
        # _show_block() and _hide_block() calls
        self.queue = deque()

        self._initialize()

    def _initialize(self) -> None:
        """Initialize the world by placing all the blocks."""
        n = 80  # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer stone and grass everywhere.
                self.add_block((x, y - 2, z), GRASS, immediate=False)
                self.add_block((x, y - 3, z), STONE, immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        self.add_block((x, y + dy, z), STONE, immediate=False)

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
                        self.add_block((x, y, z), t, immediate=False)
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
        """Add a block with the given `texture` and `position` to the world.

        Parameters
        ----------
        position : tuple of len 3
            The (x, y, z) position of the block to add.
        texture : list of len 3
            The coordinates of the texture squares. Use `tex_coords()` to
            generate.
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

    @staticmethod
    def generate_clouds_positions(world_size: int, num_of_clouds=250) -> list:
        """Generate the position of the clouds on the sky.

        Parameters
        ----------
        world_size : int
            1/2 size of the world.
        num_of_clouds : int
            Default clouds to be generated = 250

        Returns
        -------
        clouds : list of lists
            Each inner list represents a set of cloud blocks.
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


    def place_cloud_blocks(self, clouds):
        """
        represent each cloud block's coordinates with a cloud block in the sky.

        Input: clouds: list of lists; each inner list is a set of cloud block's coordinates.

        output: draw a cloud block with its corresponding coordinates.
        """
        cloud_types = [LIGHT_CLOUD,DARK_CLOUD]
        for cloud in clouds:
            cloud_color = random.choice(cloud_types)
            for x,y,z in cloud:
                self.add_block((x,y,z) , cloud_color , immediate=False)


class Window(pyglet.window.Window):
    """A window class for a game environment.

    This class extends the `pyglet.window.Window` class and provides functionality
    for a game environment. It handles player movement, collisions, rendering,
    and user input.
    """

    def __init__(self, *args, **kwargs):
        super(Window, self).__init__(*args, **kwargs)

        # Whether the window exclusively captures the mouse.
        self.exclusive = False

        self.walking_speed = 5
        self.FLYING_SPEED = 15

        self.GRAVITY = 20.0
        self.MAX_JUMP_HEIGHT = 1.0  # About the height of a block.
        # To derive the formula for calculating jump speed, first solve
        #    v_t = v_0 + a * t
        # for the time at which you achieve maximum height, where a is the acceleration
        # due to gravity and v_t = 0. This gives:
        #    t = - v_0 / a
        # Use t and the desired MAX_JUMP_HEIGHT to solve for v_0 (jump speed) in
        #    s = s_0 + v_0 * t + (a * t^2) / 2
        self.JUMP_SPEED = math.sqrt(2 * self.GRAVITY * self.MAX_JUMP_HEIGHT)
        self.TERMINAL_VELOCITY = 50

        self.PLAYER_HEIGHT = 2

        # When flying gravity has no effect and speed is increased.
        self.flying = False

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

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # Velocity in the y (upward) direction.
        self.dy = 0

        # A list of blocks the player can place. Hit num keys to cycle.
        self.inventory = [BRICK, GRASS, SAND]

        # The current block the user can place. Hit num keys to cycle.
        self.block = self.inventory[0]

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model()

        self.paused = False

        # The label that is displayed in the top left of the canvas.
        self.label = pyglet.text.Label(
            text='',
            font_name='Arial',
            font_size=18,
            x=10,
            y=self.height - 10,
            anchor_x='left',
            anchor_y='top',
            color=(0, 0, 0, 255)
        )
        self.pause_label = pyglet.text.Label(
            text="Paused",
            font_name="Arial",
            font_size=36,
            width=100,
            height=30,
            x=self.width // 2,
            y=self.height // 2,
            anchor_x="center",
        )
        self.resume_label = pyglet.text.Label(
            text="Resume",
            font_name="Arial",
            font_size=18,
            width=90,
            height=35,
            x=self.width // 2,
            y=self.height // 2 - 45,
            anchor_x="center",
        )
        self.quit_label = pyglet.text.Label(
            text="Quit",
            font_name="Arial",
            font_size=18,
            width=50,
            height=35,
            x=self.width // 2,
            y=self.height // 2 - 90,
            anchor_x="center",
        )

        # This call schedules the `update()` method to be called
        # TICKS_PER_SEC. This is the main game event loop.
        pyglet.clock.schedule_interval(self.update, 1.0 / TICKS_PER_SEC)

    def set_exclusive_mouse(self, exclusive: bool) -> None:
        """If `exclusive` is True, the game will capture the mouse, if False
        the game will ignore the mouse.

        Parameters
        ----------
        exclusive : bool
            Whether the game will capture the mouse or not.
        """
        super(Window, self).set_exclusive_mouse(exclusive)
        self.exclusive = exclusive

    def get_sight_vector(self) -> tuple:
        """Returns the current line of sight vector indicating the direction the player is looking."""
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
        """Returns the current motion vector indicating the velocity of the player.

        Returns
        -------
        vector : tuple of len 3
            Tuple containing the velocity in x, y, and z respectively.
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

    def update(self, dt: float) -> None:
        """This method is scheduled to be called repeatedly by the pyglet clock.

        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """
        if self.paused:
            return

        self.model.process_queue()
        sector = sectorize(self.position)
        if sector != self.sector:
            self.model.change_sectors(self.sector, sector)
            if self.sector is None:
                self.model.process_entire_queue()
            self.sector = sector
        m = 8
        dt = min(dt, 0.2)
        for _ in xrange(m):
            self._update(dt / m)

    def _update(self, dt: float) -> None:
        """Private implementation of the `update()` method. This is where most
        of the motion logic lives, along with gravity and collision detection.

        Parameters
        ----------
        dt : float
            The change in time since the last call.
        """
        # walking
        speed = self.FLYING_SPEED if self.flying else self.walking_speed
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
            self.dy = max(self.dy, -self.TERMINAL_VELOCITY)
            dy += self.dy * dt
        # collisions
        x, y, z = self.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), self.PLAYER_HEIGHT)
        self.position = (x, y, z)

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
                    block_type = self.model.world.get(tuple(player_currnet_coords))
                    if block_type is None or self.pass_through_clouds(player_current_coords=tuple(player_currnet_coords)):
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.dy = 0
                    break
        return tuple(p)
    

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """Called when a mouse button is pressed. See pyglet docs for button
        and modifier mappings.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        button : int
            Number representing mouse button that was clicked. 1 = left button,
            4 = right button.
        modifiers : int
            Number representing any modifying keys that were pressed when the
            mouse button was clicked.
        """
        if self.paused:
            if self.within_label(x, y, self.resume_label):
                self.resume_game()
            elif self.within_label(x, y, self.quit_label):
                self.close()
        elif self.exclusive:
            vector = self.get_sight_vector()
            block, previous = self.model.hit_test(self.position, vector)
            if (button == mouse.RIGHT) or ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous:
                    self.model.add_block(previous, self.block)
            elif button == pyglet.window.mouse.LEFT and block:
                texture = self.model.world[block]
                if texture != STONE:
                    self.model.remove_block(block)

    @staticmethod
    def within_label(x: int, y: int, label: pyglet.text.Label) -> bool:
        """Returns True if the given (x, y) coordinates are within the given
        label.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click.

        label : pyglet.text.Label
            The label to check against.
        """
        x_within_range = label.x - label.width // 2 <= x <= label.x + label.width // 2
        y_within_range = label.y <= y <= label.y + label.height // 2
        return x_within_range and y_within_range

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
        """Called when the player moves the mouse.

        Parameters
        ----------
        x, y : int
            The coordinates of the mouse click. Always center of the screen if
            the mouse is captured.
        dx, dy : int
            The movement of the mouse.
        """
        if self.paused:
            if self.within_label(x, y, self.resume_label) or self.within_label(x, y, self.quit_label):
                self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_HAND))
            else:
                self.set_mouse_cursor(self.get_system_mouse_cursor(self.CURSOR_DEFAULT))

            for label in [self.resume_label, self.quit_label]:
                if self.within_label(x, y, label):
                    label.color = (150, 150, 150, 255)  # grey
                else:
                    label.color = (255, 255, 255, 255)  # white
                label.draw()

        # Only rotate the camera if the mouse is captured.
        if not self.exclusive or self.paused:
            return

        m = 0.15
        x, y = self.rotation
        x, y = x + dx * m, y + dy * m
        y = max(-90, min(90, y))
        self.rotation = (x, y)

    def on_key_press(self, symbol: int, modifiers: int) -> None:
        """Called when the player presses a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """
        if symbol == key.ESCAPE:
            if self.paused:
                self.resume_game()
            else:
                self.pause_game()

        if self.paused:
            return

        if symbol == key.W:
            self.strafe[0] -= 1
        elif symbol == key.S:
            self.strafe[0] += 1
        elif symbol == key.A:
            self.strafe[1] -= 1
        elif symbol == key.D:
            self.strafe[1] += 1
        elif symbol == key.SPACE:
            if self.dy == 0:
                self.dy = self.JUMP_SPEED
        elif symbol == key.TAB:
            self.flying = not self.flying
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.block = self.inventory[index]
        elif symbol == key.UP:
            self.speed_up()
        elif symbol == key.DOWN:
            self.speed_down()

    def speed_up(self) -> None:
        """Increases the walking speed of the player."""
        if self.walking_speed <= 15:
            self.walking_speed += 5
    def speed_down(self):
        if self.walking_speed > 5:
            self.walking_speed -= 5

    def pause_game(self) -> None:
        """Pauses the game and bring up the pause menu."""
        self.paused = True
        self.set_mouse_visible(True)
        self.set_exclusive_mouse(False)

    def resume_game(self) -> None:
        """Resumes the game by restoring the game window to its original state."""
        self.paused = False
        self.set_exclusive_mouse(True)

    def on_key_release(self, symbol: int, modifiers: int) -> None:
        """Called when the player releases a key. See pyglet docs for key
        mappings.

        Parameters
        ----------
        symbol : int
            Number representing the key that was pressed.
        modifiers : int
            Number representing any modifying keys that were pressed.
        """
        if symbol == key.W:
            self.strafe[0] += 1
        elif symbol == key.S:
            self.strafe[0] -= 1
        elif symbol == key.A:
            self.strafe[1] += 1
        elif symbol == key.D:
            self.strafe[1] -= 1

    def on_resize(self, width: int, height: int) -> None:
        """Called when the window is resized to a new `width` and `height`.

        Parameters
        ----------
        width : int
            The new width of the window.
        height : int
            The new height of the window.
        """
        # label
        self.label.y = height - 10
        # reticle
        if self.reticle:
            self.reticle.delete()
        x, y = self.width // 2, self.height // 2
        n = 10
        self.reticle = pyglet.graphics.vertex_list(
            4,
            ('v2i', (x - n, y, x + n, y, x, y - n, x, y + n))
        )

        if self.paused:
            self.center_labels(width, height)

    def center_labels(self, width: int, height: int) -> None:
        """Center the labels when the window size changes.

        Parameters
        ----------
        width : int
            The new width of the window.
        height : int
            The new height of the window.
        """
        self.pause_label.x = self.resume_label.x = self.quit_label.x = width // 2
        self.pause_label.y = height // 2
        self.resume_label.y = height // 2 - 45
        self.quit_label.y = height // 2 - 90

    def set_2d(self) -> None:
        """Configure OpenGL to draw in 2d."""
        width, height = self.get_size()
        glDisable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, max(1, width), 0, max(1, height), -1, 1)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def set_3d(self) -> None:
        """Configure OpenGL to draw in 3d."""
        width, height = self.get_size()
        glEnable(GL_DEPTH_TEST)
        viewport = self.get_viewport_size()
        glViewport(0, 0, max(1, viewport[0]), max(1, viewport[1]))
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(65.0, width / float(height), 0.1, 60.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x, y = self.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.position
        glTranslatef(-x, -y, -z)

    def on_draw(self):
        """Called by pyglet to draw the canvas."""
        self.clear()
        self.set_3d()
        glColor3d(1, 1, 1)
        self.model.batch.draw()
        self.draw_focused_block()
        self.set_2d()
        self.draw_label()
        self.draw_reticle()

        if self.paused:
            self.draw_pause_menu()

    def draw_pause_menu(self) -> None:
        """Draws the components of the pause menu, including the background, the pause text, and the resume and quit
        buttons.
        """
        glPushMatrix()
        glLoadIdentity()
        glMatrixMode(GL_PROJECTION)
        glPushMatrix()
        glLoadIdentity()
        glOrtho(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT, -1, 1)
        glDisable(GL_DEPTH_TEST)

        # Transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        background_color = (0, 0, 0, 0.8)
        pyglet.graphics.draw(
            4,
            GL_QUADS,
            ('v2i', (0, 0, WINDOW_WIDTH, 0, WINDOW_WIDTH, WINDOW_HEIGHT, 0, WINDOW_HEIGHT)),
            ('c4f', background_color * 4)
        )

        glEnable(GL_DEPTH_TEST)
        glPopMatrix()
        glMatrixMode(GL_MODELVIEW)
        glPopMatrix()

        self.pause_label.draw()
        self.resume_label.draw()
        self.quit_label.draw()

    def draw_focused_block(self) -> None:
        """ Draw black edges around the block that is currently under the crosshairs."""
        vector = self.get_sight_vector()
        block = self.model.hit_test(self.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self) -> None:
        """Draw the label in the top left of the screen."""
        x, y, z = self.position
        self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world))
        self.label.draw()

    def draw_reticle(self) -> None:
        """Draw the crosshairs in the center of the screen."""
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
    
    
    def pass_through_clouds(self, player_current_coords):
        """
        check if the block at the given palyer_current_coords is a cloud block
        
        Input
        -----
            player_current_coords: current (x,y,z) corrdinates for the player
        
        Output
        ------
            True: if the coords corresponding to a cloud block.
            False: otherwise.
        """
        block_type = self.model.world.get(player_current_coords)
        return block_type in [LIGHT_CLOUD,DARK_CLOUD]


def setup_fog() -> None:
    """Configure the OpenGL fog properties."""
    # Enable fog. Fog "blends a fog color with each rasterized pixel fragment's
    # post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start and end,
    # the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup() -> None:
    """Basic OpenGL configuration."""
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets that aren't
    # visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST (nearest
    # in Manhattan distance) to the specified texture coordinates. GL_NEAREST
    # "is generally faster than GL_LINEAR, but it can produce textured images
    # with sharper edges because the transition between texture elements is not
    # as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main() -> None:
    window = Window(
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        caption='Tempus Fugit Minecraft',
        resizable=True
    )
    # Hide the mouse cursor and prevent the mouse from leaving the window.
    window.set_exclusive_mouse(True)
    setup()
    pyglet.app.run()


if __name__ == '__main__':
    main()
