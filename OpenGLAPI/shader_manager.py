
import moderngl as mgl


class ShaderManager(object):
    def __init__(self, ctx):
        self.ctx : mgl.Context = ctx
        self.programs = {}
        self.programs['func3D'] = self.load_program('func3D')
        self.programs['axes'] = self.load_program('axes')
        self.programs['debug'] = self.load_program('debug')
    
    def load_program(self, shader_name, geometry_shader=False):
        with open(f'shaders/{shader_name}.vert') as file:
            vertex_shader = file.read()
        with open(f'shaders/{shader_name}.frag') as file:
            fragment_shader = file.read()
        
        if geometry_shader:
            with open(f'shaders/{shader_name}.geom') as file:
                geometry_shader = file.read()
            program = self.ctx.program(vertex_shader=vertex_shader, 
                                       geometry_shader=geometry_shader,
                                       fragment_shader=fragment_shader)
        else:
            program = self.ctx.program(vertex_shader=vertex_shader, 
                                       fragment_shader=fragment_shader)

        #print(program.__dict__)
            
        return program
