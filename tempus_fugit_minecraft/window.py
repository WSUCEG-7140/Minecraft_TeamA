import math
import sys

from pyglet import window, text, graphics
from pyglet.gl import *
from pyglet.window import key, mouse
from tempus_fugit_minecraft.utilities import *
from tempus_fugit_minecraft.model import Model
from tempus_fugit_minecraft.player import Player

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

if sys.version_info[0] >= 3:
    xrange = range

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

        # Which sector the player is currently in.
        self.sector = None

        # The crosshairs at the center of the screen.
        self.reticle = None

        # Convenience list of num keys.
        self.num_keys = [
            key._1, key._2, key._3, key._4, key._5,
            key._6, key._7, key._8, key._9, key._0]

        # Instance of the model that handles the world.
        self.model = Model()
        self.player = Player()

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
        sector = sectorize(self.player.position)
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
        speed = self.player.current_speed()
        d = dt * speed  # distance covered this tick.
        dx, dy, dz = self.player.get_motion_vector()
        # New position in space, before accounting for gravity.
        dx, dy, dz = dx * d, dy * d, dz * d
        # gravity
        if not self.player.flying:
            # Update your vertical speed: if you are falling, speed up until you
            # hit terminal velocity; if you are jumping, slow down until you
            # start falling.
            self.player.dy -= dt * self.player.GRAVITY
            self.player.dy = max(self.player.dy, -self.player.MAX_FALL_SPEED)
            dy += self.player.dy * dt
        # collisions
        x, y, z = self.player.position
        x, y, z = self.collide((x + dx, y + dy, z + dz), self.player.PLAYER_HEIGHT)
        self.player.position = (x, y, z)

    #issue57
    def collide(self, position: tuple, height: int) -> tuple:
        """!
        @brief Checks to see if the player at the given `position` and `height`
            is colliding with any blocks in the world.
        
        @details If position for cloud texture, pass through clouds.

        @param position The (x, y, z) position to check for collisions at.
        @param height The height of the player.

        @return position The new position of the player taking into account collisions.
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
                    if block_type is None or self.is_it_cloud_coordinates(player_current_coords=tuple(player_currnet_coords)):
                        continue
                    p[i] -= (d - pad) * face[i]
                    if face == (0, -1, 0) or face == (0, 1, 0):
                        # You are colliding with the ground or ceiling, so stop
                        # falling / rising.
                        self.player.dy = 0
                    break
        return tuple(p)
    
    
    #issue42
    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int) -> None:
        """!
        @brief Called when a mouse button is pressed. See pyglet docs for 
            button and modifier mappings.
        
        @details If right-click on non-clouds texture, add_block() is called. 
            Otherwise, the method is not called.
        
        @details If left-click on non-brick texture, remove_block() is called. 
            Otherwise, the method is not called.

        @param x, y The coordinates of the mouse click. Always center of 
            the screen if the mouse is captured.
        @param button Number representing mouse button that was clicked. 
            1 = left button, 4 = right button.
        @param modifiers Number representing any modifying keys that 
            were pressed when the mouse button was clicked.
        
        @return None
        """
        if self.paused:
            if self.within_label(x, y, self.resume_label):
                self.resume_game()
            elif self.within_label(x, y, self.quit_label):
                self.close()
        elif self.exclusive:
            vector = self.player.get_sight_vector()
            block, previous = self.model.hit_test(self.player.position, vector)
            if (button == mouse.RIGHT) or ((button == mouse.LEFT) and (modifiers & key.MOD_CTRL)):
                # ON OSX, control + left click = right click.
                if previous and block:
                    block_texture = self.model.world[block]
                    if not self.is_it_cloud_texture(block_texture):
                        self.model.add_block(previous, self.player.block)
                        
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

        self.player.adjust_sight(dx, dy)

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
            self.player.move_forward()
        elif symbol == key.S:
            self.player.move_backward()
        elif symbol == key.A:
            self.player.move_left()
        elif symbol == key.D:
            self.player.move_right()
        elif symbol == key.SPACE:
            self.player.jump()
        elif symbol == key.TAB:
            self.player.toggle_flight()
        elif symbol in self.num_keys:
            index = (symbol - self.num_keys[0]) % len(self.inventory)
            self.player.select_active_item(index)
        elif symbol == key.Q:
            self.player.speed_up()
        elif symbol == key.E:
            self.player.speed_down()

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
            self.player.stop_forward()
        elif symbol == key.S:
            self.player.stop_backward()
        elif symbol == key.A:
            self.player.stop_left()
        elif symbol == key.D:
            self.player.stop_right()

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
        x, y = self.player.rotation
        glRotatef(x, 0, 1, 0)
        glRotatef(-y, math.cos(math.radians(x)), 0, math.sin(math.radians(x)))
        x, y, z = self.player.position
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
        vector = self.player.get_sight_vector()
        block = self.model.hit_test(self.player.position, vector)[0]
        if block:
            x, y, z = block
            vertex_data = cube_vertices(x, y, z, 0.51)
            glColor3d(0, 0, 0)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            pyglet.graphics.draw(24, GL_QUADS, ('v3f/static', vertex_data))
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    def draw_label(self) -> None:
        """Draw the label in the top left of the screen."""
        x, y, z = self.player.position
        self.label.text = '%02d (%.2f, %.2f, %.2f) %d / %d' % (
            pyglet.clock.get_fps(), x, y, z,
            len(self.model._shown), len(self.model.world))
        self.label.draw()

    def draw_reticle(self) -> None:
        """Draw the crosshairs in the center of the screen."""
        glColor3d(0, 0, 0)
        self.reticle.draw(GL_LINES)
    
    
    #issue57
    def is_it_cloud_coordinates(self, player_current_coords):
        """!
        @brief Check if the block at the given palyer_current_coords is a cloud block.
        
        @param player_current_coords Current (x,y,z) corrdinates for the player.
        
        @return True if the coordinates correspond to a cloud block, False otherwise.
        """
        block_type = self.model.world.get(player_current_coords)
        return block_type in [LIGHT_CLOUD,DARK_CLOUD]
    
    #issue42
    def is_it_cloud_texture(self, texture):
        """!
        @brief Check if the texture is of type cloud.
        
        @param texture The texture that was clicked by the mouse left-button.
        
        @return True if the texture belong to clouds' textures, False otherwise.
        """
        return texture in [LIGHT_CLOUD,DARK_CLOUD]
