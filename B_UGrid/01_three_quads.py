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
    VTK_QUAD
)

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)


coordinates = np.array([
    [0.0, 0.0, 0.0],    # point 0
    [5.0, 0.0, 0.0],    # point 1
    [10.0, 0.0, 0.0],   # point 2
    [15.0, 0.0, 0.0],   # point 3
    [0.0, 5.0, 0.0],    # point 4
    [5.0, 5.0, 0.0],    # point 5
    [10.0, 5.0, 0.0],   # point 6
    [15.0, 5.0, 0.0],   # point 7
], dtype=np.float64)

points = Points(data=coordinates)

# ============================================================
# Create vtkCellArray
# ============================================================

connectivity = np.array(
    [
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
    ], dtype=np.int64)

connectivity_flat = connectivity.ravel()

cell_types = np.array(
    [
        [VTK_QUAD],
        [VTK_QUAD],
        [VTK_QUAD],
    ], dtype=np.uint8)

vtk_cell_types = numpy_to_vtk(cell_types, deep=True)

offsets = np.array([0, 4, 8, 12], dtype=np.int64)

cells = CellArray(offsets=offsets, connectivity=connectivity_flat)

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