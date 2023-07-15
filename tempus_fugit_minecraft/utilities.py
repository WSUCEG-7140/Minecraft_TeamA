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

TICKS_PER_SEC = 60
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
