
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
    def __init__(self, app, x, y, z, shader, pos=(0, 0, 0), 
                 rot=(0, 0, 0), scale=(1, 1, 1), obj_id=None):
        super().__init__(app, pos, rot, scale, obj_id)

        self.vbo_format = '3f 3f 3f'
        self.shader_attrs = ['a_position', 'a_normal', 'a_barycentric']
        self.mesh = Func3DMesh(x, y, z)
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
        self.shader['u_cam_pos'].write(camera.position)


#
class AxesObj(BaseObject):
    def __init__(self, 
                 app, 
                 func3dobj : Func3DObj,
                 #xlim : tuple = (-1, 1),
                 #ylim : tuple = (-1, 1),
                 #zlim : tuple = (-1, 1),
                 shader : str = 'axes', 
                 obj_id : str = 'axes'):
        super().__init__(app, (0, 0, 0), (0, 0, 0), (1, 1, 1), obj_id)
        self.primitive = mgl.LINES
        self.vbo_format = '3f 1f'
        self.shader_attrs = ['a_position', 'a_color_index']
        self.mesh = AxesMesh(xlim=xlim, 
                             ylim=ylim,
                             zlim=ylim)
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












