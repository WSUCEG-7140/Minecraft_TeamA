from tempus_fugit_minecraft.block import *


class TestBlock:
    # issue#47 issue#80 issue#33 issue#34 
    def test_specified_blocks_are_breakable(self):
        blocks = [GRASS, SAND, BRICK, TREE_LEAVES, TREE_TRUNK, LIGHT_CLOUD, DARK_CLOUD]

        for block in blocks:
            assert block.is_breakable

    # issue#47 #issue#80 issue#33 issue#34
    def test_specified_blocks_not_breakable(self):
        blocks = [STONE]

        for block in blocks:
            assert not block.is_breakable

    #issue47 #issue80
    def test_specified_blocks_are_collidable(self):
        blocks = [GRASS, SAND, BRICK, STONE,TREE_TRUNK]

        for block in blocks:
            assert block.is_collidable

    #issue47 #issue80 issue#33 issue#34
    def test_specified_blocks_not_collidable(self):
        blocks = [LIGHT_CLOUD, DARK_CLOUD, TREE_LEAVES]

        for block in blocks:
            assert not block.is_collidable

    #issue47; #issue80 issue#33 issue#34
    def test_specified_blocks_placeable(self):
        blocks = [GRASS, SAND, BRICK, TREE_LEAVES, TREE_TRUNK, LIGHT_CLOUD,DARK_CLOUD]

        for block in blocks:
            assert block.can_build_on
