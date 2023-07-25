
import numpy as np
import glm
from numba import njit


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
        # rescale everything into (-5, 5) range for all axes
        self.x = x.copy()
        self.y = y.copy()
        self.z = z.copy()
        self.nx, self.nz = self.x.shape[0], self.z.shape[0]
        assert((self.nx * self.nz) == self.y.size)        
        self.vertex_data = self.get_vertex_data()
        
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
        vertex_data = np.array(vertices, dtype='f4')
        colors = np.array([0.0, 0.0, 1.0, 1.0, 2.0, 2.0], dtype='f4').reshape(-1, 1)
        vertex_data = np.hstack([vertex_data, colors])
        
        return vertex_data

