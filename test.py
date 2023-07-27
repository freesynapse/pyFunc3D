#%%
import glm
import math


#pos vec3(     -4.58544,    -0.246236,     -2.99724 )
#x_angle -0.10000000000004033
#y_angle 0.400000000000005
#forward vec3(     0.999974,   0.00698126,  -0.00174529 )
#up vec3(  -0.00698125,     0.999976,  1.21846e-05 )
#right vec3(   0.00174533,           -0,     0.999999 )
#target vec3(            0,            0,            0 )
f = glm.vec3(1, 0, 0)
u = glm.vec3(0, 1, 0)
r = glm.vec3(0, 0, 1)
t = glm.vec3(0, 0, 0)
p = glm.vec3(0, 0, 0)
vm = glm.lookAt(p, p+f, u)
print(vm)
print('inverted\n', glm.inverse(vm))

ivm = glm.inverse(vm)
p2 = glm.vec3(ivm[3])
f2 = -glm.vec3(ivm[2])
xa = glm.degrees(glm.atan(f2.z, f2.x))
ya = glm.degrees(glm.asin(f2.y))

print('p2:', p2)
print('f2:', f2)
print('xa:', xa)
print('ya:', ya)


# compare forward vector from view matrix with forward vector calculated from angles
x2r = glm.radians(xa)
y2r = glm.radians(ya)

f3 = glm.vec3(0)
f3.x = glm.cos(x2r) * glm.cos(y2r)
f3.y = glm.sin(y2r)
f3.z = glm.sin(x2r) * glm.cos(y2r)

print(f'{f2} == {f3}?')
# const glm::mat4 inverted = glm::inverse(previousCamera->view);
# position = glm::vec3(inverted[3]);
# const glm::vec3 direction = - glm::vec3(inverted[2]);
# yaw   = glm::degrees(glm::atan(direction.z, direction.x));
# pitch = glm::degrees(glm::asin(direction.y));


#%%

# target angles
t_x = 42.0
t_y = -89.0

pos     = glm.vec3( 0.0134285,  9.9999800,  0.0111486 )
forward = glm.vec3( 0.0129697, -0.9998480,  0.0116779)
up      = glm.vec3( 0.7430320,  0.0174524,  0.669029)
right   = glm.vec3(-0.6691310,  0.0000000,  0.743145)
target  = glm.vec3(0, 0, 0)

# recalc new vectors
forward2    = glm.normalize(target - pos)
right2      = glm.normalize(glm.cross(forward2, glm.vec3(0, 1, 0)))
up2         = glm.normalize(glm.cross(right2, forward2))
target2     = glm.normalize(pos + forward2)

vm = glm.lookAt(pos, pos+forward2, up2)
# pitch = y, yaw = x
pitch   = yrot = glm.degrees(math.asin(vm[0][1]))
yaw     = xrot = glm.degrees(math.atan2(-vm[0][2], vm[0][0]))
roll    = zrot = glm.degrees(math.atan2(-vm[2][1], vm[1][1]))

print(f'xrot = {xrot:.3f}\nyrot = {yrot:.3f}')

