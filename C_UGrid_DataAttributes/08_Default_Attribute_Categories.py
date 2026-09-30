"""
vtkDataSetAttributes knows that some arrays have a particular semantic role.

"Temperature"      → Scalars
"Displacement"     → Vectors
"SurfaceNormal"    → Normals
"Stress"           → Tensors
"""

import numpy as np

from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray,
    PolyData
)

from vtkmodules.vtkCommonDataModel import VTK_QUAD


# ============================================================
# Points
# ============================================================

coordinates = np.array([
    [0.0, 0.0, 0.0],   # point 0
    [5.0, 0.0, 0.0],   # point 1
    [10.0, 0.0, 0.0],  # point 2
    [15.0, 0.0, 0.0],  # point 3
    [0.0, 5.0, 0.0],   # point 4
    [5.0, 5.0, 0.0],   # point 5
    [10.0, 5.0, 0.0],  # point 6
    [15.0, 5.0, 0.0],  # point 7
], dtype=np.float64)

points = Points(data=coordinates)

# ============================================================
# Cells
# ============================================================

connectivity = np.array([
    [0, 1, 5, 4],
    [1, 2, 6, 5],
    [2, 3, 7, 6],
], dtype=np.int64)

cell_types = np.array([
    VTK_QUAD,
    VTK_QUAD,
    VTK_QUAD,
], dtype=np.uint8)

vtk_cell_types = numpy_to_vtk(
    cell_types,
    deep=True,
)

offsets = np.array(
    [0, 4, 8, 12],
    dtype=np.int64,
)

cells = CellArray(
    offsets=offsets,
    connectivity=connectivity.ravel(),
)

# ============================================================
# UnstructuredGrid
# ============================================================

grid = UnstructuredGrid(
    points=points,
    cells=(vtk_cell_types, cells),
)


# ============================================================
# Default Attribute Categories
# ============================================================

grid.point_data["Temperature"] = np.arange(5,13)
print(type(grid.point_data["Temperature"]))

grid.point_data["Displacement"] = np.arange(0,24).reshape(8,3)
print(type(grid.point_data["Displacement"]))

