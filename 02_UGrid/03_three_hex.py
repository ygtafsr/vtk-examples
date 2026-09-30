import numpy as np

# VTK native OpenGL backend
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

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

# -------------------------
# VTK rendering pipeline
# -------------------------

mapper = vtkDataSetMapper(input_data=grid)

actor = vtkActor(mapper=mapper)
#actor.property.representation = VTK_WIREFRAME
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1
actor.property.color = colors.warm_grey

# ============================================================
# Renderer
# ============================================================

renderer = vtkRenderer()

renderer.AddActor(actor)
renderer.background = colors.white
renderer.ResetCamera()

# ============================================================
# Render Window
# ============================================================

render_window = vtkRenderWindow(size=(1000, 700))
render_window.AddRenderer(renderer)

# ============================================================
# Interactor
# ============================================================

interactor = vtkRenderWindowInteractor(render_window=render_window)

# ============================================================
# Start
# ============================================================

render_window.Render()
interactor.Start()