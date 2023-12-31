
import moderngl as mgl
import glm
#
from OpenGLAPI.mesh import *


class BaseObject:
    def __init__(self, app, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), obj_id=None):
        self.app = app
        self.ctx : mgl.Context = app.ctx
        self.mesh : BaseMesh = None
        self.shader : mgl.Context.program = None
        self.vao : mgl.Context.vertex_array = None
        self.obj_id = obj_id
        self.primitive = mgl.TRIANGLES
        #
        self.pos = glm.vec3(pos)
        self.rot = glm.vec3(rot)
        self.scale = glm.vec3(scale)
        self.m_model : glm.mat4 = self.get_model_matrix()
    #
    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        # scale
        m_model = glm.scale(m_model, self.scale)        
        #
        return m_model
    #
    def on_init(self): ...
    def update(self, camera): ...
    def render(self, camera):
        self.update(camera)
        #print(f'{self.primitive} == {mgl.LINES} : {self.primitive == mgl.LINES}')
        self.vao.render(self.primitive)
        
        
#
class DebugCubeObj(BaseObject):
    def __init__(self, app, shader='debug', pos=(0, 0, 0), rot=(0, 0, 0), 
                 scale=(1, 1, 1)):
        super().__init__(app, pos, rot, scale)
        self.mesh = DebugCubeMesh()
        self.vbo_format = '3f 3f'
        self.shader_attrs = ['a_position', 'a_normal']
        self.vbo = self.ctx.buffer(self.mesh.vertex_data)
        self.shader = self.app.shader_manager.programs[shader]
        self.vao = self.ctx.vertex_array(self.shader, 
                                         [(self.vbo, self.vbo_format, *self.shader_attrs)],
                                         skip_errors=True)

    def on_init(self): pass
    
    def update(self, camera):
        self.shader['m_model'].write(self.m_model)
        self.shader['m_view'].write(camera.m_view)
        self.shader['m_proj'].write(camera.m_proj)

#
class Func3DObj(BaseObject):
    def __init__(self, app, x, y, z, equal_axes, shader, pos=(0, 0, 0), 
                 rot=(0, 0, 0), scale=(1, 1, 1), obj_id=None):
        super().__init__(app, pos, rot, scale, obj_id)

        self.vbo_format = '3f 3f 3f 3f'
        self.shader_attrs = ['a_position', 'a_normal', 'a_barycentric', 'a_color']
        self.mesh = Func3DMesh(x, y, z, equal_axes)
        self.vbo = self.ctx.buffer(self.mesh.vertex_data)
        self.shader = self.app.shader_manager.programs[shader]
        self.vao = self.ctx.vertex_array(self.shader, 
                                         [(self.vbo, self.vbo_format, *self.shader_attrs)],
                                         skip_errors=True)
        self.wireframe = False
        self.lighting = True
        #self.Ipos = glm.vec3(self.mesh.x[0], self.mesh.ylim[1]+3.0, self.mesh.z[0])
        self.Ipos = glm.vec3(2.5, 5.0, -2.5)
        #
        self.on_init()
        
    #
    def toggle_wireframe(self):
        self.wireframe = not self.wireframe
        #print(f'wireframe: {str(self.wireframe)}')
        
    #
    def toggle_lights(self):
        self.lighting = not self.lighting
        #print(f'lighting: {str(self.lighting)}')
    
    #
    def on_init(self): 
        self.shader['u_Ipos'].write(self.Ipos)
            
    #
    def update(self, camera):
        self.shader['m_model'].write(self.m_model)
        self.shader['m_view'].write(camera.m_view)
        self.shader['m_proj'].write(camera.m_proj)
        self.shader['u_cam_pos'].write(camera.position)
        self.shader['u_use_wireframe'].write(np.array(self.wireframe, dtype='int32'))
        self.shader['u_use_lighting'].write(np.array(self.lighting, dtype='int32'))


#
class AxesObj(BaseObject):
    def __init__(self, 
                 app, 
                 func3DObj : Func3DObj,
                 shader : str = 'axes', 
                 obj_id : str = 'axes'):
        super().__init__(app, (0, 0, 0), (0, 0, 0), (1, 1, 1), obj_id)
        self.primitive = mgl.LINES
        self.vbo_format = '3f 1f'
        self.shader_attrs = ['a_position', 'a_color_index']
        func_mesh = func3DObj.mesh
        self.mesh = AxesMesh(xlim=(func_mesh.x[0], func_mesh.x[-1]),
                             ylim=func_mesh.ylim,
                             zlim=(func_mesh.z[0], func_mesh.z[-1]))
        self.vbo = self.ctx.buffer(self.mesh.vertex_data)
        self.shader = self.app.shader_manager.programs[shader]
        self.vao = self.ctx.vertex_array(self.shader,
                                         [(self.vbo, self.vbo_format, *self.shader_attrs)],
                                         skip_errors=True)
        
    # 
    def on_init(self): pass
    
    #
    def update(self, camera):
        self.shader['m_model'].write(self.m_model)
        self.shader['m_view'].write(camera.m_view)
        self.shader['m_proj'].write(camera.m_proj)












