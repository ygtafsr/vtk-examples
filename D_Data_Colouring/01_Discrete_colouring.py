
"""
Reference:
https://vtk.org/doc/nightly/html/classvtkDiscretizableColorTransferFunction.html

a combination of vtkColorTransferFunction and vtkLookupTable.

This is a cross between a vtkColorTransferFunction and a vtkLookupTable selectively combining the functionality of 
both. This class is a vtkColorTransferFunction allowing users to specify the RGB control points that control 
the color transfer function. At the same time, by setting Discretize to 1 (true), one can force the transfer function
to only have NumberOfValues discrete colors.
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

from vtkmodules.vtkCommonCore import vtkLookupTable

from vtkmodules.vtkRenderingCore import (
    vtkDiscretizableColorTransferFunction,
    vtkPolyDataMapper,
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
# Create Scalar Data
# -------------------------

stress = np.array(
    [100, 150, 200, 250,
     300, 350, 400, 450],
    dtype=np.float64,
)

grid.point_data["von_mises_stress"] = stress
print(grid.point_data["von_mises_stress"][1])

### !!! Set Active Scalars !!!
grid.point_data.SetActiveScalars("von_mises_stress")

# ============================================================
# 5. Discrete colour transfer function
# ============================================================

color_transfer_function = vtkDiscretizableColorTransferFunction()

color_transfer_function.DiscretizeOn()
color_transfer_function.SetNumberOfValues(3)

# Scalar 0 -> red
color_transfer_function.AddRGBPoint(
    0.0, 1.0, 0.0, 0.0
)

# Scalar 1 -> green
color_transfer_function.AddRGBPoint(
    1.0, 0.0, 1.0, 0.0
)

# Scalar 2 -> blue
color_transfer_function.AddRGBPoint(
    2.0, 0.0, 0.0, 1.0
)

color_transfer_function.Build()

# -------------------------
# VTK rendering pipeline
# -------------------------

mapper = vtkDataSetMapper(input_data=grid)
#mapper.scalar_visibility = True
mapper.scalar_range = (0.0, 2.0)
mapper.lookup_table = color_transfer_function

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
