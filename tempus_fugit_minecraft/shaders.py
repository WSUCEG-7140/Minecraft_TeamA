import cmath as math
from ctypes import *

from pyglet.gl import *


def to_cfloat(vector):
    """!
    @brief Function to convert a vector of numbers to a vector of c_float.
    @Param vector A vector with numbers
    """
    return (c_float * len(vector))(*vector)


def c_float_vector_is_equal(vector1, vector2):
    """!
    @brief compare two c_float vectors.
    @param vector1  The first c_float vector
    @param vector2  The second c_float vector
    """
    count = 0
    if len(vector1) != len(vector2):
        return False

    for value in vector1:
        if value != vector2[count]:
            return False
        else:
            count = count + 1
    return True


class Shaders:
    """!
    @brief The Shader class holds the attributes and functions responsible for applying lighting and darkness to the
    game.
    @return shaders An instance of Shaders class.
    """
    def __init__(self, model):
        self.blockInformation = model._shown
        self.ambient = to_cfloat([3, 3, 3])
        self.diffuse = to_cfloat([3, 3, 3])
        self.specular = to_cfloat([3, 3, 3])

    def turn_on_environment_light(self):
        """!
        @brief Turns on the environment light.
        @see [Issue#7](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/7)
        """
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        light_pos_y = [0, -1, 0, 0.]
        light_pos_y = to_cfloat(light_pos_y)
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos_y)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)
        return 1

    @staticmethod
    def enable_lighting():
        """!
        @brief This function turns on realistic lighting in your graphics. It considers the light sources and material
            properties. giving the objects a real appearance with shadows and highlights.
        """
        glEnable(GL_LIGHTING)

    @staticmethod
    def disable_lighting():
        """!
        @brief This function switches off the lighting effects. All the shadow and the highlight effects will disappear.
        """
        glDisable(GL_LIGHTING)

    def adjust_ambient_light(self, red, green, blue):
        """!
        @brief Adjusts the three types of light's color and intensity
        @Param red a number that specifies the intensity of red light
        @Param green a number that specifies the intensity of green light
        @Param blue a number that specifies the intensity of blue light
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
    """
        self.ambient = to_cfloat([red, green, blue])
        return self.ambient

    def adjust_diffuse_light(self, red, green, blue):
        """!
        @brief Adjusts the diffuse light color.
        @param red The intensity of the red component of the diffuse light color.
        @param green The intensity of the green component of the diffuse light color.
        @param blue The intensity of the blue component of the diffuse light color.
        @return The adjusted diffuse light color as a list of three elements (red, green, blue).
        """
        self.diffuse = to_cfloat([red, green, blue])
        return self.diffuse

    def adjust_specular_light(self, red, green, blue):
        """!
        @brief Adjusts the specular light color.
        @param red The red component of the specular light color.
        @param green The green component of the specular light color.
        @param blue The blue component of the specular light color.
        @return The updated specular light color as a list of floats.
        """
        self.specular = to_cfloat([red, green, blue])
        return self.specular

    def _update_light(self):
        """!
        @brief Takes the classes current ambient, diffuse and light values and changes them
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)

    def decrease_light_intensity(self, decrease_value):
        """!
        @brief Decreases the intensity of light.
        @Param decrease_value A number that specifies how much to decrease light intensity
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.ambient = to_cfloat([color - decrease_value for color in self.ambient])
        self.diffuse = to_cfloat([color - decrease_value for color in self.diffuse])
        self.specular = to_cfloat([color - decrease_value for color in self.specular])
        self._update_light()

    def increase_light_intensity(self, increase_value):
        """!
        @brief Increases the intensity of light.
        @Param increase_value A number that specifies how much to increase light intensity
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.ambient = to_cfloat([color + increase_value for color in self.ambient])
        self.diffuse = to_cfloat([color + increase_value for color in self.diffuse])
        self.specular = to_cfloat([color + increase_value for color in self.specular])
        self._update_light()

    @staticmethod
    def normal_3D_vector_calc(vector):
        """!
        @brief Calculates the magnitude of a 3D vector.
        @param vector A list representing the 3D vector.
        @return The magnitude of the vector.
        """
        threeDVector = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])
        return threeDVector
