
import numpy as np
import glm
from numba import njit
from settings import *
from matplotlib import colors, cm

#
class BaseMesh:
    def __init__(self):
        self.vertex_data : np.array = None
    
    def get_vertex_data(self): ...

#
class DebugCubeMesh(BaseMesh):
    def __init__(self):
        super().__init__()
        self.vertex_data = self.get_vertex_data()
    
    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    def get_vertex_data(self):
        vertices = [(-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1),
                    (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (1, 1, -1)]
        indices = [(0, 2, 3), (0, 1, 2),
                   (1, 7, 2), (1, 6, 7),
                   (6, 5, 4), (4, 7, 6),
                   (3, 4, 5), (3, 5, 0),
                   (3, 7, 4), (3, 2, 7),
                   (0, 6, 1), (0, 5, 6)]
        vertex_data = self.get_data(vertices, indices)
        
        normals = [(0, 0, 1) * 6,
                   (1, 0, 0) * 6,
                   (0, 0,-1) * 6,
                   (-1,0, 0) * 6,
                   (0, 1, 0) * 6,
                   (0,-1, 0) * 6]
        normals = np.array(normals, dtype='f4').reshape(36, 3)
        
        vertex_data = np.hstack([vertex_data, normals])
        return vertex_data

#
class Func3DMesh(BaseMesh):
    def __init__(self, 
                 x : np.ndarray, 
                 y : np.ndarray,    # the data
                 z : np.ndarray):
        super().__init__()
        
        # if x or z is None
        if x == None:
            x = np.linspace(-1, 1, y.shape[1])
        if z == None:
            z = np.linspace(-1, 1, y.shape[0])  
        #
        self.x, self.y, self.z = x.copy(), y.copy(), z.copy()
        # store limits for later access
        self.xlim = (self.x[0], self.x[-1])
        self.ylim = (np.min(self.y), np.max(self.y))
        self.zlim = (self.z[0], self.z[-1])
        
        # interpolate the axis of the lowest resolution to match the highest
        if x.shape != z.shape:
            print('interpolating function to new axes... ', end='')
            # y is of shape (z, x), so will have to be interpolated to fit the new shape
            max_dim = max(z.shape[0], x.shape[0])
            y_interp = np.zeros(shape=(max_dim, max_dim))
            #
            if x.shape[0] < z.shape[0]:
                self.x = np.linspace(self.xlim[0], self.xlim[1], max_dim)
                print(f'\tnew x shape = {self.x.shape}')
                # y is interpolated over new shape of axis=1 (column-wise)
                for i in np.arange(self.x.shape[0]):
                    y_row_i = np.interp(x=self.x, xp=x, fp=self.y[i,:])
                    y_interp[i,:] = y_row_i
            #    
            else: # z.shape[0] < x.shape[0]
                self.z = np.linspace(self.zlim[0], self.zlim[1], max_dim)
                # y is interpolated over new shape of axis=0 (row-wise)
                for i in np.arange(self.z.shape[0]):
                    y_col_i = np.interp(x=self.z, xp=z, fp=self.y[:,i])
                    y_interp[:,i] = y_col_i
            #                    
            self.y = y_interp
            print('done.')
            
        # rescale everything
        self.x = MESH_SCALE[0] * (self.x / np.max(np.abs(self.x)))
        self.y = MESH_SCALE[1] * (self.y / np.max(np.abs(self.y)))
        self.z = MESH_SCALE[2] * (self.z / np.max(np.abs(self.z)))
        
        # find ylim
        self.ylim = (np.min(self.y.flatten()), np.max(self.y.flatten()))
            
        self.nx, self.nz = self.x.shape[0], self.z.shape[0]
        assert((self.nx * self.nz) == self.y.size)
        self.vertex_data = self.get_vertex_data()
        print(f'vertices: {self.vertex_data.shape[0]}, triangles: {self.vertex_data.shape[0]//3}')
        
    #
    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    #
    #@njit
    def get_vertex_data(self):
        x, z = self.x, self.z
        nx, nz = self.nx, self.nz
        vertices, indices, normals = [], [], []
        y1d = self.y.flatten()

        # vertices
        for i in np.arange(nz):
            for j in np.arange(nx):
                k = i * nx + j
                vertices.append((x[j], y1d[k], z[i]))
                
        # calculate indices (both for vertices and normals)
        for i in np.arange(nz-1):
            for j in np.arange(nx-1):
                indices.append((i * nx + j, (i + 1) * nx + j, i * nx + j + 1))
                indices.append((i * nx + j + 1, (i + 1) * nx + j, (i + 1) * nx + j + 1))
        
        # calculate normals
        for i in np.arange(nz):
            for j in np.arange(nx):
                k = i * nx + j
                
                L = i * nx + j - 1
                R = i * nx + j + 1
                U = (i - 1) * nx + j
                D = (i + 1) * nx + j
                
                if i > 0 and i < (nz-1) and j > 0 and j < (nx - 1):
                    # L -> P :  [ x - (x-1),  f(x,z) - f(x-1,z),  z - z ] =
                    #           [ 1.0, f(x,z) - f(x-1,z), 0.0 ]
                    LP = glm.vec3(x[j]-x[j-1], y1d[k]-y1d[L], 0.0)
                    # P -> R :  [ (x+1) - x,  f(x+1,z) - f(x,z),  z - z ] =
                    #           [ 1.0, f(x+1,z) - f(x,z), 0.0 ]
                    PR = glm.vec3(x[j+1]-x[j], y1d[R]-y1d[k], 0.0)
                    # U -> P :  [ x - x,  f(x,z) - f(x,z-1),  z - (z-1) ] =
                    #           [ 0.0, f(x,z) - f(x,z-1), 1.0 ]
                    UP = glm.vec3(0.0, y1d[k]-y1d[U], z[i]-z[i-1])
                    # P -> D :  [ x - x,  f(x,z+1) - f(x,z),  (z+1) - z ] =
                    #           [ 0.0, f(x,z+1) - f(x,z), 1.0 ]
                    PD = glm.vec3(0.0, y1d[D]-y1d[k], z[i+1]-z[i])

                    UP_LP = glm.cross(UP, LP)
                    UP_PR = glm.cross(UP, PR)
                    PD_LP = glm.cross(PD, LP)
                    PD_PR = glm.cross(PD, PR)

                    sum = UP_LP + UP_PR + PD_LP + PD_PR
                
                # z borders, excluding corners
                elif (i > 0 and i < (nz-1) and (j == 0 or j == (nx-1))):
                    if (j == 0):    PX = glm.vec3(x[1]-x[0], y1d[R]-y1d[k], 0.0)
                    else:           PX = glm.vec3(x[nx-1]-x[nx-2], y1d[k]-y1d[L], 0.0)

                    UP = glm.vec3(0.0, y1d[k]-y1d[U], z[i]-z[i-1])
                    PD = glm.vec3(0.0, y1d[D]-y1d[k], z[i+1]-z[i])

                    UP_PX = glm.cross(UP, PX)
                    PD_PX = glm.cross(PD, PX)

                    sum = UP_PX + PD_PX

                # x borders, excluding corners
                elif (j > 0 and j < (nx-1) and (i == 0 or i == (nz-1))):
                    if (i == 0):    PZ = glm.vec3(0.0, y1d[D]-y1d[k], z[1]-z[0])
                    else:           PZ = glm.vec3(0.0, y1d[k]-y1d[U], z[nz-1]-z[nz-2])

                    PR = glm.vec3(x[j+1]-x[j], y1d[R]-y1d[k], 0.0)
                    LP = glm.vec3(x[j]-x[j-1], y1d[k]-y1d[L], 0.0)

                    PZ_LP = glm.cross(PZ, LP)
                    PZ_PR = glm.cross(PZ, PR)

                    sum = PZ_LP + PZ_PR

                # corners
                elif (i == 0 and j == 0):
                    PR = glm.vec3(x[1]-x[0], y1d[R]-y1d[k], 0.0)
                    PD = glm.vec3(0.0, y1d[D]-y1d[k], z[1]-z[0])
                    sum = glm.cross(PD, PR)
                elif (i == 0 and j == (nx-1)):
                    LP = glm.vec3(x[nx-1]-x[nx-2], y1d[k]-y1d[L], 0.0)
                    PD = glm.vec3(0.0, y1d[D]-y1d[k], z[1]-z[0])
                    sum = glm.cross(PD, LP)
                elif (i == (nz-1) and j == 0):
                    PR = glm.vec3(x[1]-x[0], y1d[R]-y1d[k], 0.0)
                    UP = glm.vec3(0.0, y1d[k]-y1d[U], z[nz-1]-z[nz-2])
                    sum = glm.cross(UP, PR)
                elif (i == (nz-1) and j == (nx-1)):
                    LP = glm.vec3(x[nx-1]-x[nx-2], y1d[k]-y1d[L], 0.0)
                    UP = glm.vec3(0.0, y1d[k]-y1d[U], z[nz-1]-z[nz-2])
                    sum = glm.cross(UP, LP)

                # set vertex normal
                normals.append(glm.normalize(sum))

        # pack vertex data
        vertex_data = self.get_data(vertices, indices)

        # add barycentric coordinates
        barycentric = []
        Q = 1   # remove diagnoal edge?
        for i in range(vertex_data.shape[0]//3):
            even = i % 2
            if even:
                barycentric.append((1, 0, 0))
                barycentric.append((0, 1, Q))
                barycentric.append((0, 0, 1))
            else:
                barycentric.append((1, 0, 0))
                barycentric.append((Q, 1, 0))
                barycentric.append((0, 0, 1))
        barycentric = np.array(barycentric, dtype='f4')
        
        #barycentric = np.tile([1, 1, 1, 0, 0, 0], reps=vertex_data.shape[0]//6)
        #barycentric = np.array(barycentric, dtype='uint8').reshape(-1, 1)
                
        # pack data for GPU upload
        normal_data = self.get_data(normals, indices)
        vertex_data = np.hstack([vertex_data, normal_data])
        vertex_data = np.hstack([vertex_data, barycentric])
        
        # add linear color map -- map to cm.jet on y value
        #crange = np.linspace(self.ylim[0], self.ylim[1], 255)
        norm_colors = colors.Normalize(vmin=self.ylim[0], vmax=self.ylim[1], clip=True)
        color_mapper = cm.ScalarMappable(norm=norm_colors, cmap=cm.jet)
        # get vec3 per vertex y value (currently in vertex_data[:, 1])
        color_data = np.array(color_mapper.to_rgba(vertex_data[:, 1])[:, :3], dtype='f4')
        # add color to vertex_data
        vertex_data = np.hstack([vertex_data, color_data])
        
        return vertex_data

#
class AxesMesh(BaseMesh):
    def __init__(self, xlim, ylim, zlim):
        super().__init__()
        self.xlim, self.ylim, self.zlim = xlim, ylim, zlim
        self.vertex_data = self.get_vertex_data()

    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    #
    def get_vertex_data(self):
        o = glm.vec3(self.xlim[0], self.ylim[0], self.zlim[0])
        vertices = [(o.x, o.y, o.z), (self.xlim[1], o.y, o.z), 
                    (o.x, o.y, o.z), (o.x, self.ylim[1], o.z),
                    (o.x, o.y, o.z), (o.x, o.y, self.zlim[1])]
        #o = glm.vec3(0, 2, 0)
        #vertices = [(self.xlim[0], o.y, o.z), (self.xlim[1], o.y, o.z), 
        #            (o.x, self.ylim[0], o.z), (o.x, self.ylim[1], o.z),
        #            (o.x, o.y, self.zlim[0]), (o.x, o.y, self.zlim[1])]
        vertex_data = np.array(vertices, dtype='f4')
        colors = np.array([0.0, 0.0, 1.0, 1.0, 2.0, 2.0], dtype='f4').reshape(-1, 1)
        vertex_data = np.hstack([vertex_data, colors])
        
        return vertex_data

