import numpy as np

# ============================================================
# VTK native OpenGL backend
# ============================================================

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util import colors
from vtkmodules.util.numpy_support import numpy_to_vtk

from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray,
)

from vtkmodules.vtkCommonDataModel import (
    VTK_HEXAHEDRON,
)

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkPointPicker,
    vtkTextActor,
)

from vtkmodules.vtkFiltersSources import (
    vtkSphereSource,
)


# ============================================================
# HEX mesh
# ============================================================

coordinates = np.array([
    # Hex 0
    [0.0, 0.0, 0.0],
    [1.0, 0.0, 0.0],
    [1.0, 1.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [1.0, 0.0, 1.0],
    [1.0, 1.0, 1.0],
    [0.0, 1.0, 1.0],

    # Hex 1
    [1.0, 0.0, 0.0],
    [2.0, 0.0, 0.0],
    [2.0, 1.0, 0.0],
    [1.0, 1.0, 0.0],
    [1.0, 0.0, 1.0],
    [2.0, 0.0, 1.0],
    [2.0, 1.0, 1.0],
    [1.0, 1.0, 1.0],

    # Hex 2
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
# Cell connectivity
# ============================================================

connectivity = np.arange(24, dtype=np.int64)

cell_types = np.array(
    [
        [VTK_HEXAHEDRON],
        [VTK_HEXAHEDRON],
        [VTK_HEXAHEDRON],
    ],
    dtype=np.uint8,
)

vtk_cell_types = numpy_to_vtk(cell_types, deep=True)

offsets = np.array(
    [0, 8, 16, 24],
    dtype=np.int64,
)

cells = CellArray(offsets=offsets, connectivity=connectivity)


# ============================================================
# UnstructuredGrid
# ============================================================

grid = UnstructuredGrid(points=points,
                        cells=(vtk_cell_types, cells))

# ============================================================
# PointData
# ============================================================

stress = np.array(
    [
        100.0,
        120.0,
        150.0,
        180.0,
        200.0,
        220.0,
        250.0,
        280.0,

        300.0,
        320.0,
        340.0,
        360.0,
        380.0,
        400.0,
        420.0,
        440.0,

        450.0,
        470.0,
        500.0,
        520.0,
        540.0,
        560.0,
        580.0,
        600.0,
    ],
    dtype=np.float64,
)

grid.point_data["von_mises_stress"] = stress


# ============================================================
# Main mesh mapper
# ============================================================

mapper = vtkDataSetMapper(
    input_data=grid
)


# ============================================================
# Main mesh actor
# ============================================================

actor = vtkActor(
    mapper=mapper
)

actor.property.color = colors.warm_grey
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1.0


# ============================================================
# Renderer
# ============================================================

renderer = vtkRenderer()

renderer.AddActor(actor)

renderer.background = colors.white

renderer.ResetCamera()


# ============================================================
# Render window
# ============================================================

render_window = vtkRenderWindow()

render_window.AddRenderer(renderer)

render_window.size = (1000, 700)


# ============================================================
# Interactor
# ============================================================

interactor = vtkRenderWindowInteractor()

interactor.render_window = render_window


# ============================================================
# Camera interaction
# ============================================================

from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleTrackballCamera
)

style = vtkInteractorStyleTrackballCamera()

interactor.interactor_style = style


# ============================================================
# Point Picker
# ============================================================

picker = vtkPointPicker()

picker.tolerance = 0.01


# ============================================================
# Highlight node
# ============================================================

highlight_actor = None


# ============================================================
# Information text
# ============================================================

text_actor = vtkTextActor()

text_actor.position = (20, 20)

text_actor.text_scale_mode = (
    vtkTextActor.TEXT_SCALE_MODE_VIEWPORT
)

text_actor.text_property.font_size = 24

text_actor.text_property.color = colors.black

text_actor.input = "Click a node"

renderer.AddActor(text_actor)


# ============================================================
# Create node highlight
# ============================================================

def create_node_highlight(point_id):

    # --------------------------------------------------------
    # Get node coordinates
    # --------------------------------------------------------

    position = grid.points.data[point_id]

    # --------------------------------------------------------
    # Sphere around node
    # --------------------------------------------------------

    sphere = vtkSphereSource(
        center=position,
        radius=0.08,
        theta_resolution=24,
        phi_resolution=24,
    )

    # --------------------------------------------------------
    # Mapper
    # --------------------------------------------------------

    mapper = vtkDataSetMapper(
        input_connection=sphere.output_port
    )

    # --------------------------------------------------------
    # Actor
    # --------------------------------------------------------

    highlight = vtkActor(
        mapper=mapper
    )

    highlight.property.color = colors.red

    return highlight


# ============================================================
# Left mouse button callback
# ============================================================

def on_left_button_press(caller, event):

    global highlight_actor

    # --------------------------------------------------------
    # Mouse position
    # --------------------------------------------------------

    x, y = caller.GetEventPosition()

    # --------------------------------------------------------
    # Point picking
    # --------------------------------------------------------

    picked = picker.Pick(
        x,
        y,
        0.0,
        renderer,
    )

    # --------------------------------------------------------
    # Nothing picked
    # --------------------------------------------------------

    if not picked:
        return

    # --------------------------------------------------------
    # Get Point ID
    # --------------------------------------------------------

    point_id = picker.point_id

    if point_id < 0:
        return

    # --------------------------------------------------------
    # Get coordinates
    # --------------------------------------------------------

    position = grid.points.data[point_id]

    # --------------------------------------------------------
    # Get PointData
    # --------------------------------------------------------

    stress_value = (
        grid.point_data["von_mises_stress"][point_id]
    )

    # --------------------------------------------------------
    # Print information
    # --------------------------------------------------------

    print(f"Node ID: {point_id}")

    print(
        f"Coordinates: "
        f"({position[0]:.3f}, "
        f"{position[1]:.3f}, "
        f"{position[2]:.3f})"
    )

    print(
        f"Von Mises Stress: "
        f"{stress_value:.1f} MPa"
    )

    # --------------------------------------------------------
    # Remove previous highlight
    # --------------------------------------------------------

    if highlight_actor is not None:

        renderer.RemoveActor(
            highlight_actor
        )

    # --------------------------------------------------------
    # Create new highlight
    # --------------------------------------------------------

    highlight_actor = create_node_highlight(
        point_id
    )

    renderer.AddActor(
        highlight_actor
    )

    # --------------------------------------------------------
    # Update information text
    # --------------------------------------------------------

    text_actor.input = (
        f"Node ID: {point_id}\n"
        f"Coordinates: "
        f"({position[0]:.2f}, "
        f"{position[1]:.2f}, "
        f"{position[2]:.2f})\n"
        f"Von Mises Stress: "
        f"{stress_value:.1f} MPa"
    )

    # --------------------------------------------------------
    # Render
    # --------------------------------------------------------

    render_window.Render()


# ============================================================
# Register observer
# ============================================================

interactor.AddObserver(
    "LeftButtonPressEvent",
    on_left_button_press,
)


# ============================================================
# Start
# ============================================================

render_window.Render()

interactor.Start()