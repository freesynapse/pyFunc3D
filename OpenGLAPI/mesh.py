
import numpy as np
import glm
from numba import njit


#
class BaseMesh:
    def __init__(self):
        self.ctx = None
        self.vertex_data : np.array = None
    
    def get_vertex_data(self): ...

#
class DebugCubeMesh(BaseMesh):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
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
    def __init__(self, ctx, data : np.ndarray, x_linspace : np.ndarray, 
                 z_linspace : np.ndarray):
        super().__init__()
        self.ctx = ctx
        self.Y = data.copy()
        self.X = x_linspace.copy()
        self.Z = z_linspace.copy()
        self.nx, self.nz = self.X.shape[0], self.Z.shape[0]
        assert((self.nx * self.nz) == self.Y.size)        
        self.vertex_data = self.get_vertex_data()
        
    #
    @staticmethod
    def get_data(vertices, indices):
        data = [vertices[ind] for triangle in indices for ind in triangle]
        return np.array(data, dtype='f4')

    #
    #@njit
    def get_vertex_data(self):
        # create a surface to play with
        #d = 6.0
        #nx, nz = 100, 100
        #x, z = np.linspace(-d, d, nx), np.linspace(-d, d, nz)
        #X, Z = np.meshgrid(x, z)
        #Y = (np.sin(2.0 * X) * np.cos(1.0 * Z) / 2.0)
        #Y = (np.sin(0.0 * X) * np.cos(0.0 * Z) / 2.0)
        x, z = self.X, self.Z
        nx, nz = self.nx, self.nz
        vertices, indices, normals = [], [], []
        Y1d = self.Y.flatten()

        # vertices
        for i in np.arange(nz):
            for j in np.arange(nx):
                k = i * nx + j
                vertices.append((x[j], Y1d[k], z[i]))
                
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
                    LP = glm.vec3(x[j]-x[j-1], Y1d[k]-Y1d[L], 0.0)
                    # P -> R :  [ (x+1) - x,  f(x+1,z) - f(x,z),  z - z ] =
                    #           [ 1.0, f(x+1,z) - f(x,z), 0.0 ]
                    PR = glm.vec3(x[j+1]-x[j], Y1d[R]-Y1d[k], 0.0)
                    # U -> P :  [ x - x,  f(x,z) - f(x,z-1),  z - (z-1) ] =
                    #           [ 0.0, f(x,z) - f(x,z-1), 1.0 ]
                    UP = glm.vec3(0.0, Y1d[k]-Y1d[U], z[i]-z[i-1])
                    # P -> D :  [ x - x,  f(x,z+1) - f(x,z),  (z+1) - z ] =
                    #           [ 0.0, f(x,z+1) - f(x,z), 1.0 ]
                    PD = glm.vec3(0.0, Y1d[D]-Y1d[k], z[i+1]-z[i])

                    UP_LP = glm.cross(UP, LP)
                    UP_PR = glm.cross(UP, PR)
                    PD_LP = glm.cross(PD, LP)
                    PD_PR = glm.cross(PD, PR)

                    sum = UP_LP + UP_PR + PD_LP + PD_PR
                
                # z borders, excluding corners
                elif (i > 0 and i < (nz-1) and (j == 0 or j == (nx-1))):
                    if (j == 0):    PX = glm.vec3(x[1]-x[0], Y1d[R]-Y1d[k], 0.0)
                    else:           PX = glm.vec3(x[nx-1]-x[nx-2], Y1d[k]-Y1d[L], 0.0)

                    UP = glm.vec3(0.0, Y1d[k]-Y1d[U], z[i]-z[i-1])
                    PD = glm.vec3(0.0, Y1d[D]-Y1d[k], z[i+1]-z[i])

                    UP_PX = glm.cross(UP, PX)
                    PD_PX = glm.cross(PD, PX)

                    sum = UP_PX + PD_PX

                # x borders, excluding corners
                elif (j > 0 and j < (nx-1) and (i == 0 or i == (nz-1))):
                    if (i == 0):    PZ = glm.vec3(0.0, Y1d[D]-Y1d[k], z[1]-z[0])
                    else:           PZ = glm.vec3(0.0, Y1d[k]-Y1d[U], z[nz-1]-z[nz-2])

                    PR = glm.vec3(x[j+1]-x[j], Y1d[R]-Y1d[k], 0.0)
                    LP = glm.vec3(x[j]-x[j-1], Y1d[k]-Y1d[L], 0.0)

                    PZ_LP = glm.cross(PZ, LP)
                    PZ_PR = glm.cross(PZ, PR)

                    sum = PZ_LP + PZ_PR

                # corners
                elif (i == 0 and j == 0):
                    PR = glm.vec3(x[1]-x[0], Y1d[R]-Y1d[k], 0.0)
                    PD = glm.vec3(0.0, Y1d[D]-Y1d[k], z[1]-z[0])
                    sum = glm.cross(PD, PR)
                elif (i == 0 and j == (nx-1)):
                    LP = glm.vec3(x[nx-1]-x[nx-2], Y1d[k]-Y1d[L], 0.0)
                    PD = glm.vec3(0.0, Y1d[D]-Y1d[k], z[1]-z[0])
                    sum = glm.cross(PD, LP)
                elif (i == (nz-1) and j == 0):
                    PR = glm.vec3(x[1]-x[0], Y1d[R]-Y1d[k], 0.0)
                    UP = glm.vec3(0.0, Y1d[k]-Y1d[U], z[nz-1]-z[nz-2])
                    sum = glm.cross(UP, PR)
                elif (i == (nz-1) and j == (nx-1)):
                    LP = glm.vec3(x[nx-1]-x[nx-2], Y1d[k]-Y1d[L], 0.0)
                    UP = glm.vec3(0.0, Y1d[k]-Y1d[U], z[nz-1]-z[nz-2])
                    sum = glm.cross(UP, LP)

                # set vertex normal
                normals.append(glm.normalize(sum))

        # pack vertex data
        vertex_data = self.get_data(vertices, indices)
        # add barycentric coordinates
        #  -> for TRI order 0, 1, 2, 2, 3, 0 this corresponds to 0, 1, 2, 2, 1, 0
        ##vertex_data[:, 3] = np.tile([0, 1, 2, 2, 1, 0], reps=vertex_data.shape[0]//6)
        #
        barycentric = []
        Q = 1   # remove diagnoal edge?
        for i in range(vertex_data.shape[0]//3):
            even = i % 2
            if even:
                barycentric.append((1, 0, 0))
                barycentric.append((0, 1, 1))
                barycentric.append((0, 0, 1))
            else:
                barycentric.append((1, 0, 0))
                barycentric.append((1, 1, 0))
                barycentric.append((0, 0, 1))
        barycentric = np.array(barycentric, dtype='f4')
        
        #barycentric = np.tile([1, 1, 1, 0, 0, 0], reps=vertex_data.shape[0]//6)
        #barycentric = np.array(barycentric, dtype='uint8').reshape(-1, 1)
        
        # pack data for GPU upload
        normal_data = np.array(self.get_data(normals, indices), dtype='f4')
        vertex_data = np.hstack([vertex_data, normal_data])
        vertex_data = np.hstack([vertex_data, barycentric])
        #
        return vertex_data