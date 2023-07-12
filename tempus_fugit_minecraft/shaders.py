from pyglet.gl import *
import pyglet.graphics as graphics
import cmath as math
from tempus_fugit_minecraft.utilities import *

class Shaders():
    def __init__(self, model):
        self.blockInformation = model._shown
        '''Solves issue #7'''
        def TurnOnEnvironmentLight():
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            lightpos = {0, -1, 0, 0.}
            glLightfv(GL_LIGHT0, GL_POSITION, lightpos)
        
        def Normal3DVectorCalc(vector):
            threeDVector = math.sqrt(vector[0] * v[0] + vector[1] * vector[1] + vector[2] * vector[2])
            return threeDVector
        
