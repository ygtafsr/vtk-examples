
"""
https://vtk.org/doc/nightly/html/classvtkInteractorStyleUser.html

https://vtk.org/doc/nightly/html/classvtkCamera.html

https://vtk.org/doc/nightly/html/classvtkActor.html

https://vtk.org/doc/nightly/html/classvtkProp3D.html

https://vtk.org/doc/nightly/html/classvtkProp.html


implementation of the class vtkInteractorStyleUser

"""

import sys
from pathlib import Path
import numpy as np

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util import colors
from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.vtkCommonCore import vtkCommand

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    VTK_WIREFRAME
)

from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleTrackballCamera,
)



from _ugrid_data import grid
from CameraPointsHelper import add_3d_point

# -------------------------
# VTK rendering pipeline
# -------------------------

mapper = vtkDataSetMapper(input_data=grid)

actor = vtkActor(mapper=mapper)
#actor.property.representation = VTK_WIREFRAME
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1
actor.property.color = colors.cobalt
actor.property.opacity = 0.2

renderer = vtkRenderer()
renderer.AddActor(actor)
renderer.background = colors.white

render_window = vtkRenderWindow(size=(1000, 700))
render_window.AddRenderer(renderer)

# ------------------------------------------
# ---------- Interactor Layer --------------
# ------------------------------------------

interactor = vtkRenderWindowInteractor()
interactor.render_window = render_window

style = vtkInteractorStyleTrackballCamera()
interactor.interactor_style = style

renderer.ResetCamera()

# ---------------------------------------------
# Camera
renderer_camera = renderer.GetActiveCamera()

# Parallel Projection

renderer_camera.parallel_projection = True  # Orthographic view
# renderer_camera.parallel_projection = False  # Perspective view

# Controlling Orthographic Zoom ------------
# When using parallel projection, Zoom() behaves differently from perspective:
renderer_camera.parallel_scale = 2
# ParallelScale controls the size of the visible world region vertically.
# Smaller values = zoom in.

# Whereas in perspective mode, you generally use:
# camera.Dolly(2.0)  # move camera closer
# or modify the view angle:
# camera.SetViewAngle(30)

interactor.Start()






