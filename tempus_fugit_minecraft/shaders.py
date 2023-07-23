from pyglet.gl import *
import cmath as math
from ctypes import *


def to_cfloat(vector):
    """!
    @brief Function to convert a vector of numbers to a vector of c_float.
    @Param vector A vector with numbers
    @return A c_float class vector
    """
    return (c_float * len(vector))(*vector)

    
def c_float_vector_is_equal(vector1, vector2):
    """!
    @brief Compare two c_float vectors and check if they are equal.
    @param vector1  The first c_float vector
    @param vector2  The second c_float vector
    @return A boolean depending on if the two c_float vectors are equal or not
    """
    count = 0
    if len(vector1) != len(vector2):
        return False

    for float in vector1:
        if float != vector2[count]:
            return False
        else:
            count = count + 1
    return True

class Shaders():
    """!
    @brief The Shader class holds the attributes and functions 
        responsible for applying lighting and darkness to the game.
        @param blockInformation  An array of the currently shown blocks taken from the model class
        @param ambient  A c_float vector consisting of red, green blue that is used to determine the ambient light
        @param diffuse  A c_float vector consisting of red, green, blue that is used to determine the diffuse light
        @param specular A c_float vector consisting of red, green, blue that is used to determine the specular light
    @return shaders An instance of Shaders class.
    """
    def __init__(self, model):
        self.blockInformation = model._shown
        self.ambient = to_cfloat([3, 3, 3])
        self.diffuse = to_cfloat([3, 3, 3])
        self.specular = to_cfloat([3, 3, 3])
        
    def turn_on_environment_light(self):
        """!
        @brief Activates the OpenGL light and sets up the enivronmental lighting at the top of the minecraft world.
        The light is aimed downwards with infinite range. 
        @return Returns a 1 to signify completion of the job function
        @see [Issue#7](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/7)
        """
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        lightpos_y = [0, -1, 0, 0.]
        lightpos_y = to_cfloat(lightpos_y)
        glLightfv(GL_LIGHT0, GL_POSITION, lightpos_y)
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)
        return 1

    def enable_lighting(self):
        """!
        @brief This function enables GL_LIGHTING. GL_LIGHTING is what enables lighting effects.
        This enables the shadow and highlight effects.
        https://www.khronos.org/opengl/wiki/How_lighting_works
        """
        glEnable(GL_LIGHTING)

    def disable_lighting(self):
        """!
        @brief This function switches GL_LIGHTING. This turns off the lighting effects. All the 
            shadow and the highlight effects will dissapear.
        https://www.khronos.org/opengl/wiki/How_lighting_works
        """
        glDisable(GL_LIGHTING)

    def adjust_ambient_light(self, red, green, blue):
        """!
        @brief Adjusts the three types of light's color and intensity
        @Param red a number that specifies the intensity of red light
        @Param green a number that specifies the intensity of green light
        @Param blue a number that specifies the intensity of blue light
        @return returns the c_float vector that corresponds to the ambient
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.ambient = to_cfloat([red, green, blue])
        return self.ambient

    def adjust_diffuse_light(self, red, green, blue):
        """!
        @brief Adjusts the three types of light's color and intensity
        @Param red a number that specifies the intensity of red light
        @Param green a number that specifies the intensity of green light
        @Param blue a number that specifies the intensity of blue light
        @return returns the c_float vector that corresponds to the diffuse light
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.diffuse = to_cfloat([red, green, blue])
        return self.diffuse
    
    def adjust_specular_light(self, red, green, blue):
        """!
        @brief Adjusts the three types of light's color and intensity
        @Param red a number that specifies the intensity of red light
        @Param green a number that specifies the intensity of green light
        @Param blue a number that specifies the intensity of blue light
        @return returns the c_float vector that corresponds to the specular light
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.specular = to_cfloat([red, green, blue])
        return self.specular
    
    def _update_light(self):
        """!
        @brief Takes the classes current ambient, diffuse and light 
            values and updates the GL_LIGHT0 values
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        glLightfv(GL_LIGHT0, GL_AMBIENT, self.ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, self.diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, self.specular)
    
    def decrease_light_intensity(self, decrease_value):
        """!
        @brief Decreases the intensity of light.
        @Param decrease_value A number that specifies how much to 
            decrease light intensity
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.ambient = to_cfloat([color - decrease_value for color in self.ambient])
        self.diffuse = to_cfloat([color - decrease_value for color in self.diffuse])
        self.specular = to_cfloat([color - decrease_value for color in self.specular])
        self._update_light()
    
    def increase_light_intensity(self, increase_value):
        """!
        @brief Increases the intensity of light.
        @Param increase_value A number that specifies how much to 
            increase light intensity
        @see [Issue#12](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/12)
        """
        self.ambient = to_cfloat([color + increase_value for color in self.ambient])
        self.diffuse =  to_cfloat([color + increase_value for color in self.diffuse])
        self.specular =  to_cfloat([color + increase_value for color in self.specular])
        self._update_light()

    @staticmethod
    def normal_3D_vector_calc(vector):
        """!
        @brief A calculation to get the normal 3D vector from a vector
        @param vector   The vector that will be calculated
        @return The normal 3D vector.
        """
        threeDVector = math.sqrt(vector[0] * vector[0] + vector[1] * vector[1] + vector[2] * vector[2])
        return threeDVector
