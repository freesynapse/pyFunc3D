
import numpy as np
from OpenGLAPI.object import *

#
class Scene:
    def __init__(self, app, camera):
        self.app = app
        self.camera = camera
        self.objects = {}
        self.object_count = 0
        #self.objects['f'] = Func3DObj(app, shader='func3D')
        #self.objects.append(DebugCubeObj(app, shader='debug'))
        
    def add_data(self, data : np.ndarray, x_linspace, z_linspace, func_id=None):
        obj_id = func_id
        if func_id is None:
            obj_id = 'func' + str(self.object_count)    
        self.objects[obj_id] = Func3DObj(self.app, data, x_linspace, z_linspace, shader='func3D')
        self.object_count += 1
        
    def render(self, camera):
        for obj_id in self.objects.keys():
            self.objects[obj_id].render(camera)

