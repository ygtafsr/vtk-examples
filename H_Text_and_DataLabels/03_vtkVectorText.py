import numpy as np

# ------------------------------------------------------------
# VTK data model
# ------------------------------------------------------------

from vtkmodules.util.numpy_support import numpy_to_vtk

from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray,
)

from vtkmodules.vtkCommonDataModel import (
    VTK_QUAD,
)

# ------------------------------------------------------------
# VTK rendering
# ------------------------------------------------------------

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkFollower,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from vtkmodules.vtkRenderingFreeType import (
    vtkVectorText,
)

# ------------------------------------------------------------
# Required on Windows / OpenGL
# ------------------------------------------------------------

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2


# ============================================================
# 1. Create mesh
# ============================================================

coordinates = np.array([
    [0.0, 0.0, 0.0],     # node 0
    [5.0, 0.0, 0.0],     # node 1
    [10.0, 0.0, 0.0],    # node 2
    [15.0, 0.0, 0.0],    # node 3
    [0.0, 5.0, 0.0],     # node 4
    [5.0, 5.0, 0.0],     # node 5
    [10.0, 5.0, 0.0],    # node 6
    [15.0, 5.0, 0.0],    # node 7
], dtype=np.float64)


points = Points(
    data=coordinates,
)


# ============================================================
# 2. Create cells
# ============================================================

connectivity = np.array(
    [
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
    ],
    dtype=np.int64,
)


cell_types = np.array(
    [
        VTK_QUAD,
        VTK_QUAD,
        VTK_QUAD,
    ],
    dtype=np.uint8,
)


vtk_cell_types = numpy_to_vtk(
    cell_types,
    deep=True,
)


offsets = np.array(
    [0, 4, 8, 12],
    dtype=np.int64,
)


cells = CellArray(
    offsets=offsets,
    connectivity=connectivity.ravel(),
)


# ============================================================
# 3. Create vtkUnstructuredGrid
# ============================================================

grid = UnstructuredGrid(
    points=points,
    cells=(vtk_cell_types, cells),
)


# ============================================================
# 4. Mesh pipeline
#
# vtkUnstructuredGrid
#        ↓
# vtkDataSetMapper
#        ↓
# vtkActor
# ============================================================

mesh_mapper = vtkDataSetMapper(
    input_data=grid,
)


mesh_actor = vtkActor(
    mapper=mesh_mapper,
)


mesh_actor.property.edge_visibility = True
mesh_actor.property.edge_color = (0.1, 0.1, 0.1)
mesh_actor.property.line_width = 2.0


# ============================================================
# 5. Renderer
# ============================================================

renderer = vtkRenderer()

renderer.SetBackground(
    0.15,
    0.15,
    0.18,
)

renderer.AddActor(
    mesh_actor,
)


# ============================================================
# 6. Node ID annotations
#
# vtkVectorText
#       ↓
# vtkPolyDataMapper
#       ↓
# vtkFollower
# ============================================================

label_actors = []

for node_id, position in enumerate(coordinates):

    # --------------------------------------------------------
    # Text source
    # --------------------------------------------------------

    text_source = vtkVectorText(
        text=str(node_id),
    )

    # --------------------------------------------------------
    # Text mapper
    # --------------------------------------------------------

    text_mapper = vtkPolyDataMapper(
        input_connection=text_source.output_port,
    )

    # --------------------------------------------------------
    # Follower
    # --------------------------------------------------------

    text_actor = vtkFollower(
        mapper=text_mapper,
    )

    # --------------------------------------------------------
    # Position
    # --------------------------------------------------------

    text_actor.position = (
        position[0] + 0.2,
        position[1] + 0.2,
        position[2],
    )

    # --------------------------------------------------------
    # Size
    # --------------------------------------------------------

    text_actor.scale = (
        0.8,
        0.8,
        0.8,
    )

    # --------------------------------------------------------
    # Rotation centre
    # --------------------------------------------------------

    text_actor.origin = (
        text_source.output.center
    )

    # --------------------------------------------------------
    # Camera
    # --------------------------------------------------------

    text_actor.camera = (
        renderer.active_camera
    )

    # --------------------------------------------------------
    # Add to renderer
    # --------------------------------------------------------

    renderer.AddActor(
        text_actor
    )

    label_actors.append(
        text_actor
    )


# ============================================================
# 7. Camera
# ============================================================

renderer.ResetCamera()


# ============================================================
# 8. Render window
# ============================================================

render_window = vtkRenderWindow()

render_window.AddRenderer(
    renderer
)

render_window.SetWindowName(
    "VTK VectorText - Node Labels"
)

render_window.SetSize(
    1000,
    700,
)


# ============================================================
# 9. Interactor
# ============================================================

render_window_interactor = vtkRenderWindowInteractor()

render_window_interactor.SetRenderWindow(
    render_window
)


# ============================================================
# 10. Render
# ============================================================

render_window.Render()


# ============================================================
# 11. Start Windows event loop
# ============================================================

render_window_interactor.Start()