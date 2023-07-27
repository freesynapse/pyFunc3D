#!/usr/bin/python3

import os, time, sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'   # hide pygame welcome message
import pygame as pg
import moderngl as mgl
import numpy as np
#
from settings import *
from OpenGLAPI.shader_manager import ShaderManager
from OpenGLAPI.camera import OrbitCamera, PerspectiveCamera
from scene import Scene

#
class Func3D:
    def __init__(self, window_size=WIN_RES):
        t0 = time.perf_counter_ns()
        self.window_size = window_size
        # init PyGame and set OpenGL attributes
        pg.init()
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        pg.display.gl_set_attribute(pg.GL_DEPTH_SIZE, 24)
        self.surface = pg.display.set_mode(WIN_RES, flags=pg.OPENGL | pg.DOUBLEBUF)
        
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
        
        self.is_running = True
        self.is_loaded = False
        
        self.on_init()
        
        print(f'Core modules initialized in {(time.perf_counter_ns() - t0)/1e6} ms.')
    
    #
    def on_init(self):
        self.shader_manager = ShaderManager(self.ctx)
        self.camera_orbit = OrbitCamera(self, x_angle=40, y_angle=60)
        self.camera_perspective = PerspectiveCamera(self, x_angle=0, y_angle=0)
        # vectors screwed up?! forward = (1, 0, 0)?
        self.camera = self.camera_perspective
        self.camera_orbit_current = False    # toggle for switching camera
        self.scene = Scene(self, self.camera)
        self.func3D_obj_id = '' # for later access through Scene
    #
    def load_numpy_array(self, 
                         data : np.array,
                         x : np.ndarray =None, 
                         y : np.ndarray =None, 
                         func_id : str=None):
        t0 = time.perf_counter_ns()
        self.func3D_obj_id = self.scene.add_data(x, data, y, func_id)
        self.scene.add_axes(self.func3D_obj_id)
        self.is_loaded = True
        print(f'Meshes created in {(time.perf_counter_ns() - t0)/1e6} ms.')
    
    #
    def handle_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                self.is_running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.is_running = False
                # take screenshot
                if event.key == pg.K_z:
                    pg.image.save(self.surface, './screenshot.png')
                # toggle mesh wireframe
                if event.key == pg.K_F3:
                    self.scene.objects[self.func3D_obj_id].toggle_wireframe()
                if event.key == pg.K_F4:
                    self.scene.objects[self.func3D_obj_id].toggle_lights()
                # DEBUG : camera state
                if event.key == pg.K_c:
                    self.camera.print_state_debug()
                # toggle orbital/perspective camera
                if event.key == pg.K_TAB:
                    #print('==========================================================')
                    #self.camera.print_state_debug()
                    if self.camera_orbit_current:
                        self.camera = self.camera_perspective
                        self.camera.copy_state(self.camera_orbit)
                    else:
                        self.camera = self.camera_orbit
                        self.camera.copy_state(self.camera_perspective)
                    #self.camera.print_state_debug()
                    self.camera_orbit_current = not self.camera_orbit_current
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
            self.dt = self.clock.tick()
            self.fps = 1000.0 / self.dt
            pg.display.set_caption(f'{self.fps:.2f} fps')

    #
    def shutdown(self, error_msg=None):
        pg.quit()
        if error_msg is not None:
            raise Exception(error_msg)
        sys.exit()

        


if __name__ == '__main__':
    #
    app = Func3D()
    #
    #xd, zd = 6.0, 10.0
    #nx, nz = 100, 50
    #scale = 20.0
    #x, z = np.linspace(-xd, xd, nx), np.linspace(-zd, zd, nz)
    #xx, zz = np.meshgrid(x, z)
    #y = (scale * np.sin(1.0 * xx) * scale * np.cos(0.4 * zz) / 2.0)
    #app.load_numpy_array(x, y, z)
    
    # using saved numpy data
    data = np.load('./data/spect_data.npy')
    # flip y axis
    data = np.flip(data, axis=0)
    data = data[:, -data.shape[0]:]
    import matplotlib.pyplot as plt
    plt.imshow(data)
    plt.show()
    print(data.shape)
    #x = np.linspace(-1, 1, data.shape[0])
    #y = np.linspace(-1, 1, data.shape[0])
    #app.load_numpy_array(data, x, y, 'spect_func')
    app.load_numpy_array(data, func_id='spect_func')
    
    #
    app.run()

