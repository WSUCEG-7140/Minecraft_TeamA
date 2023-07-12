from pyglet.gl import *
import pyglet.graphics as graphics
import cmath as math
from ctypes import *
from tempus_fugit_minecraft.utilities import *

class Shaders():
    def __init__(self, model):
        self.blockInformation = model._shown
        '''Solves issue #7'''
    def TurnOnEnvironmentLight(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        lightpos = [0, -1, 0, 0.]
        lightpos = (c_float * len(lightpos))(*lightpos)
        glLightfv(GL_LIGHT0, GL_POSITION, lightpos)
        
    def Normal3DVectorCalc(self, vector):
        threeDVector = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])
        return threeDVector
        
