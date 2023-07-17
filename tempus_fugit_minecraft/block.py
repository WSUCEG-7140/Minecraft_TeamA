class Block:
    def __init__(self, name: str, texture_coordinates: tuple, is_breakable : bool = True, is_collidable : bool = True, can_build_on : bool = True) -> None:
        self.name = name
        self.texture_coordinates = tex_coords(*texture_coordinates)
        self.is_breakable = is_breakable
        self.is_collidable = is_collidable
        self.can_build_on = can_build_on

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

GRASS = Block("GRASS", ((1, 0), (0, 1), (0, 0)))
SAND = Block("SAND", ((1, 1), (1, 1), (1, 1)))
BRICK = Block("BRICK", ((2, 0), (2, 0), (2, 0)))
STONE = Block("STONE", ((2, 1), (2, 1), (2, 1)), is_breakable=False, can_build_on=True)
LIGHT_CLOUD = Block("LIGHT_CLOUD", ((3, 0), (3, 0), (3, 0)), is_breakable=False, is_collidable=False, can_build_on=False)
DARK_CLOUD = Block("DARK_CLOUD", ((3, 1), (3, 1), (3, 1)), is_breakable=False, is_collidable=False, can_build_on=False)