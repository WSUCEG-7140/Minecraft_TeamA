import pyglet
import pytest
from pyglet.gl import *
from ctypes import c_float
from tempus_fugit_minecraft.window import Window
from tempus_fugit_minecraft.shaders import Shaders, to_cfloat

@pytest.fixture(scope="class")
def window():
    yield Window()

class TestLighting():
    def test_lights_turned_on(self, window):
        assert glIsEnabled(GL_LIGHTING)
        assert glIsEnabled(GL_LIGHT0)

    def test_disable_glLIGHTING(self, window):
        window.shaders.disable_lighting()
        assert not glIsEnabled(GL_LIGHTING)
    
    def test_enable_glLIGHTING(self, window):
        window.shaders.enable_lighting()
        assert glIsEnabled(GL_LIGHTING)

    def test_convert_to_c_float(self):
        vector = [1, 1.0]
        assert isinstance(to_cfloat(vector)[0], float)
        assert isinstance(to_cfloat(vector)[1], float)

    @staticmethod
    def test_3D_norm_vector_calc():
        vector = [0, 0, 1]
        assert Shaders.normal_3D_vector_calc(vector) == 1