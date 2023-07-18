from pyglet.gl import *
import pyglet.graphics as graphics
import cmath as math
from ctypes import *
from tempus_fugit_minecraft.utilities import *

'''!Function to convert a vector of numbers to a vector of c_float.
    @Param vector A     a list of numbers'''
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
        lightpos_y = [0, -1, 0, 0.]
        lightpos_y = to_cfloat(lightpos_y)
        glLightfv(GL_LIGHT0, GL_POSITION, lightpos_y)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)

        '''lightpos_x = to_cfloat([-1, 0, 0, 0.])
        glLightfv(GL_LIGHT1, GL_POSITION, lightpos_x)
        glLightfv(GL_LIGHT1, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT1, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT1, GL_SPECULAR, self.specular)

        lightpos_z = to_cfloat([0, 0, -1, 0.])
        glLightfv(GL_LIGHT2, GL_POSITION, lightpos_z)
        glLightfv(GL_LIGHT2, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT2, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT2, GL_SPECULAR, self.specular)'''
        return 1
    
    def enable_lighting(self):
        glEnable(GL_LIGHTING)
    
    def disable_lighting(self):
        glDisable(GL_LIGHTING)
    
    '''!Solves Issue #8. Adjusts the three types of light's color and intensity
        @Param red  a number that specifies the intensity of red light
        @Param green    a number that specifies the intensity of green light
        @Param blue     a number that specifies the intensity of blue light 
    '''
    def adjust_ambient_light(self, red, green, blue):
        self.ambient = to_cfloat([red, green, blue])
        return self.ambient

    def adjust_diffuse_light(self, red, green, blue):
        self.diffuse = to_cfloat([red, green, blue])
        return self.diffuse
    
    def adjust_specular_light(self, red, green, blue):
        self.specular = to_cfloat([red, green, blue])
        return self.specular
    
    def _update_light(self):
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)
    
    '''!Solves issue#8 Decreases the intensity of light
        @Param decrease_value   a number that specifies how much to decrease light intensity
    '''
    def decrease_light_intensity(self, decrease_value):
        self.ambient = to_cfloat([color - decrease_value for color in self.ambient])
        self.diffuse = to_cfloat([color - decrease_value for color in self.diffuse])
        self.specular = to_cfloat([color - decrease_value for color in self.specular])
        self._update_light()
    
    '''!Solves issue#8 Increases the intensity of light
        @Param increase_value   a number that specifies how much to decrease light intensity
    '''    
    def increase_light_intensity(self, increase_value):
        self.ambient = to_cfloat([color + increase_value for color in self.ambient])
        self.diffuse =  to_cfloat([color + increase_value for color in self.diffuse])
        self.specular =  to_cfloat([color + increase_value for color in self.specular])
        self._update_light()

    @staticmethod
    def normal_3D_vector_calc(vector):
        threeDVector = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])
        return threeDVector
    
