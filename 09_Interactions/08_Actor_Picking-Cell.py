"""
###################################################################################
# Example of vtk Actor -> vtkCameraOrientationWidget -> camera manipulation logic #
###################################################################################

* This example uses vtkCameraOrientationWidget instead of vtkInteractorStyleTrackballCamera
  to manipualte camera. vtkCameraOrientationWidget needs "renderer object" in addition to
  object to those vtkInteractorStyleTrackballCamera needs.

###  Pipeline for interactor events -> Interactor Observer Logic ###

                        OPERATING SYSTEM
                              │
                              │ mouse / keyboard / etc.
                              ▼

                            2D SCREEN
                                │
                            mouse (x,y)
                                │
                                ▼
                 ┌───────────────────────────┐
                 │ vtkRenderWindowInteractor │
                 │                           │
                 │ receives input            │
                 │ translates input          │
                 └────────────┬──────────────┘
                              │
                              ▼
                         VTK EVENT
                              │
                              │
                              ▼
                            PICKER
                                │
                        ┌───────┼────────┐
                        ▼       ▼        ▼
                        Prop    Point     Cell
                        │       │        │
                        ▼       ▼        ▼
                        Actor   Node    Element


"""

import numpy as np

# ============================================================
# VTK native OpenGL backend
# ============================================================

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util import colors
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy

from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray,
)

from vtkmodules.vtkCommonCore import vtkIdList # !!!!

from vtkmodules.vtkCommonDataModel import (
    VTK_HEXAHEDRON,
)

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkCellPicker,
    vtkTextActor,
)

from vtkmodules.vtkInteractionStyle import (vtkCameraManipulator,
                                            vtkInteractorStyleManipulator,
                                            vtkTrackballRotate,
                                            vtkTrackballPan)

# -- Import Common Data --
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.grid_three_hex import grid
# -----------------

class CustomInteractorStyle(vtkInteractorStyleManipulator):

    def __init__(self, renderer) -> None:
        super().__init__()

        self.rotate_manipulator = vtkTrackballRotate(mouse_button=vtkCameraManipulator.MouseButtonType.Middle)
        self.pan_manipulator = vtkTrackballPan(mouse_button=vtkCameraManipulator.MouseButtonType.Right)
        self.AddManipulator(self.rotate_manipulator)
        self.AddManipulator(self.pan_manipulator)

        camera = renderer.GetActiveCamera()
        self.center_of_rotation = (camera.focal_point)
        self.mouse_wheel_zooms_to_cursor = True
        self.mouse_motion_factor = 1.0

# -------------------------
# VTK rendering pipeline
# -------------------------
grid = grid()

mapper = vtkDataSetMapper(input_data=grid)

actor = vtkActor(mapper=mapper)
#actor.property.representation = VTK_WIREFRAME
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1
actor.property.color = colors.warm_grey

renderer = vtkRenderer()
renderer.AddActor(actor)
renderer.background = colors.white

renderer.ResetCamera()

camera = renderer.GetActiveCamera()
camera.parallel_projection = True

render_window = vtkRenderWindow(size=(1000, 700))
render_window.AddRenderer(renderer)

interactor = vtkRenderWindowInteractor()
interactor.render_window = render_window

interactor.interactor_style = CustomInteractorStyle(renderer)

# ============================================================
# CellData
# ============================================================

von_mises_stress = np.array(
    [
        100.0,   # Hex 0
        250.0,   # Hex 1
        400.0,   # Hex 2
    ],
    dtype=np.float64,
)

grid.cell_data["von_mises_stress"] = von_mises_stress


# ============================================================
# Cell picker
# ============================================================

picker = vtkCellPicker()
picker.tolerance = 0.001

# ============================================================
# Highlight actor
# ============================================================

highlight_actor = None

# ============================================================
# Text actor
# ============================================================

text_actor = vtkTextActor()
text_actor.position = (20, 20)
text_actor.text_scale_mode = vtkTextActor.TEXT_SCALE_MODE_VIEWPORT
text_actor.text_property.font_size = 24
text_actor.text_property.color = (0.0, 0.0, 0.0)
text_actor.input = "Click an element"
renderer.AddActor(text_actor)

# ============================================================
# Create highlight mesh for one cell
# ============================================================

def create_highlight_actor(cell_id):

    point_ids = vtkIdList()
    grid.GetCellPoints(cell_id, point_ids)

    selected_coordinates = np.array(
        [
            grid.points.data[point_ids.GetId(i)]
            for i in range(point_ids.GetNumberOfIds())
        ],
        dtype=np.float64)

    selected_points = Points(data=selected_coordinates)

    selected_connectivity = np.arange(8, dtype=np.int64)

    selected_cell_types = numpy_to_vtk(np.array([VTK_HEXAHEDRON], dtype=np.uint8), deep=True)

    selected_offsets = np.array([0, 8], dtype=np.int64)

    selected_cells = CellArray(offsets=selected_offsets, connectivity=selected_connectivity)

    selected_grid = UnstructuredGrid(points=selected_points, cells=(selected_cell_types, selected_cells))

    selected_mapper = vtkDataSetMapper(input_data=selected_grid)

    selected_actor = vtkActor(mapper=selected_mapper)

    selected_actor.property.color = (1.0, 1.0, 0.0)
    selected_actor.property.opacity = 0.35
    selected_actor.property.edge_visibility = True
    selected_actor.property.edge_color = (1.0, 0.0, 0.0)
    selected_actor.property.line_width = 4.0

    return selected_actor

# ============================================================
# Left mouse button callback
# ============================================================

def on_left_button_press(caller, event):

    global highlight_actor

    # --------------------------------------------------------
    # Get mouse position in display coordinates
    # --------------------------------------------------------

    x, y = caller.GetEventPosition()

    # --------------------------------------------------------
    # Pick
    # --------------------------------------------------------

    picked = picker.Pick(x, y, 0.0, renderer)

    # --------------------------------------------------------
    # Nothing was picked
    # --------------------------------------------------------

    if not picked:
        return

    # --------------------------------------------------------
    # Get picked cell ID
    # --------------------------------------------------------

    cell_id = picker.cell_id

    if cell_id < 0:
        return

    # --------------------------------------------------------
    # Print Cell ID
    # --------------------------------------------------------

    print(f"Cell ID: {cell_id}")

    # --------------------------------------------------------
    # Retrieve CellData
    # --------------------------------------------------------

    stress = grid.cell_data["von_mises_stress"][cell_id]

    print(f"Von Mises Stress: {stress:.1f} MPa")

    # --------------------------------------------------------
    # Remove previous highlight
    # --------------------------------------------------------

    if highlight_actor is not None:

        renderer.RemoveActor(highlight_actor)

    # --------------------------------------------------------
    # Create new highlight
    # --------------------------------------------------------

    highlight_actor = create_highlight_actor(cell_id)

    renderer.AddActor(highlight_actor)

    # --------------------------------------------------------
    # Update information text
    # --------------------------------------------------------

    text_actor.input = (f"Element ID: {cell_id}\n"
                        f"Von Mises Stress: {stress:.1f} MPa")

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    render_window.Render()

# ============================================================
# Register observer
# ============================================================

interactor.AddObserver("LeftButtonPressEvent",
                        on_left_button_press)

# ============================================================
# Start
# ============================================================

render_window.Render()

interactor.Start()