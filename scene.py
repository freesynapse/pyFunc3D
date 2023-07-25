
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

    def add_axes(self, x_linspace, z_linspace, id='axes'):
        self.objects[id] = AxesObj(self.app, shader='axes', obj_id=id)
        self.object_count += 1
        
    def add_data(self, x, y, z, func_id=None):
        obj_id = func_id
        if func_id is None:
            obj_id = 'func' + str(self.object_count)    
        self.objects[obj_id] = Func3DObj(self.app, x, y, z, shader='func3D')
        self.object_count += 1
        
    def render(self, camera):
        for obj_id in self.objects.keys():
            self.objects[obj_id].render(camera)

