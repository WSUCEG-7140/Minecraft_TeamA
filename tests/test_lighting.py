import pyglet
import pytest
from pyglet.gl import *
from tempus_fugit_minecraft.window import Window
from tempus_fugit_minecraft.shaders import Shaders

@pytest.fixture(scope="class")
def window():
    yield Window()

class TestLighting():
    def test_lights_turned_on(self, window):
        assert glIsEnabled(GL_LIGHTING)
        assert glIsEnabled(GL_LIGHT0)
    
    @staticmethod
    def test_3D_norm_vector_calc():
        vector = [0, 0, 1]
        assert Shaders.Normal3DVectorCalc(vector) == 1