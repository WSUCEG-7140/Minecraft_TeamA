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
CLOUD_TYPE = [LIGHT_CLOUD , DARK_CLOUD]


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
    SECTOR_SIZE = 16  # Size of sectors used to ease block loading.

    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, 0, z
