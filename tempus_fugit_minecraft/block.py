class Block:
    """!
    @brief A class to represent a block in the game.
    @return An instance of the Block object.
    """
    def __init__(self, name: str, texture_coordinates: tuple, is_breakable: bool = True, is_collidable: bool = True,
                 can_build_on: bool = True) -> None:
        """!
        @brief Initializes an instance of a Block class
        @param name The name of the block.
        @param texture_coordinates A tuple of pairs of indices on the texture map file of where the texture is.
        @param is_breakable A flag indicating if this type of block is breakable by the player. Default is True.
        @param is_collidable A flag indicating if this type of block will prevent the player from moving through it.
            Default is True.
        @param can_build_on A flag indicating if the player can place blocks off of this block type. Default is True.
        @return An instance of the Block class
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        self.name = name
        self.texture_coordinates = tex_coords(*texture_coordinates)
        self.is_breakable = is_breakable
        self.is_collidable = is_collidable
        self.can_build_on = can_build_on


def tex_coord(x: int, y: int, n=4) -> tuple:
    """!
    @brief Return the bounding vertices of the texture square.
    @param x The x coordinate of the texture square
    @param y The y coordinate of the texture square
    @param n The size of the texture atlas. Default is 4.
    @return A tuple with the vertices of the texture square.
    @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
    """
    m = 1.0 / n
    dx = x * m
    dy = y * m
    return dx, dy, dx + m, dy, dx + m, dy + m, dx, dy + m


def tex_coords(top: tuple, bottom: tuple, side: tuple) -> list:
    """!
    @brief Return a list of the texture squares for the top, bottom and side.
    @param top A tuple of coordinates on which the top texture of the block is.
    @param bottom A tuple of coordinates on which the bottom texture of the block is.
    @param side A tuple of coordinates on which the side texture of the block is.
    @return The texture coordinates for the top, bottom, and sites of a block in a list.
    @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
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
LIGHT_CLOUD = Block("LIGHT_CLOUD", ((3, 0), (3, 0), (3, 0)), is_breakable=True, is_collidable=False, can_build_on=True)
DARK_CLOUD = Block("DARK_CLOUD", ((3, 1), (3, 1), (3, 1)), is_breakable=False, is_collidable=False, can_build_on=False)
TREE_TRUNK = Block("TREE_TRUNK", ((1, 2), (1, 2), (2, 2)), is_breakable=True, is_collidable=True, can_build_on=True)
TREE_LEAVES = Block("TREE_LEAVES", ((0, 2), (0, 2), (0, 2)), is_breakable=True, is_collidable=False, can_build_on=True)