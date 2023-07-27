
import glm
import pygame as pg
import math
import time
#
from settings import *

#
class CameraObj(object):
    def __init__(self, app, position, x_angle, y_angle):
        self.app = app
        self.type : str = ''
        self.aspect_ratio = app.window_size[0] / app.window_size[1]
        self.position = glm.vec3(position)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)
        self.target = glm.vec3(0, 0, 0)
        self.y_angle = y_angle
        self.x_angle = x_angle
        self.m_proj = self.get_projection_matrix()
        self.m_view = self.get_view_matrix()
    
    # 'virtual' functions    
    def get_projection_matrix(self): ...
    def get_view_matrix(self): ...
    def init_camera_vectors(self): ...
    def update_camera_vectors(self): ...
    def update(self): ...

    #
    def copy_state(self, camera2):
        self.position = camera2.position
        self.m_view = camera2.m_view
        self.init_camera_vectors()
    
    #
    def print_state_debug(self):
        print('---- CAMERA STATE ----')
        print(f'type    : {self.type}')
        print(f'pos     : {self.position}')
        print(f'x_angle : {self.x_angle}')
        print(f'y_angle : {self.y_angle}')
        print(f'forward : {self.forward}')
        print(f'up      : {self.up}')
        print(f'right   : {self.right}')
        print(f'target  : {self.target}')
        print(f'm_view\n{self.m_view}')
        
        
#
class PerspectiveCamera(CameraObj):
    def __init__(self, app, position=(0, 0, 0), x_angle=-90, y_angle=-35):
        super().__init__(app, position, x_angle, y_angle)
        self.type = 'PERSPECTIVE'
        
    #
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
    
    #
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)

    #
    def init_camera_vectors(self):
        # recreate all vectors and rotations from the view matrix of the
        # other camera
        inv_m_view = glm.inverse(self.m_view)
        self.position = glm.vec3(inv_m_view[3])
        self.forward = -glm.vec3(inv_m_view[2])
        self.x_angle = glm.degrees(glm.atan(self.forward.z, self.forward.x))
        self.y_angle = glm.degrees(glm.asin(self.forward.y))
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

    #
    def update_camera_vectors(self):
        x_rad, y_rad = glm.radians(self.x_angle), glm.radians(self.y_angle)
        
        self.forward.x = glm.cos(x_rad) * glm.cos(y_rad)
        self.forward.y = glm.sin(y_rad)
        self.forward.z = glm.sin(x_rad) * glm.cos(y_rad)
        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))
    
    #    
    def rotate(self):
        rel_x, rel_y = pg.mouse.get_rel()
        self.x_angle += rel_x * SENSITIVITY
        if self.x_angle > 360.0:
            self.x_angle -= 360.0
        elif self.x_angle < -360.0:
            self.x_angle += 360.0
        
        self.y_angle -= rel_y * SENSITIVITY
        self.y_angle = max(-89, min(89, self.y_angle))
        
    #
    def move(self):
        velocity = PERSPECTIVE_SPEED * self.app.dt
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.position += self.forward * velocity
        if keys[pg.K_s]:
            self.position -= self.forward * velocity
        if keys[pg.K_d]:
            self.position += self.right * velocity
        if keys[pg.K_a]:
            self.position -= self.right * velocity
        if keys[pg.K_SPACE]:
            self.position += self.up * velocity
        if keys[pg.K_LSHIFT]:
            self.position -= self.up * velocity

    #
    def update(self):
        self.move()
        self.rotate()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()

#
class OrbitCamera(CameraObj):
    def __init__(self, app, position=(0, 0, 0), x_angle=90, y_angle=35, radius=10.0):
        super().__init__(app, position, x_angle, y_angle)    
        self.type = 'SPH_ORBIT'
        self.radius = radius
        x_rad, y_rad = glm.radians(self.x_angle), glm.radians(self.y_angle)
        self.position.x = self.radius * math.sin(y_rad) * math.cos(x_rad)
        self.position.y = self.radius * math.cos(y_rad)
        self.position.z = self.radius * math.sin(y_rad) * math.sin(x_rad)
    
    #
    def get_projection_matrix(self):
        return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
    
    #
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.target, self.up)

    #
    def init_camera_vectors(self):
        # recreate vectors and rotations from prev cameras view matrix
        inv_m_view = glm.inverse(self.m_view)
        self.position = glm.vec3(inv_m_view[3])
        # avoid division by zero
        if self.position.x == 0:
            self.position.x += EPSILON
        if self.position.z == 0:
            self.position.z += EPSILON
        self.radius = max(glm.length(self.position), EPSILON)
        # conversion of cartesian to spherical coordinates
        #
        self.x_angle = glm.degrees(glm.atan(self.position.z / self.position.x))
        # adjust x angle (theta) according to quadrant
        if self.position.x < 0:
            if self.position.z >= 0.0:
                self.x_angle += 180.0
            elif self.position.z < 0.0:
                self.x_angle -= 180.0
        self.y_angle = glm.degrees(glm.acos(self.position.y / self.radius))
        # clamp angles
        if self.x_angle < 0.0:
            self.x_angle += 360.0
        if self.x_angle > 360.0:
            self.x_angle -= 360.0
            
        
        self.target = glm.vec3(0, 0, 0)
        self.update_camera_vectors()
        
    #
    def update_camera_vectors(self):        
        # update pos based on rot angles
        x_rad, y_rad = glm.radians(self.x_angle), glm.radians(self.y_angle)
        self.position.x = self.radius * glm.sin(y_rad) * glm.cos(x_rad)
        self.position.y = self.radius * glm.cos(y_rad)
        self.position.z = self.radius * glm.sin(y_rad) * glm.sin(x_rad)

        # calculate direction vectors        
        self.forward.x = glm.normalize(self.position - self.target)
        if abs(self.forward.x) < EPSILON and abs(self.forward.z) < EPSILON:
            if self.forward.y > 0:
                self.up = glm.vec3(0, 0, -1)
            else:
                self.up = glm.vec3(0, 0, 1)
        else:
            self.up = glm.vec3(0, 1, 0)
            
        self.right = glm.normalize(glm.cross(self.forward, self.up))
        self.up = glm.normalize(glm.cross(self.right, self.forward))
        
        # update view matrix
        self.m_view = self.get_view_matrix()
    
    #    
    def on_input(self):
        rel_x, rel_y = pg.mouse.get_rel()
        delta = ORBIT_SPEED * glm.vec2(rel_x, rel_y)
        self.x_angle += delta.x
        self.y_angle -= delta.y
        
        if self.x_angle > 360.0:    self.x_angle -= 360.0
        if self.x_angle < 0.0:      self.x_angle += 360.0
        
        self.y_angle = min(max(self.y_angle, 0.1), 179.0)
        
        # zoom
        velocity = ZOOM_SPEED * self.app.dt
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            self.radius -= velocity
        if keys[pg.K_s]:
            self.radius += velocity
        self.radius = min(max(self.radius, 0.05), FAR+100.0)
        
    #
    def update(self):
        self.on_input()
        self.update_camera_vectors()
        self.m_view = self.get_view_matrix()
    