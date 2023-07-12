import pyglet
import pytest
from pyglet.gl import *
from unittest.mock import Mock
from tempus_fugit_minecraft.window import Window

@pytest.fixture(scope="class")
def window():
    yield Window()

class TestLighting():
    def test_lights_turned_on(self, window):
        window.setup_environmental_lighting()
        assert glIsEnabled(GL_LIGHTING)
        assert glIsEnabled(GL_LIGHT0)
    
    def test_3D_norm_vector_calc():
        vector = [0, 0, 1]
        threeDNormVector = window.shaders.Normal3DVectorCalc(vector)
        assert threeDNormVector == 1