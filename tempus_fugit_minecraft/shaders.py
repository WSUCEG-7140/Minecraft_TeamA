from pyglet.gl import *
import pyglet.graphics as graphics
import cmath as math
from ctypes import *
from tempus_fugit_minecraft.utilities import *

def to_cfloat(vector):
    return (c_float * len(vector))(*vector)

class Shaders():
    def __init__(self, model):
        self.blockInformation = model._shown
        self.ambient = to_cfloat([3, 3, 3])
        self.diffuse = to_cfloat([3, 3, 3])
        self.specular = to_cfloat([3, 3, 3])
        '''Solves issue #7'''
    def turn_on_environment_light(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        lightpos = [0, -1, 0, 0.]
        lightpos = (c_float * len(lightpos))(*lightpos)
        glLightfv(GL_LIGHT0, GL_POSITION, lightpos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)
        return 1
        
    @staticmethod
    def normal_3D_vector_calc(vector):
        threeDVector = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])
        return threeDVector
    
