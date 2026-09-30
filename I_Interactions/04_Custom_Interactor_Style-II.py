"""
https://docs.vtk.org/en/latest/release_details/9.7/add-camera-manipulators.html#camera-manipulators-enhanced

https://vtk.org/doc/nightly/html/classvtkCameraManipulator.html

https://vtk.org/doc/nightly/html/classvtkInteractorStyleManipulator.html
"""

import numpy as np

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util import colors
from vtkmodules.util.numpy_support import numpy_to_vtk

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    
)

# -- Import Common Data --
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ZZ_Data.grid_three_hex import grid
# -----------------

from vtkmodules.vtkInteractionStyle import (vtkCameraManipulator,
                                            vtkInteractorStyleManipulator,
                                            vtkJoystickFlyIn,
                                            vtkJoystickFlyOut,
                                            vtkTrackballRotate,
                                            vtkTrackballPan,
                                            vtkTrackballZoom,
                                            vtkTrackballRoll,
                                            vtkTableTopRotate,
                                            vtkTrackballZoomToMouse,
                                            vtkTrackballEnvironmentRotate,
                                            vtkTrackballMultiRotate)

# An example that assigns different mouse and modifier key combinations to particular manipulators.
# Each row corresponds to a modifier key (no modifier, Ctrl, Shift, Alt) and each column corresponds to a mouse button (Left, Middle, Right).

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

mapper = vtkDataSetMapper(input_data=grid())

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

render_window = vtkRenderWindow(size=(1000, 700))
render_window.AddRenderer(renderer)

# ------------------------------------------
# ---------- Interactor Layer --------------
# ------------------------------------------

interactor = vtkRenderWindowInteractor()
interactor.render_window = render_window

interactor.interactor_style = CustomInteractorStyle(renderer)




render_window.Render()
interactor.Start()