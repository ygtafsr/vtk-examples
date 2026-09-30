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
    VTK_TRIANGLE
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
    [5.0, 0.0, 0.0],  # node 1 - bottom-right-front
    [0.0, 5.0, 0.0],  # node 2 - bottom-right-back
    [5.0, 5.0, 0.0],  # node 3 - bottom-left-back
    [10.0, 5.0, 0.0],  # node 4 - top-left-front
], dtype=np.float64)

points = Points(data=coordinates)

# ============================================================
# Create vtkCellArray
# ============================================================

# Connectivity array: node indices of the hexahedron
connectivity = np.array(
    [
        [0, 1, 2],
        [1, 3, 2],
        [1, 4, 3]
    ], dtype=np.int64)

cell_types = np.array(
    [
        [VTK_TRIANGLE],
        [VTK_TRIANGLE],
        [VTK_TRIANGLE]
    ], dtype=np.uint8)

vtk_cell_types = numpy_to_vtk(cell_types, deep=True)

offsets = np.array([0, 3, 6, 9], dtype=np.int64)

cells = CellArray(offsets=offsets, connectivity=connectivity.ravel())

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
actor.property.edge_color = (0.1, 0.1, 0.1)
actor.property.line_width = 1

# ============================================================
# Renderer
# ============================================================

renderer = vtkRenderer()

renderer.AddActor(actor)
renderer.SetBackground(0.15, 0.15, 0.15)
renderer.ResetCamera()


# ============================================================
# Render Window
# ============================================================

render_window = vtkRenderWindow()

render_window.AddRenderer(renderer)
render_window.SetSize(1000, 700)


# ============================================================
# Interactor
# ============================================================

interactor = vtkRenderWindowInteractor()

interactor.SetRenderWindow(render_window)


# ============================================================
# Start
# ============================================================

render_window.Render()
interactor.Start()

