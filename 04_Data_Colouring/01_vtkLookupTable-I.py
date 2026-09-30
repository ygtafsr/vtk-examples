
"""
Choose color schemes from ColorSeriesPatches. 
Make sure that the number of bands used in your surface matches the number of colors
in the color series patches that you select.

https://examples.vtk.org/site/ColorNamesSeries/ColorSeriesPatches.html
"""

import numpy as np

# VTK native OpenGL backend
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2


from vtkmodules.vtkCommonColor import vtkColorSeries

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor
)

# -- Get Grid Data --
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from Data.grid_three_quad import grid
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
colors = vtkColorSeries()
lut = colors.CreateLookupTable()
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
