import random
import sys
from typing import Dict, TypeAlias

from tempus_fugit_minecraft.block import Block

Position: TypeAlias = tuple[int, int, int]
Map: TypeAlias = Dict[Position, Block]

if sys.version_info[0] >= 3:
    xrange = range


def normalize(position: tuple) -> Position:
    """!
    @brief Accepts `position` of arbitrary precision and returns the block containing that position.
    @param position : tuple of len 3
    @return block_position : tuple of ints of len 3
    """
    x, y, z = position
    x, y, z = (int(round(x)), int(round(y)), int(round(z)))
    return x, y, z


def sectorize(position: tuple) -> tuple:
    """!
    @brief Returns a tuple representing the sector for the given `position`.
    @param position : tuple of len 3
    @return sector : tuple of len 3
    """
    SECTOR_SIZE_IN_BLOCKS = 16  # Size of sectors used to ease block loading.

    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE_IN_BLOCKS, y // SECTOR_SIZE_IN_BLOCKS, z // SECTOR_SIZE_IN_BLOCKS
    return x, 0, z


class World:
    """!
    @brief A collection of functions to generate the structure of a 3D world
    """
    WIDTH_IN_BLOCKS = 320
    WIDTH_FROM_ORIGIN_IN_BLOCKS = WIDTH_IN_BLOCKS // 2

    @staticmethod
    def generate_base_layer() -> list[tuple[Block, Position]]:
        """!
        @brief Generate the base layer of the world
        @return a list of pairs of blocks and their positions
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        blockList = []
        step_size_in_block = 1
        y_hight_in_block = 0
        for x in xrange(-World.WIDTH_FROM_ORIGIN_IN_BLOCKS, World.WIDTH_FROM_ORIGIN_IN_BLOCKS + 1, step_size_in_block):
            for z in xrange(-World.WIDTH_FROM_ORIGIN_IN_BLOCKS, World.WIDTH_FROM_ORIGIN_IN_BLOCKS + 1, step_size_in_block):
                # create a layer stone and grass everywhere.
                blockList.append((Block.GRASS, (x, y_hight_in_block - 2, z)))
                blockList.append((Block.STONE, (x, y_hight_in_block - 3, z)))
                if x in (-World.WIDTH_FROM_ORIGIN_IN_BLOCKS, World.WIDTH_FROM_ORIGIN_IN_BLOCKS) or z in (-World.WIDTH_FROM_ORIGIN_IN_BLOCKS, World.WIDTH_FROM_ORIGIN_IN_BLOCKS):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        blockList.append((Block.STONE, (x, y_hight_in_block + dy, z)))
        return blockList

    # is responsible for generating a number of hills within the world. We start by setting up a list to hold all of the hills, and a value 'game_margin' which represents the 
    # maximum possible distance a hill can be from the center of the world in the x and z directions.
    @staticmethod
    def generate_hills(world_size_in_blocks=WIDTH_FROM_ORIGIN_IN_BLOCKS, num_hills=int(WIDTH_FROM_ORIGIN_IN_BLOCKS * 1.5)) -> list[list[tuple[Block, Position]]]:
        """!
        @brief this function generates a group of randomly positioned hills strewn around the world
        @param world_size_in_blocks : The world size (default: world_size_in_blocks)
        @param num_hills : The number of hills generated (default: 1.5x world_size_in_blocks)
        @return :  a list of lists of pairs of blocks and positions that represent a collection of hills
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        hills = []
        
        # game_margin is used to set the limit for where clouds can be placed in the x and z directions.
        game_margin = world_size_in_blocks - 10
        
        # for the number of hills we want to create, we generate a hill at a random x and z position within our world bounds, and then add that hill to our list of hills.
        for _ in xrange(num_hills):
            hill_center_x_coordinate_in_model = random.randint(-game_margin, game_margin)
            hill_center_z_coordinate_in_model = random.randint(-game_margin, game_margin)
            hill = World.generate_hill(hill_center_x_coordinate_in_model, hill_center_z_coordinate_in_model)
            hills.append(hill)
        return hills

    @staticmethod
    def generate_hill(hill_center_x_coordinate_in_model: int, hill_center_z_coordinate_in_model: int) -> list[tuple[Block, Position]]:
        """!
        @brief this function generates a single hill
        @param hill_center_x_coordinate_in_model Represents the x coordinate center of the hill
        @param hill_center_z_coordinate_in_model Represents the z coordinate center of the hill
        @return a list of pairs of blocks and positions that represent a hill
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        base = -1  # base of the hill
        taperRate = 1  # how quickly to taper off the hills
        height = random.randint(1, 6)  # height of the hill
        sideLength = random.randint(4, 8)  # 2 * s is the side length of the hill
        block = random.choice([Block.GRASS, Block.SAND, Block.BRICK])
        hill = []
        for y in xrange(base, base + height):
            for x in xrange(hill_center_x_coordinate_in_model - sideLength, hill_center_x_coordinate_in_model + sideLength + 1):
                for z in xrange(hill_center_z_coordinate_in_model - sideLength, hill_center_z_coordinate_in_model + sideLength + 1):
                    if (x - hill_center_x_coordinate_in_model) ** 2 + (z - hill_center_z_coordinate_in_model) ** 2 > (sideLength + 1) ** 2:
                        continue
                    if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                        continue
                    hill.append((block, (x, y, z)))
            sideLength -= taperRate  # decrement side length so hills taper off
        return hill

    # generate_trees() function is responsible for creating a specified 
    # number of trees in the game.
    @staticmethod
    def generate_trees(model, num_trees=int((WIDTH_FROM_ORIGIN_IN_BLOCKS * 3.125))) -> list[list[tuple[Block, Position]]]:
        """!
        @brief Generate trees' (trunks and leaves) positions.
        @details single_tree is a list contains 2 lists of coordinates: list of trunks, and list of leaves.
        @details list trees appends each single_tree list.
        @details the trees are set to be built on Block.SAND and Block.GRASS only.
        @param num_trees Number of clouds (default is "world_size_in_blocks * 3.125").
        @return a list of lists of pairs of block type and positions that represent a collection of trees
        @see [Issue#80](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/80)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        # The function first defines a list of possible locations for 
        # trees to grow.
        # First, it lists all the grass blocks in the ground level.
        suggested_places_for_trees = []
        trees = []
        grass_list = [coords for coords , block in model.world.items() if block == Block.GRASS and coords[1]<=0]
        min_grass_level = min(ground[1] for ground in grass_list)
        ground_grass_list = [ground for ground in grass_list if ground[1] == min_grass_level]

        # Then, Among this list, it finds all the grass blocks that do not have any blocks above them. add those items to a different list.
        # The item in the list is a tuple of (x, y, z) coordinate of the grass blocks located at the ground level, with nothing above them.
        for coords in ground_grass_list:
            x,y,z = coords
            does_not_grass_have_block_above_it = all([(x, y+j, z) not in model.world for j in range(1,10)])
            if does_not_grass_have_block_above_it:
                suggested_places_for_trees.append(coords)

        # The function then randomly selects a location from this list and removes it so that no two trees are created at the same location. 
        # It then calls generate_single_tree() to create a tree at this location.
        for _ in range(num_trees):
            if suggested_places_for_trees:
                base_x, base_y, base_z = random.choice(suggested_places_for_trees)
                suggested_places_for_trees.remove((base_x, base_y, base_z))
                single_tree = World.generate_single_tree(base_x, base_y+1, base_z, trunk_height=5)
                trees.append(single_tree)
            else:
                break
        return trees
    
    # generate_single_tree() function creates a single tree at a specified location.
    @staticmethod
    def generate_single_tree(x, y, z, trunk_height=4) -> list[tuple[Block, Position]]:
        """!
        @brief represent trees' components.
        @details Tree components are Trunks and Leaves.
        @details The function returns 2 lists: list of trunks, list of leaves.
        @param x : x-coordinate of the position of the tree to be built at.
        @param y : y-coordinate of the position of the tree to be built at.
        @param z : z-coordinate of the position of the tree to be built at.
        @param trunk_height Number of trunks (stems) in the tree (default=4).
        @return a single list of pairs of block type and positions that represent a tree
        @see [Issue#80](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/80)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        # The tree consists of a trunk and leaves. The trunk is a block that leaves are built on it, (default number of trunks = 4).
        # The leaves are leaves blocks on top of the trunk.
        tree = []

        # Create trunks
        for stem in range(trunk_height):
            position = (x, y + stem, z)
            tree.append((Block.TREE_TRUNK, position))

        # Create leaves
        for dx in range(-2,3):
            for dy in range(0,3):
                for dz in range(-2,3):
                    position = (x + dx, y + trunk_height + dy, z + dz)
                    tree.append((Block.TREE_LEAVES, position))
        return tree

    @staticmethod
    def generate_clouds(world_size_in_blocks:int=WIDTH_FROM_ORIGIN_IN_BLOCKS, num_of_clouds=int((WIDTH_FROM_ORIGIN_IN_BLOCKS * 3.75))) -> list[list[tuple[Block, Position]]]:
        """!
        @brief Generate sky cloud positions.
        @param world_size_in_blocks Half the world's size.
        @param num_of_clouds Number of clouds (default is "world_size_in_blocks * 3.75").
        @return clouds list of lists representing cloud block types and positions.
        @see [Issue#20](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/20)
        @see [Issue#28](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/28)
        @see [Issue#44](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/44)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        # game_margin is used to set the limit for where clouds can be placed in the x and z directions.
        game_margin = world_size_in_blocks
        
        # clouds list will be storing generated clouds coordinates (x, y, z)
        clouds = list()
        
        # creating positions for clouds based on the specified value in num_of_clouds
        for _ in xrange(num_of_clouds):
            # The cloud's position in the x and z dimensions are randomly chosen within the game_margin.
            cloud_center_x = random.randint(-game_margin, game_margin)
            cloud_center_z = random.randint(-game_margin, game_margin)
            
            # while the y coordinate is randomly chosen between range of predefined values.
            cloud_center_y = random.choice([18,20,22,24,26])
            
            # 2*s is the side length of the cloud from the center. It is randomly chosen to provide different size of clouds.
            s = random.randint(3, 6)

            # A single_cloud is a tuple of (cloud_color,position)
            single_cloud = World.generate_single_cloud(cloud_center_x, cloud_center_y, cloud_center_z, s)

            clouds.append(single_cloud)
        return clouds

    # This function's goal is to generate the coordinates of all the blocks in a single cloud
    @staticmethod
    def generate_single_cloud(cloud_center_x, cloud_center_y, cloud_center_z,s) -> list[tuple[Block, Position]]:
        """!
        @brief generate a single cloud (list of cloud blocks).
        @param cloud_center_x Represents the x-coordinate center of the cloud.
        @param cloud_center_y Represents the y-coordinate (height) center of the cloud.
        @param cloud_center_z Represents the z-coordinate center of the cloud.
        @param s represent number of blocks drawn from center - goes in each direction around the center.
        @return single_cloud A list that contains pairs of blocks and positions that represent a cloud. 
        @see [Issue#20](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/20)
        @see [Issue#28](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/28)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        single_cloud = []
        
        # Iterate over the x and z coordinates around the cloud's center (s)
        cloud_color = random.choice([Block.LIGHT_CLOUD, Block.DARK_CLOUD])
        for x in xrange(cloud_center_x - s, cloud_center_x + s + 1):
                for z in xrange(cloud_center_z - s, cloud_center_z + s + 1):
                    if (x - cloud_center_x) ** 2 + (z - cloud_center_z) ** 2 > (s + 1) ** 2:
                        continue
                    position = (x, cloud_center_y, z)
                    single_cloud.append((cloud_color, position))
        return single_cloud
