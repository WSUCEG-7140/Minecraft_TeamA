def cube_vertices(x: float, y: float, z: float, n: float) -> list:
    """!
    @brief Return the vertices of the cube at position x, y, z with size 2*n.
    @param x The x coordinate of the center of the cube
    @param y The y coordinate of the center of the cube 
    @param z The z coordinate of the center of the cube
    @param n The size of the cube
    @return A list of verticies of the cube passed in
    @see [Issue#47](https://github.com/WSUCEG-7140/Tempus_Fugit_Minecraft/issues/47)
    """
    return [
        x-n,y+n,z-n, x-n,y+n,z+n, x+n,y+n,z+n, x+n,y+n,z-n,  # top
        x-n,y-n,z-n, x+n,y-n,z-n, x+n,y-n,z+n, x-n,y-n,z+n,  # bottom
        x-n,y-n,z-n, x-n,y-n,z+n, x-n,y+n,z+n, x-n,y+n,z-n,  # left
        x+n,y-n,z+n, x+n,y-n,z-n, x+n,y+n,z-n, x+n,y+n,z+n,  # right
        x-n,y-n,z+n, x+n,y-n,z+n, x+n,y+n,z+n, x-n,y+n,z+n,  # front
        x+n,y-n,z-n, x-n,y-n,z-n, x-n,y+n,z-n, x+n,y+n,z-n,  # back
    ]

WORLD_SIZE = 160
TICKS_PER_SEC = 60

FACES = [
    (0, 1, 0),
    (0, -1, 0),
    (-1, 0, 0),
    (1, 0, 0),
    (0, 0, 1),
    (0, 0, -1),
]
