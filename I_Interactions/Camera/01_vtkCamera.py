
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
    vtkCamera,
    vtkCameraActor
)

from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleTrackballCamera,
)

from vtkmodules.vtkCommonColor import vtkNamedColors

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
actor.property.color = colors.warm_grey
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

# Camera Points

add_3d_point(renderer, np.array((0, 0, 0)))
add_3d_point(renderer, np.array(renderer_camera.position)) 
add_3d_point(renderer, np.array(renderer_camera.view_up))
add_3d_point(renderer, np.array(renderer_camera.focal_point))
add_3d_point(renderer, np.array(renderer_camera.orientation))

# vtk Camera Actor -------------------------

camera = vtkCamera()
camera_actor = vtkCameraActor()
camera_actor.SetCamera(camera)
camera_actor.property.color = vtkNamedColors().GetColor3d('Black')

 # Set the camera parameters for the camera actor.
camera.DeepCopy(renderer.active_camera)
renderer.AddActor(camera_actor)

# Camera Attributes -------------------------

print("position", camera.position)
print("view up", camera.view_up)
print("focal point:", camera.focal_point)
print("orientation", camera.orientation)

print("direction of projection:", camera.direction_of_projection)
print("focal distance", camera.focal_distance)
print("view angle", camera.view_angle)
print("distance", camera.distance)
print("clipping range:", camera.clipping_range) # (min. range value, max. range value) -> front/back clipping plane



#print("orientation wxyz", camera.orientation_wxyz)
#print("window center", camera.window_center)
#print("roll", camera.roll)
#print("eye angle", camera.eye_angle)
#camera.ComputeViewPlaneNormal()

# Camera Manipulation -------------------------

#camera.Roll(1)
#camera.Elevation(30)
#camera.Azimuth(-30)
#camera.Dolly(1.25)

#camera.Pitch(1)
#camera.Yaw(1)
#camera.Zoom(-50)

# ---------------------------------------------


interactor.Start()






