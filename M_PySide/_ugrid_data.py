import numpy as np

from vtkmodules.util import colors
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
)

coordinates = np.array([
    [0.0, 0.0, 0.0],  
    [1.0, 0.0, 0.0],  
    [1.0, 1.0, 0.0],  
    [0.0, 1.0, 0.0],  
    [0.0, 0.0, 1.0],  
    [1.0, 0.0, 1.0],  
    [1.0, 1.0, 1.0],  
    [0.0, 1.0, 1.0],  
    [1.0, 0.0, 0.0],  
    [2.0, 0.0, 0.0],  
    [2.0, 1.0, 0.0],  
    [1.0, 1.0, 0.0],  
    [1.0, 0.0, 1.0],  
    [2.0, 0.0, 1.0],  
    [2.0, 1.0, 1.0],  
    [1.0, 1.0, 1.0],  
    [2.0, 0.0, 0.0],  
    [3.0, 0.0, 0.0],  
    [3.0, 1.0, 0.0],  
    [2.0, 1.0, 0.0],  
    [2.0, 0.0, 1.0],  
    [3.0, 0.0, 1.0],  
    [3.0, 1.0, 1.0],  
    [2.0, 1.0, 1.0],  
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

mapper = vtkDataSetMapper(input_data=grid)

actor = vtkActor(mapper=mapper)
#actor.property.representation = VTK_WIREFRAME
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1
actor.property.color = colors.warm_grey