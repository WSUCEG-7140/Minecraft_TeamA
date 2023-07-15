from tempus_fugit_minecraft.block import *

class TestBlock:
    def test_specified_blocks_are_breakable(self):
        blocks = [GRASS, SAND, BRICK]
        
        for block in blocks: 
            assert block.is_breakable
        
    def test_specified_blocks_not_breakable(self):
        blocks = [STONE, LIGHT_CLOUD, DARK_CLOUD]

        for block in blocks:
            assert not block.is_breakable

    def test_specified_blocks_are_collidable(self):
        blocks = [GRASS, SAND, BRICK, STONE]
        
        for block in blocks: 
            assert block.is_collidable
    
    def test_specified_blocks_not_collidable(self):
        blocks = [LIGHT_CLOUD, DARK_CLOUD]

        for block in blocks:
            assert not block.is_collidable