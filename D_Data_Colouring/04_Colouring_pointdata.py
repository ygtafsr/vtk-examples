
"""
The mapper is where the scalar values become colours.
VTK's mapper provides controls such as ScalarVisibility, ScalarRange, LookupTable, ColorMode, etc.

                    PointData
                        │
                        ▼
    UnstructuredGrid ──► vtkDataSetMapper
                            │
                            │ scalar → colour
                            ▼
                        Actor

VTK's mapper provides controls such as ScalarVisibility, ScalarRange, LookupTable, ColorMode, etc.
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
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor
)

# -- Import Common Data --
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ZZ_Data.grid_three_quad import grid
# -----------------

# Rendering Pipeline
renderer = vtkRenderer()
renderer.background = (0.15, 0.15, 0.15)
renderer.ResetCamera()

render_window = vtkRenderWindow(size=(1000, 700))
render_window.AddRenderer(renderer)

interactor = vtkRenderWindowInteractor()
interactor.render_window = render_window


# ============================================================
# Point Data Colouring
# ============================================================

# Create Scalar Data
stress = np.array(
    [100, 150, 200, 250,
     300, 350, 400, 450],
    dtype=np.float64,
)

grid.point_data["von_mises_stress"] = stress
grid.point_data.SetActiveScalars("von_mises_stress") ### !!! Set Active Scalars !!!

mapper = vtkDataSetMapper(input_data=grid)
mapper.scalar_visibility = True
mapper.scalar_range = (stress.min(), stress.max())

# Create a lookup table :: Scalar to Colour mapping 
lut = vtkLookupTable(number_of_table_values=5,
                        range=(100, 450))

"""
lut.SetTableValue(0, 0.0, 0.0, 1.0, 1.0)
lut.SetTableValue(1, 0.0, 1.0, 1.0, 1.0)
lut.SetTableValue(2, 0.0, 1.0, 0.0, 1.0)
lut.SetTableValue(3, 1.0, 1.0, 0.0, 1.0)
lut.SetTableValue(4, 1.0, 0.0, 0.0, 1.0)
"""
mapper.lookup_table = lut


actor = vtkActor(mapper=mapper)
#actor.property.representation = VTK_WIREFRAME
actor.property.edge_visibility = True
actor.property.edge_color = (0.1, 0.1, 0.1)
actor.property.line_width = 1

renderer.AddActor(actor)
# ============================================================

# Start

render_window.Render()
interactor.Start()
