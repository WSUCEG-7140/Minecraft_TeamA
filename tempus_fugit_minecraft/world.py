import random
import sys
from typing import Dict, TypeAlias

from tempus_fugit_minecraft.block import (BRICK, DARK_CLOUD, GRASS, LIGHT_CLOUD, SAND, STONE, TREE_LEAVES, TREE_TRUNK, 
                                          Block)
from tempus_fugit_minecraft.utilities import WORLD_SIZE

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
    SECTOR_SIZE = 16  # Size of sectors used to ease block loading.

    x, y, z = normalize(position)
    x, y, z = x // SECTOR_SIZE, y // SECTOR_SIZE, z // SECTOR_SIZE
    return x, 0, z


class World:
    """!
    @brief A collection of functions to generate the structure of a 3D world
    """
    @staticmethod
    def generate_base_layer() -> list[tuple[Block, Position]]:
        """!
        @brief Generate the base layer of the world
        @return a list of pairs of blocks and their positions
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        blockList = []
        s = 1  # step size
        y = 0  # initial y height
        for x in xrange(-WORLD_SIZE, WORLD_SIZE + 1, s):
            for z in xrange(-WORLD_SIZE, WORLD_SIZE + 1, s):
                # create a layer stone and grass everywhere.
                blockList.append((GRASS, (x, y - 2, z)))
                blockList.append((STONE, (x, y - 3, z)))
                if x in (-WORLD_SIZE, WORLD_SIZE) or z in (-WORLD_SIZE, WORLD_SIZE):
                    # create outer walls.
                    for dy in xrange(-2, 3):
                        blockList.append((STONE, (x, y + dy, z)))
        return blockList

    @staticmethod
    def generate_hills(world_size=WORLD_SIZE, num_hills=int(WORLD_SIZE * 1.5)) -> list[list[tuple[Block, Position]]]:
        """!
        @brief this function generates a group of randomly positioned hills strewn around the world
        @param world_size : The world size (default: WORLD_SIZE)
        @param num_hills : The number of hills generated (default: 1.5x WORLD_SIZE)
        @return :  a list of lists of pairs of blocks and positions that represent a collection of hills
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        hills = []
        o = world_size - 10
        for _ in xrange(num_hills):
            center_x = random.randint(-o, o)  # x position of the hill
            center_z = random.randint(-o, o)  # z position of the hill
            hill = World.generate_hill(center_x, center_z)
            hills.append(hill)
        return hills

    @staticmethod
    def generate_hill(center_x: int, center_z: int) -> list[tuple[Block, Position]]:
        """!
        @brief this function generates a single hill
        @param center_x Represents the x coordinate center of the hill
        @param center_z Represents the z coordinate center of the hill
        @return a list of pairs of blocks and positions that represent a hill
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        base = -1  # base of the hill
        taperRate = 1  # how quickly to taper off the hills
        height = random.randint(1, 6)  # height of the hill
        sideLength = random.randint(4, 8)  # 2 * s is the side length of the hill
        block = random.choice([GRASS, SAND, BRICK])
        hill = []
        for y in xrange(base, base + height):
            for x in xrange(center_x - sideLength, center_x + sideLength + 1):
                for z in xrange(center_z - sideLength, center_z + sideLength + 1):
                    if (x - center_x) ** 2 + (z - center_z) ** 2 > (sideLength + 1) ** 2:
                        continue
                    if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                        continue
                    hill.append((block, (x, y, z)))
            sideLength -= taperRate  # decrement side length so hills taper off
        return hill

    @staticmethod
    def generate_trees(model, num_trees=int((WORLD_SIZE * 3.125))) -> list[list[tuple[Block, Position]]]:
        """!
        @brief Generate trees' (trunks and leaves) positions.
        @details single_tree is a list contains 2 lists of coordinates: list of trunks, and list of leaves.
        @details list trees appends each single_tree list.
        @details the trees are set to be built on SAND and GRASS only.
        @param num_trees Number of clouds (default is "WORLD_SIZE * 3.125").
        @return a list of lists of pairs of block type and positions that represent a collection of trees
        @see [Issue#80](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/80)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        suggested_places_for_trees = []
        trees = []
        grass_list = [coords for coords , block in model.world.items() if block == GRASS and coords[1]<=0]
        min_grass_level = min(ground[1] for ground in grass_list)
        ground_grass_list = [ground for ground in grass_list if ground[1] == min_grass_level]

        for coords in ground_grass_list:
            x,y,z = coords
            does_not_grass_have_block_above_it = all([(x, y+j, z) not in model.world for j in range(1,10)])
            if does_not_grass_have_block_above_it:
                suggested_places_for_trees.append(coords)

        for _ in range(num_trees):
            if suggested_places_for_trees:
                base_x, base_y, base_z = random.choice(suggested_places_for_trees)
                suggested_places_for_trees.remove((base_x, base_y, base_z))
                single_tree = World.generate_single_tree(base_x, base_y+1, base_z, trunk_height=5)
                trees.append(single_tree)
            else:
                break
        return trees
    
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
        tree = []

        # Create trunks
        for stem in range(trunk_height):
            position = (x, y + stem, z)
            tree.append((TREE_TRUNK, position))

        # Create leaves
        for dx in range(-2,3):
            for dy in range(0,3):
                for dz in range(-2,3):
                    position = (x + dx, y + trunk_height + dy, z + dz)
                    tree.append((TREE_LEAVES, position))
        return tree

    @staticmethod
    def generate_clouds(world_size: int = WORLD_SIZE, num_of_clouds=int((WORLD_SIZE * 3.75))) -> list[list[tuple[Block, Position]]]:
        """!
        @brief Generate sky cloud positions.
        @param world_size Half the world's size.
        @param num_of_clouds Number of clouds (default is "WORLD_SIZE * 3.75").
        @return clouds list of lists representing cloud block types and positions.
        @see [Issue#20](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/20)
        @see [Issue#28](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/28)
        @see [Issue#44](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/44)
        @see [Issue#84](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/84)
        @see [Issue#86](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/86)
        """
        game_margin = world_size
        clouds = list()
        for _ in xrange(num_of_clouds):
            cloud_center_x = random.randint(-game_margin, game_margin)
            cloud_center_z = random.randint(-game_margin, game_margin)
            cloud_center_y = random.choice([18,20,22,24,26])
            s = random.randint(3, 6) # 2 * s is the side length of the cloud

            single_cloud = World.generate_single_cloud(cloud_center_x, cloud_center_y, cloud_center_z, s)

            clouds.append(single_cloud)
        return clouds

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
        cloud_color = random.choice([LIGHT_CLOUD, DARK_CLOUD])
        for x in xrange(cloud_center_x - s, cloud_center_x + s + 1):
                for z in xrange(cloud_center_z - s, cloud_center_z + s + 1):
                    if (x - cloud_center_x) ** 2 + (z - cloud_center_z) ** 2 > (s + 1) ** 2:
                        continue
                    position = (x, cloud_center_y, z)
                    single_cloud.append((cloud_color, position))
        return single_cloud
