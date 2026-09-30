"""
Pipeline:

RubberBand3D
      │
      │ start/end screen coordinates
      ▼
vtkAreaPicker
      │
      │ 3D selection frustum
      ▼
vtkExtractSelectedFrustum
      │
      ▼
selected cells
      │
      ▼
highlight / CellData

"""


import numpy as np

# ============================================================
# VTK native OpenGL backend
# ============================================================

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util import colors

from vtkmodules.util.numpy_support import (
    numpy_to_vtk,
    vtk_to_numpy,
)

from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray,
)



from vtkmodules.vtkCommonDataModel import (
    VTK_HEXAHEDRON,
)

from vtkmodules.vtkFiltersExtraction import (
    vtkExtractGeometry,
)

from vtkmodules.vtkFiltersGeneral import(
    vtkExtractSelectedFrustum
)


from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleRubberBand3D,
)

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkRenderedAreaPicker,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkTextActor,
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

    # Hex 3
    [0.0, 1.0, 0.0],
    [1.0, 1.0, 0.0],
    [1.0, 2.0, 0.0],
    [0.0, 2.0, 0.0],
    [0.0, 1.0, 1.0],
    [1.0, 1.0, 1.0],
    [1.0, 2.0, 1.0],
    [0.0, 2.0, 1.0],

    # Hex 4
    [1.0, 1.0, 0.0],
    [2.0, 1.0, 0.0],
    [2.0, 2.0, 0.0],
    [1.0, 2.0, 0.0],
    [1.0, 1.0, 1.0],
    [2.0, 1.0, 1.0],
    [2.0, 2.0, 1.0],
    [1.0, 2.0, 1.0],

    # Hex 5
    [2.0, 1.0, 0.0],
    [3.0, 1.0, 0.0],
    [3.0, 2.0, 0.0],
    [2.0, 2.0, 0.0],
    [2.0, 1.0, 1.0],
    [3.0, 1.0, 1.0],
    [3.0, 2.0, 1.0],
    [2.0, 2.0, 1.0],
], dtype=np.float64)

points = Points(data=coordinates)


# ============================================================
# Cell connectivity
# ============================================================

connectivity = np.arange(48, dtype=np.int64)

cell_types = np.full(
    6,
    VTK_HEXAHEDRON,
    dtype=np.uint8,
)

vtk_cell_types = numpy_to_vtk(
    cell_types,
    deep=True,
)

offsets = np.arange(
    0,
    49,
    8,
    dtype=np.int64,
)

cells = CellArray(
    offsets=offsets,
    connectivity=connectivity,
)


# ============================================================
# UnstructuredGrid
# ============================================================

grid = UnstructuredGrid(
    points=points,
    cells=(vtk_cell_types, cells),
)


# ============================================================
# CellData
# ============================================================

# Keep an explicit engineering element ID.
# This becomes important after extraction because
# the selected dataset has its own local cell numbering.

element_ids = np.arange(
    grid.number_of_cells,
    dtype=np.int64,
)

grid.cell_data["ElementId"] = element_ids

# Example FEA result
von_mises = np.array(
    [100, 150, 200, 250, 300, 350],
    dtype=np.float64,
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
# Main mesh mapper
# ============================================================

mapper = vtkDataSetMapper(input_data=grid)

# ============================================================
# Main mesh actor
# ============================================================

actor = vtkActor(mapper=mapper)
actor.property.color = colors.warm_grey
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1.5

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
# Interactor and InteractorStyle
# ============================================================

interactor = vtkRenderWindowInteractor()
interactor.render_window = render_window

style = vtkInteractorStyleRubberBand3D()
style.default_renderer = renderer
interactor.interactor_style = style

# ============================================================
# Area Picker
# ============================================================

area_picker = vtkRenderedAreaPicker()

# ============================================================
# Selected actor
# ============================================================

selected_mapper = vtkDataSetMapper()

selected_actor = vtkActor(mapper=selected_mapper)
selected_actor.property.color = colors.yellow
selected_actor.property.edge_visibility = True
selected_actor.property.edge_color = colors.red
selected_actor.property.line_width = 3.0

renderer.AddActor(selected_actor)

# ============================================================
# Area selection callback
# ============================================================

def select_area(caller, event):

    # --------------------------------------------------------
    # Get RubberBand3D rectangle
    # --------------------------------------------------------

    x0, y0 = style.start_position
    x1, y1 = style.end_position

    xmin = min(x0, x1)
    xmax = max(x0, x1)

    ymin = min(y0, y1)
    ymax = max(y0, y1)

    # Ignore simple clicks
    if xmax - xmin < 3 or ymax - ymin < 3:
        return


    # --------------------------------------------------------
    # vtkAreaPicker
    # --------------------------------------------------------

    picked = area_picker.AreaPick(
        xmin,
        ymin,
        xmax,
        ymax,
        renderer,
    )

    if not picked:
        return


    # --------------------------------------------------------
    # Get the selection frustum
    # --------------------------------------------------------

    frustum = area_picker.frustum

    # --------------------------------------------------------
    # Extract cells inside the frustum
    # --------------------------------------------------------

    extract = vtkExtractSelectedFrustum(input_data=grid, frustum=frustum)
    extract.field_type = 0
    extract.Update()

    # --------------------------------------------------------
    # Get selected dataset
    # --------------------------------------------------------
    
    selected = extract.output
    print(f"Selected cells: {selected.number_of_cells}")

    # --------------------------------------------------------
    # Get original cell IDs
    # --------------------------------------------------------

    original_ids = (selected.cell_data["vtkOriginalCellIds"])

    if original_ids is not None:

        selected_ids = vtk_to_numpy(original_ids)
        print(f"Selected cell IDs: {selected_ids}")

        # ----------------------------------------------------
        # Access original CellData
        # ----------------------------------------------------

        for cell_id in selected_ids:

            stress_value = (grid.cell_data["Stress"][cell_id])
            print(f"Element {cell_id}: Stress = {stress_value}")

    # --------------------------------------------------------
    # Highlight selected cells
    # --------------------------------------------------------
    
    selected_mapper.input_data = selected

    render_window.Render()

# ============================================================
# SelectionChangedEvent
# ============================================================

style.AddObserver(
    "SelectionChangedEvent",
    select_area,
)

# ============================================================
# Start
# ============================================================

render_window.Render()
interactor.Start()