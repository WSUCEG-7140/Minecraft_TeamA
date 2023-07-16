from tempus_fugit_minecraft.block import *

class TestBlock:
    def test_specified_blocks_are_breakable(self):
        blocks = [GRASS, SAND, BRICK, TREE_LEAVES, TREE_TRUNK]
        
        for block in blocks: 
            assert block.is_breakable
        
    def test_specified_blocks_not_breakable(self):
        blocks = [STONE, LIGHT_CLOUD, DARK_CLOUD]

        for block in blocks:
            assert not block.is_breakable

    def test_specified_blocks_are_collidable(self):
        blocks = [GRASS, SAND, BRICK, STONE,TREE_TRUNK]
        
        for block in blocks: 
            assert block.is_collidable
    
    def test_specified_blocks_not_collidable(self):
        blocks = [LIGHT_CLOUD, DARK_CLOUD, TREE_LEAVES]

        for block in blocks:
            assert not block.is_collidable

    def test_specified_blocks_placeable(self):
        blocks = [GRASS, SAND, BRICK, TREE_LEAVES, TREE_TRUNK]
        
        for block in blocks:
            assert block.can_build_on

    def test_specified_blocks_not_placeable(self):
        blocks = [LIGHT_CLOUD, DARK_CLOUD]

        for block in blocks:
            assert not block.can_build_on