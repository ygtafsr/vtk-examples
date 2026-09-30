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
# PointData
# ============================================================

# Method 1 :: Assigning Data into ugrid point data property (Implicit PointData)

scalar = np.array([
    0.0,  # point 0
    1.0,  # point 1
    2.0,  # point 2
    3.0,  # point 3
    0.0,  # point 4
    1.0,  # point 5
    2.0,  # point 6
    3.0,  # point 7
])

grid.point_data["Scalar"] = scalar

# We can get point_data "Scalar" by a point id
print(type(grid.point_data["Scalar"]))  # <class 'vtkmodules.util.data_model.PointData'>
print(grid.point_data["Scalar"])
print(grid.point_data["Scalar"][3])

# Method 2 :: Create a PointData object explicitly

poly_data = PolyData(points=points)
poly_data.point_data["Scalar-2"] = scalar   
print(poly_data.point_data["Scalar-2"][5])

