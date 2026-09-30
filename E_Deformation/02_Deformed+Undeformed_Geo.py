
"""
### deformation vs. displacement magnitude ###

There are actually two different things you may want to visualize.

    1) X_deformed = X + U  -> Use vtkWarpVecotr
    2) Displacement Magnitude -> Use a vector-magnitude operation and then color the mesh using that scalar.

Pipeline:

                 displacement
                     │
             ┌───────┴────────┐
             │                │
             ▼                ▼
      vtkWarpVector       vector norm
             │                │
             ▼                ▼
      deformed geometry   scalar magnitude
             │                │
             └───────┬────────┘
                     ▼
                   Mapper
                     │
                     ▼
                   Actor

This gives you the familiar FEA plot: deformed shape + displacement contour

"""


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

from vtkmodules.vtkFiltersGeneral import vtkWarpVector

from vtkmodules.vtkCommonCore import vtkLookupTable

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
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

# ============================================================
# FEA displacement
# ============================================================

displacement = np.array([
    [0.0, 0.0, 0.0],
    [0.1, 0.0, 0.0],
    [0.3, 0.0, 0.0],
    [0.6, 0.0, 0.0],

    [0.0, 0.2, 0.0],
    [0.1, 0.4, 0.0],
    [0.3, 0.7, 0.0],
    [0.6, 1.0, 0.0],
], dtype=np.float64)

# Add displacement to PointData
grid.point_data["Displacement"] = displacement

# Make displacement the active vector field
grid.point_data.SetActiveVectors("Displacement")

# ============================================================
# 5. Calculate displacement magnitude
# ============================================================

displacement_magnitude = np.linalg.norm(
    displacement,
    axis=1,
)

grid.point_data["Displacement_Magnitude"] = displacement_magnitude
grid.point_data.SetActiveScalars("Displacement_Magnitude")


# ============================================================
# Deform mesh
# ============================================================

warp = vtkWarpVector(
    input_data=grid
)

warp.scale_factor = 5.0

# ============================================================
# Lookup table for displacement magnitude
# ============================================================

lookup_table = vtkLookupTable()

lookup_table.SetNumberOfTableValues(256)

# Blue → red
lookup_table.SetHueRange(
    0.667,
    0.0,
)

lookup_table.SetRange(
    displacement_magnitude.min(),
    displacement_magnitude.max(),
)

lookup_table.Build()

# ============================================================
# Mapper
# ============================================================

mapper = vtkDataSetMapper(
    input_connection=warp.output_port
)

mapper.scalar_visibility = True

mapper.scalar_range = (
    displacement_magnitude.min(),
    displacement_magnitude.max(),
)

mapper.lookup_table = lookup_table

# ============================================================
# Actor
# ============================================================

actor = vtkActor(
    mapper=mapper
)

actor.property.edge_visibility = True
actor.property.edge_color = (0.1, 0.1, 0.1)
actor.property.line_width = 1.5

# ============================================================
# Renderer
# ============================================================

renderer = vtkRenderer()

renderer.SetBackground(
    0.15,
    0.15,
    0.15,
)

renderer.AddActor(actor)

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
