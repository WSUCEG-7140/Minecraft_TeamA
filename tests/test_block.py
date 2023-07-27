from tempus_fugit_minecraft.block import (Block)

class TestBlock:
    # issue#47 issue#80 issue#33 issue#34 
    def test_specified_blocks_are_breakable(self):
        blocks = [Block.GRASS, Block.SAND, Block.BRICK, Block.TREE_LEAVES, Block.TREE_TRUNK, Block.LIGHT_CLOUD, Block.DARK_CLOUD]

        for block in blocks:
            assert block.is_breakable

    # issue#47 #issue#80 issue#33 issue#34
    def test_specified_blocks_not_breakable(self):
        blocks = [Block.STONE]

        for block in blocks:
            assert not block.is_breakable

    #issue47 #issue80
    def test_specified_blocks_are_collidable(self):
        blocks = [Block.GRASS, Block.SAND, Block.BRICK, Block.STONE,Block.TREE_TRUNK]

        for block in blocks:
            assert block.is_collidable

    #issue47 #issue80
    def test_specified_blocks_not_collidable(self):
        blocks = [Block.LIGHT_CLOUD, Block.DARK_CLOUD, Block.TREE_LEAVES]

        for block in blocks:
            assert not block.is_collidable

    #issue47; #issue80 issue#33 issue#34
    def test_specified_blocks_placeable(self):
        blocks = [Block.GRASS, Block.SAND, Block.BRICK, Block.TREE_LEAVES, Block.TREE_TRUNK, Block.LIGHT_CLOUD, Block.DARK_CLOUD]

        for block in blocks:
            assert block.can_build_on

    #issue#47 issue#33 
    def test_specified_blocks_not_placeable(self):
        # Currently no blocks can not be built on...
        blocks = []

        for block in blocks:
            assert not block.can_build_on