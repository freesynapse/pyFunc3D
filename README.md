# spectrogram3D
Python OpenGL (modernGL) implementation of 3d function plotting. A basic lighting model
is implemented, as well as the use of barycentric coordinates for plotting a quad 
wireframe. Normals are computed using central differences.

*** TODO ***
* loading options:
    1. text file containing a function expression and domain (SymPy?).
    2. text file containing height coordinates.
    3. image file.
    4. from a numpy array
    The different loading options are implemented as class methods.
* storing y values as a texture
* domain for plotting, which can be different from the texture domain (for spectrograms
  over longer time periods).
* debug rendering of light source

*** IMPLEMENTED ***
* axes

