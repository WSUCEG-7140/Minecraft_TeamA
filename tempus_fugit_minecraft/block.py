class Block:
    """!
    @brief A class to represent a block in the game.
    @return An instance of the Block object.
    @see [trunk_texture](https://stock.adobe.com/au/images/texture-for-platformers-pixel-art-vector-brown-tree-trunk/91706199)
    @see [leaves_texture](https://www.planetminecraft.com/texture-pack/colored-spruce-leaves/)
    
    """
    __GRASS__ = None
    __SAND__ = None
    __BRICK__ = None
    __STONE__ = None
    __LIGHT_CLOUD__ = None
    __DARK_CLOUD__ = None
    __TREE_LEAVES__ = None
    __TREE_TRUNK__ = None

    @classmethod
    @property
    def GRASS(cls):
        """!
        @brief Returns a grass block
        @return The grass block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__GRASS__ is None:
            cls.__GRASS__ = Block("GRASS", ((1, 0), (0, 1), (0, 0)))
        return cls.__GRASS__
    
    @classmethod 
    @property
    def SAND(cls):
        """!
        @brief Returns a sand block
        @return The sand block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__SAND__ is None:
            cls.__SAND__ = Block("SAND", ((1, 1), (1, 1), (1, 1)))
        return cls.__SAND__

    @classmethod 
    @property
    def BRICK(cls):
        """!
        @brief Returns a brick block
        @return The brick block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__BRICK__ is None:
            cls.__BRICK__ = Block("BRICK", ((2, 0), (2, 0), (2, 0)))
        return cls.__BRICK__
    
    @classmethod 
    @property
    def STONE(cls):
        """!
        @brief Returns a stone block
        @return The stone block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__STONE__ is None: 
            cls.__STONE__ = Block("STONE", ((2, 1), (2, 1), (2, 1)), is_breakable=False, can_build_on=True)
        return cls.__STONE__
            
    @classmethod 
    @property
    def LIGHT_CLOUD(cls):
        """!
        @brief Returns a light cloud block
        @return The light cloud block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__LIGHT_CLOUD__ is None:
            cls.__LIGHT_CLOUD__ = Block("LIGHT_CLOUD", ((3, 0), (3, 0), (3, 0)), is_breakable=True, is_collidable=False, can_build_on=True)
        return cls.__LIGHT_CLOUD__

    @classmethod 
    @property
    def DARK_CLOUD(cls):
        """!
        @brief Returns a dark cloud block
        @return The dark cloud block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__DARK_CLOUD__ is None:
            cls.__DARK_CLOUD__ = Block("DARK_CLOUD", ((3, 1), (3, 1), (3, 1)), is_breakable=True, is_collidable=False, can_build_on=True)
        return cls.__DARK_CLOUD__
        
    @classmethod 
    @property
    def TREE_TRUNK(cls):
        """!
        @brief Returns a tree trunk block
        @return The tree trunk block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__TREE_TRUNK__ is None:
            cls.__TREE_TRUNK__ = Block("TREE_TRUNK", ((1, 2), (1, 2), (2, 2)), is_breakable=True, is_collidable=True, can_build_on=True)
        return cls.__TREE_TRUNK__

    @classmethod 
    @property
    def TREE_LEAVES(cls):
        """!
        @brief Returns a tree leaves block
        @return The tree leaves block
        @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
        """
        if cls.__TREE_LEAVES__ is None:
            cls.__TREE_LEAVES__ = Block("TREE_LEAVES", ((0, 2), (0, 2), (0, 2)), is_breakable=True, is_collidable=False, can_build_on=True)
        return cls.__TREE_LEAVES__    

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
