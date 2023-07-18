#!/usr/bin/python3

import os, time, sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'   # hide pygame welcome message
import pygame as pg
import moderngl as mgl
import numpy as np
#
from settings import *
from OpenGLAPI.shader_manager import ShaderManager
from OpenGLAPI.camera import OrbitCamera
from scene import Scene

#
class pyFunc3D:
    def __init__(self, window_size=WIN_RES):
        t0 = time.perf_counter_ns()
        self.window_size = window_size
        # Init PyGame and set OpenGL attributes
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)
        pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        
        # OpenGL context and settings
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)# | mgl.BLEND)
        self.ctx.blend_func = mgl.SRC_ALPHA, mgl.ONE_MINUS_SRC_ALPHA
        self.ctx.gc_mode = 'auto'

        # framerate-related
        self.clock = pg.time.Clock()
        self.dt = 0
        self.time = 0
        self.fps = 0
        self.frame_count = 0

        pg.event.set_grab(True)
        pg.mouse.set_visible(False)
        
        print(f'Core modules initialized in {(time.perf_counter_ns() - t0)/1e6} ms.')
        
        self.is_running = True
        self.is_loaded = False
        
        self.on_init()
    
    #
    def on_init(self):
        self.shader_manager = ShaderManager(self.ctx)
        self.camera = OrbitCamera(self, x_angle=40, y_angle=60)
        self.scene = Scene(self, self.camera)
    
    #
    def load_numpy_array(self, 
                         data : np.ndarray, 
                         x_linspace : np.ndarray, 
                         z_linspace : np.ndarray,
                         func_id : str=None):
        self.scene.add_data(data, x_linspace, z_linspace, func_id)
        self.is_loaded = True
    
    #
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                self.is_running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.is_running = False
                if event.key == pg.K_c:
                    print('Camera state:')
                    attrs = vars(self.camera)
                    [print(f'\t{item}') for item in attrs.items()]
    
    #
    def update(self):
        self.camera.update()
    
    #
    def render(self):
        self.ctx.clear(color=BG_COLOR)
        self.scene.render(self.camera)
        pg.display.flip()
    
    #    
    def run(self):
        if not self.is_loaded:
            self.shutdown(error_msg='no data loaded')
            
        while self.is_running:
            self.handle_events()
            self.update()
            self.render()

            #
            self.dt = self.clock.tick(60)
            self.fps = 1000.0 / self.dt

    #
    def shutdown(self, error_msg=None):
        pg.quit()
        if error_msg is not None:
            raise Exception(error_msg)
        sys.exit()

        


if __name__ == '__main__':
    #
    app = pyFunc3D()
    #
    d = 6.0
    nx, nz = 100, 100
    x, z = np.linspace(-d, d, nx), np.linspace(-d, d, nz)
    X, Z = np.meshgrid(x, z)
    Y = (np.sin(2.0 * X) * np.cos(1.0 * Z) / 2.0)
    app.load_numpy_array(Y, x, z)
    #
    app.run()

