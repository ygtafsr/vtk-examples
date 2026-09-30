
import numpy as np

# VTK native OpenGL backend
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util.numpy_support import numpy_to_vtk

from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    PolyData,
    CellArray
)

from vtkmodules.vtkCommonDataModel import (
    VTK_QUAD
)

from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkFiltersCore import vtkGlyph3D

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor
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

# ------------------------------------------------------------
# Vector data
# ------------------------------------------------------------

vectors = np.array([
    [1.0, 0.0, 0.0],
    [0.0, 2.0, 0.0],
    [1.0, 1.0, 0.0],
    [-1.0, 0.5, 0.0],
    [1.0, 0.0, 0.0],
    [0.0, 2.0, 0.0],
    [1.0, 1.0, 0.0],
    [-1.0, 0.5, 0.0],
], dtype=np.float64)


input_data = PolyData(points=points)

# Add displacement to input_data
input_data.point_data["Displacement"] = vectors

# Make displacement the active vector field
input_data.point_data.SetActiveVectors("Displacement")

# ------------------------------------------------------------
# Glyph source
# ------------------------------------------------------------

cone = vtkConeSource(
    height=1.0,
    radius=0.2,
    resolution=20,
)

# ------------------------------------------------------------
# Glyph filter
# ------------------------------------------------------------

glyph = vtkGlyph3D(
    input_data=input_data,
    source_connection=cone.GetOutputPort(),
)

glyph.vector_mode = 1
glyph.scale_mode = 2
glyph.scale_factor = 0.5

# ============================================================
# VTK rendering pipeline
# ============================================================

mapper = vtkDataSetMapper(input_data=grid)
actor = vtkActor(mapper=mapper)
actor.property.edge_visibility = True
actor.property.edge_color = (0.1, 0.1, 0.1)
actor.property.line_width = 1

mapper = vtkDataSetMapper(input_data=grid)
poly_mapper = vtkPolyDataMapper(input_connection=glyph.GetOutputPort())
poly_actor = vtkActor(mapper=poly_mapper)

# ============================================================
# Renderer
# ============================================================

renderer = vtkRenderer()

renderer.AddActor(actor)
renderer.AddActor(poly_actor)
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
