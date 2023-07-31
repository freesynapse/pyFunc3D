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
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE | mgl.BLEND)
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
        self.mousewheel_event :pg.event = None
        
        self.is_running = True
        self.is_loaded = False
        
        self.on_init()
        
        print(f'Core modules initialized in {(time.perf_counter_ns() - t0)/1e6} ms.')
    
    #
    def on_init(self):
        self.shader_manager = ShaderManager(self.ctx)
        self.camera_orbit = OrbitCamera(self, position=(-3.6, 0.5, -4.4), x_angle=230, 
                                        y_angle=85)
        self.camera_perspective = PerspectiveCamera(self, x_angle=0, y_angle=0)
        self.camera = self.camera_orbit
        self.camera_orbit_current = True        # toggle for switching camera
        self.scene = Scene(self, self.camera)
        self.func3D_obj_id = ''                 # for later access through Scene
    #
    def load_data(self, 
                  data : np.array,
                  x : np.ndarray =np.array(None), 
                  y : np.ndarray =np.array(None), 
                  equal_axes : bool=True,   # if true, the data array is shrunk to 
                                            # (m x m), where m is min(dim(x), dim(y))
                  func_id : str=None):
        t0 = time.perf_counter_ns()
        self.func3D_obj_id = self.scene.add_data(x, data, y, equal_axes, func_id)
        self.scene.add_axes(self.func3D_obj_id)
        self.is_loaded = True
        print(f'Meshes created in {(time.perf_counter_ns() - t0)/1e6} ms.')
    
    #
    def handle_events(self):
        self.mousewheel_event = None
        for event in pg.event.get():
            if event.type == pg.QUIT: 
                self.is_running = False
            elif event.type == pg.MOUSEWHEEL:
                self.mousewheel_event = event
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.is_running = False
                # take screenshot
                if event.key == pg.K_z:
                    pg.image.save(self.surface, './screenshot.png')
                    print("saved screenshot to './screenshot.png'.")
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

    #examples = ['mp3', 'sine_func', 'eeg', 'essw']
    ex = 'essw'
    
    # -----------------------------------------------------------------------------------
    # use spectrum from ~/source/misc/music_visualizer (fft on music)
    # -----------------------------------------------------------------------------------
    if ex == 'mp3':
        with open('./data/mp3_spectrum.txt') as f:
            data = f.read()
        data = data.split('\n')[2:-2] # skip file headers etc
        # list in the form of 'step: x y z w ...'
        freqs = []
        for row in data:
            step = [float(val) for val in row.split(' ') if val != 'step:']
            freqs.append(step)
        freqs = np.array(freqs, dtype=np.float32)
        # remove data when FFT buffer not full
        freqs = freqs[40:,:]
        print(freqs.shape)
        #import matplotlib.pyplot as plt
        #fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 5))
        #ax0.imshow(freqs)
        #ax0.set_title('freqs')
        #ax1.imshow(freqs.T)
        #ax1.set_title('freqs.transpose()')
        #plt.show()

        app.load_data(freqs,
                      equal_axes=False, 
                      func_id='mp3')

    # -----------------------------------------------------------------------------------
    # make up a function
    # -----------------------------------------------------------------------------------
    elif ex == 'sine_func':
        xd, zd = 6.0, 10.0
        nx, nz = 100, 50
        scale = 20.0
        x, z = np.linspace(-xd, xd, nx), np.linspace(-zd, zd, nz)
        xx, zz = np.meshgrid(x, z)
        y = (scale * np.sin(1.0 * xx) * scale * np.cos(0.4 * zz) / 2.0)
        app.load_data(y, x, z, equal_axes=False, func_id='sine_func')
    
    # -----------------------------------------------------------------------------------
    # using saved numpy data
    # -----------------------------------------------------------------------------------
    elif ex == 'eeg':
        data = np.load('./data/spect_data.npy')
        data = np.load('/home/iomanip/documents/_BIOINFO--ML/_EXP/spectral_analysis/'
                       'dpss_test/spect_data.npy')
        # flip y axis
        data = np.flip(data, axis=0)
        print(data.shape)
        app.load_data(data, equal_axes=False, func_id='eeg')

    
    # -----------------------------------------------------------------------------------
    # load from image (cm.jet)
    # -----------------------------------------------------------------------------------
    elif ex == 'essw':
        import cv2
        from matplotlib import colormaps # colormaps['jet'], colormaps['turbo']
        from matplotlib.colors import LinearSegmentedColormap
        from matplotlib._cm import _jet_data
        
        def convert_jet_to_grey(img):
            """
            (for lossy compression (JPG), interpolates values to 'nearest' gray scale).
            """
            (height, width) = img.shape[:2]
        
            cm = LinearSegmentedColormap("jet", _jet_data, N=2**8)
            # cm = colormaps['turbo'] swap with jet if you use turbo colormap instead
        
            cm._init()  # Must be called first. cm._lut data field created here
        
            FLANN_INDEX_KDTREE = 1
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
            search_params = dict(checks=50)
            fm = cv2.FlannBasedMatcher(index_params, search_params)
        
            # JET, BGR order, excluding special palette values (>= 256)
            fm.add(255 * np.float32([cm._lut[:256, (2, 1, 0)]]))  # jet
            fm.train()
        
            # look up all pixels
            query = img.reshape((-1, 3)).astype(np.float32)
            matches = fm.match(query)
        
            # statistics: `result` is palette indices ("grayscale image")
            output = np.uint16([m.trainIdx for m in matches]).reshape(height, width)
            result = np.where(output < 256, output, 0).astype(np.uint8)
            # dist = np.uint8([m.distance for m in matches]).reshape(height, width)
        
            return result  # , dist uncomment if you wish accuracy image
        
        #
        data = cv2.imread('./data/essw.jpg', cv2.IMREAD_COLOR)
        data = data[10:-10:, 10:-10]
        
        data = convert_jet_to_grey(data).astype(dtype='f4')
        data /= 255.0
        print(data.shape)
        
        app.load_data(data, equal_axes=False, func_id='essw')
    
    #
    else:
        print('no data provided.')
        sys.exit(-1)
    #
    app.run()

