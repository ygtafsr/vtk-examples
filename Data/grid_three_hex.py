"""
This module created to be used for interaction examples to isolate
data representation layer.
"""

import numpy as np

from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray
)

from vtkmodules.vtkCommonDataModel import (
    VTK_HEXAHEDRON
)

# ------------------------------------------
# ---------- DATA MODEL --------------------
# ------------------------------------------
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

grid = UnstructuredGrid(points=points, cells=(vtk_cell_types, cells))

