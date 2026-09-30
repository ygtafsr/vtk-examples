
# https://chatgpt.com/share/6a884781-7830-83ed-8ff7-25f5c1d4cac7

'''
For an FEA application, I would not make every component a separate vtkUnstructuredGrid by default.

A better model is:

One global vtkUnstructuredGrid representing the FE mesh + cell/point attributes describing components, 
elements, materials, sets, etc.

the component information is an attribute of the cells, rather than a different mesh.
'''
import numpy as np

# VTK native OpenGL backend
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2


from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray
)

from vtkmodules.vtkCommonDataModel import (
    VTK_HEXAHEDRON
)

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

# Define the 8 corner points of a unit hexahedron
# Bottom face (z=0): nodes 0,1,2,3
# Top face (z=1): nodes 4,5,6,7
coordinates = np.array([
    [0.0, 0.0, 0.0],  # node 0 - bottom-left-front
    [1.0, 0.0, 0.0],  # node 1 - bottom-right-front
    [1.0, 1.0, 0.0],  # node 2 - bottom-right-back
    [0.0, 1.0, 0.0],  # node 3 - bottom-left-back
    [0.0, 0.0, 1.0],  # node 4 - top-left-front
    [1.0, 0.0, 1.0],  # node 5 - top-right-front
    [1.0, 1.0, 1.0],  # node 6 - top-right-back
    [0.0, 1.0, 1.0],  # node 7 - top-left-back
    [1.0, 0.0, 0.0],  # node 0 - bottom-left-front
    [2.0, 0.0, 0.0],  # node 1 - bottom-right-front
    [2.0, 1.0, 0.0],  # node 2 - bottom-right-back
    [1.0, 1.0, 0.0],  # node 3 - bottom-left-back
    [1.0, 0.0, 1.0],  # node 4 - top-left-front
    [2.0, 0.0, 1.0],  # node 5 - top-right-front
    [2.0, 1.0, 1.0],  # node 6 - top-right-back
    [1.0, 1.0, 1.0],  # node 7 - top-left-back
    [2.0, 0.0, 0.0],  # node 0 - bottom-left-front
    [3.0, 0.0, 0.0],  # node 1 - bottom-right-front
    [3.0, 1.0, 0.0],  # node 2 - bottom-right-back
    [2.0, 1.0, 0.0],  # node 3 - bottom-left-back
    [2.0, 0.0, 1.0],  # node 4 - top-left-front
    [3.0, 0.0, 1.0],  # node 5 - top-right-front
    [3.0, 1.0, 1.0],  # node 6 - top-right-back
    [2.0, 1.0, 1.0],  # node 7 - top-left-back
], dtype=np.float64)

points = Points(data=coordinates)

# ============================================================
# Create vtkCellArray
# ============================================================

# Connectivity array: node indices of the hexahedron
connectivity = np.arange(24, dtype=np.int64)

cell_types = np.array(
    [
        [VTK_HEXAHEDRON],
        [VTK_HEXAHEDRON],
        [VTK_HEXAHEDRON]
    ], dtype=np.uint8)

vtk_cell_types = numpy_to_vtk(cell_types, deep=True)

offsets = np.array([0, 8, 16, 24], dtype=np.int64)

cells = CellArray(offsets=offsets, connectivity=connectivity)

# ============================================================
# Create vtkUnstructuredGrid
# ============================================================

grid = UnstructuredGrid(points=points, cells=(vtk_cell_types, cells))

# ============================================================
# FEA attributes
# ============================================================

grid.point_data["NodeId"] = np.array([
    1, 2, 3, 4,
    5, 6, 7, 8,
])

grid.cell_data["ElementId"] = np.array([
    101,
    102,
    103,
])

grid.cell_data["ComponentId"] = np.array([
    1,
    1,
    2,
])

"""
Your mesh now knows:

Element    Component
--------------------
101        1
102        1
103        2

"""