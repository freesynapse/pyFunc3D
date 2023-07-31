
import glm

# app settings
WIN_RES = glm.ivec2(1440, 900)
#BG_COLOR = glm.vec3(0.10, 0.16, 0.25)
BG_COLOR = glm.vec3(0.9)

# camera
FOV = 60
NEAR = 0.01
FAR = 1000
PERSPECTIVE_SPEED = 0.01
SENSITIVITY = 0.1
ORBIT_SPEED = 0.1
ZOOM_SPEED = 0.03
EPSILON = 1e-7

# 3D functions
MESH_SCALE = (5.0, 1.5, 5.0)    # scale of (x, y, z) axes in mesh, rescaled in Func3DMesh 
                                # constructor. If x/z dimensions are unequal, a flag in
                                # the mesh constructor dictates the behaviour.



