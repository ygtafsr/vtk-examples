
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

from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor

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


#### Lookup Table ###
lut = vtkLookupTable()

lut.SetNumberOfTableValues(5)
lut.SetRange(0.0, 500.0)

lut.SetTableValue(0, 0.0, 0.0, 1.0, 1.0)  # blue
lut.SetTableValue(1, 0.0, 1.0, 1.0, 1.0)  # cyan
lut.SetTableValue(2, 0.0, 1.0, 0.0, 1.0)  # green
lut.SetTableValue(3, 1.0, 1.0, 0.0, 1.0)  # yellow
lut.SetTableValue(4, 1.0, 0.0, 0.0, 1.0)  # red

lut.Build()

### Scalar Bar ###
scalar_bar = vtkScalarBarActor()
scalar_bar.lookup_table = lut
scalar_bar.title = "Von Mises Stress"
scalar_bar.number_of_labels = 6
scalar_bar.position = (0.85, 0.1)
#scalar_bar.orientation = "Vertical"
scalar_bar.width = 0.12
scalar_bar.height = 0.8

# -------------------------
# VTK rendering pipeline
# -------------------------

mapper = vtkDataSetMapper(input_data=grid)
mapper.scalar_visibility = True
mapper.scalar_range = (stress.min(), stress.max())

mapper.lookup_table = lut

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
renderer.AddActor(scalar_bar)
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
