
"""
https://vtk.org/doc/nightly/html/classvtkInteractorStyleUser.html

https://vtk.org/doc/nightly/html/classvtkCamera.html

https://vtk.org/doc/nightly/html/classvtkActor.html

https://vtk.org/doc/nightly/html/classvtkProp3D.html

https://vtk.org/doc/nightly/html/classvtkProp.html


implementation of the class vtkInteractorStyleUser

"""

from typing import Literal

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
    vtkPropPicker,
    vtkCamera,
    vtkCameraActor
)

from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleUser,
)

from vtkmodules.vtkCommonColor import vtkNamedColors

from Data.grid_three_hex import grid



class CustomInteractorStyle(vtkInteractorStyleUser):

    def __init__(self, renderer) -> None:
        super().__init__()

        self.renderer = renderer
        self.picker = vtkPropPicker()
        self.camera : vtkCamera = self.renderer.GetActiveCamera()

        self.AddObserver(vtkCommand.LeftButtonPressEvent, self.on_left_button_down)
        self.AddObserver(vtkCommand.MiddleButtonPressEvent, self.on_middle_button_down)
        self.AddObserver(vtkCommand.RightButtonPressEvent, self.on_right_button_down)

        self.AddObserver(vtkCommand.LeftButtonReleaseEvent, self.on_left_button_up)
        self.AddObserver(vtkCommand.MiddleButtonReleaseEvent, self.on_middle_button_up)
        self.AddObserver(vtkCommand.RightButtonReleaseEvent, self.on_right_button_up)

        self.AddObserver(vtkCommand.MouseMoveEvent, self.on_mouse_move)
    
        self.AddObserver(vtkCommand.MouseWheelForwardEvent, self.zoom_in)
        self.AddObserver(vtkCommand.MouseWheelBackwardEvent, self.zoom_out)

        self.AddObserver(vtkCommand.CharEvent, self.on_key_press)

        self._state : None | Literal["PAN", "ROTATE", "ZOOM", "SELECT"] = None

        self.old_x, self.old_y = None, None

        self.zoom_factor = 1.1
        self.mouse_motion_factor = 0.5
        

    def on_left_button_down(self, caller, event) -> None:
        self._state = "SELECT"

    def on_middle_button_down(self, caller, event) -> None:
        self._state = "ROTATE"

    def on_right_button_down(self, caller, event) -> None:
        self._state = "PAN"

    def on_left_button_up(self, caller, event) -> None:
        self._state = None

    def on_middle_button_up(self, caller, event) -> None:
        self._state = None

    def on_right_button_up(self, caller, event) -> None:
        self._state = None


    def on_mouse_move(self, caller, event):

        old_x, old_y = caller.old_pos
        x, y = caller.last_pos
        dx = old_x - x
        dy = old_y - y

        if self._state == "ROTATE":

            # Example rotation
            self.camera.Azimuth(dx * self.mouse_motion_factor)
            self.camera.Elevation(dy * self.mouse_motion_factor)
    
        elif self._state == "PAN":

            # Manipulate the camera position and focal point simultaneously.

            width, height = render_window.GetSize()
            
            # Camera coordinate system
            direction = np.array(self.camera.direction_of_projection)

            up = np.array(self.camera.view_up)

            right = np.cross(direction, up)
            right /= np.linalg.norm(right)

            up /= np.linalg.norm(up)

            # Pixel -> world units
            world_per_pixel = (self.camera.parallel_scale / height)

            dx_world = dx * world_per_pixel
            dy_world = dy * world_per_pixel

            # Screen-space translation
            translation = (right * dx_world + up * dy_world)

            # Move camera and focal point together
            position = np.array(self.camera.position)
            focal = np.array(self.camera.focal_point)

            self.camera.SetPosition(position + translation)
            self.camera.SetFocalPoint(focal + translation)

            renderer.ResetCameraClippingRange()

        self.interactor.Render()


    def zoom_in(self, caller, event):
    
        print(type(caller.last_pos), caller.old_pos)
        #self.camera.SetFocalPoint(caller.last_pos)
        self.camera.Zoom(self.zoom_factor)
        self.interactor.Render()
    
    def zoom_out(self, caller, event):
        
        self.camera.Zoom(1.0 / self.zoom_factor)
        self.interactor.Render()


    def select(self):

        print(self.last_pos)
        interactor = self.GetInteractor()
        x, y = interactor.GetEventPosition()

        self.picker.Pick(x, y, 0, self.renderer)
        actor = self.picker.GetActor()

        if actor is not None:
            print("Actor selected")
            actor.GetProperty().SetColor(1.0, 0.0, 0.0)
            interactor.Render()
    
    def on_key_press(self, caller, event) -> None:
        key = (self.GetInteractor().GetKeySym() or "").lower()

        if key == "e":
            print("element")
        elif key == "n":
            print("node")
        elif key == "s":
            print("surface")



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

style = CustomInteractorStyle(renderer)
interactor.interactor_style = style

# ---------------------------------------------
# Camera

# vtk Camera Actor -------------------------

camera = vtkCamera()
camera_actor = vtkCameraActor()
camera_actor.SetCamera(camera)
camera_actor.property.color = vtkNamedColors().GetColor3d('Black')

 # Set the camera parameters for the camera actor.
camera.DeepCopy(renderer.active_camera)
renderer.AddActor(camera_actor)

#camera = renderer.GetActiveCamera()
#camera.Azimuth(-30)
#camera.Elevation(30)
#camera.Dolly(1.25)
#camera.Zoom(-5)


# ---------------------------------------------

render_window.Render()
interactor.Start()