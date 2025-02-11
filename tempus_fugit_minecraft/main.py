from __future__ import division

from pyglet import app
from pyglet.gl import *
from tempus_fugit_minecraft.window import Window, WINDOW_WIDTH, WINDOW_HEIGHT


def setup_fog() -> None:
    """!
    @brief Configure the OpenGL fog properties.
    """
    # Enable fog. Fog "blends a fog color with each rasterized pixel
    # fragment's post-texturing color."
    glEnable(GL_FOG)
    # Set the fog color.
    glFogfv(GL_FOG_COLOR, (GLfloat * 4)(0.5, 0.69, 1.0, 1))
    # Say we have no preference between rendering speed and quality.
    glHint(GL_FOG_HINT, GL_DONT_CARE)
    # Specify the equation used to compute the blending factor.
    glFogi(GL_FOG_MODE, GL_LINEAR)
    # How close and far away fog starts and ends. The closer the start
    # and end, the denser the fog in the fog range.
    glFogf(GL_FOG_START, 20.0)
    glFogf(GL_FOG_END, 60.0)


def setup() -> None:
    """!
    @brief Basic OpenGL configuration.
    """
    # Set the color of "clear", i.e. the sky, in rgba.
    glClearColor(0.5, 0.69, 1.0, 1)
    # Enable culling (not rendering) of back-facing facets -- facets
    # that aren't visible to you.
    glEnable(GL_CULL_FACE)
    # Set the texture minification/magnification function to GL_NEAREST
    # (nearest in Manhattan distance) to the specified texture
    # coordinates. GL_NEAREST "is generally faster than GL_LINEAR, but
    # it can produce textured images with sharper edges because the
    # transition between texture elements is not as smooth."
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    setup_fog()


def main() -> None:
    """!
    @brief The main method
    """
    window = Window(
        width=WINDOW_WIDTH,
        height=WINDOW_HEIGHT,
        caption='Tempus Fugit Minecraft',
        resizable=True
    )
    window.set_exclusive_mouse(True)  # Hide the mouse cursor and prevent the mouse from leaving the window.
    setup()
    app.run()


if __name__ == '__main__':
    main()
