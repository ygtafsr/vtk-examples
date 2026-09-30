

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

from _ugrid_data import actor
from CameraPointsHelper import add_3d_point

from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Slot

from mainwindow_ui import Ui_MainWindow

class CustomInteractorStyle(vtkInteractorStyleUser):

    def __init__(self, renderer) -> None:
        super().__init__()

        self.renderer = renderer
        self.picker = vtkPropPicker()
        self.camera : vtkCamera = self.renderer.GetActiveCamera()

        """
        self.AddObserver(vtkCommand.LeftButtonPressEvent, self.on_left_button_down)
        self.AddObserver(vtkCommand.MiddleButtonPressEvent, self.on_middle_button_down)
        self.AddObserver(vtkCommand.RightButtonPressEvent, self.on_right_button_down)

        self.AddObserver(vtkCommand.LeftButtonReleaseEvent, self.on_left_button_up)
        self.AddObserver(vtkCommand.MiddleButtonReleaseEvent, self.on_middle_button_up)
        self.AddObserver(vtkCommand.RightButtonReleaseEvent, self.on_right_button_up)

        self.AddObserver(vtkCommand.MouseMoveEvent, self.on_mouse_move)
    
        self.AddObserver(vtkCommand.MouseWheelForwardEvent, self.zoom_in)
        self.AddObserver(vtkCommand.MouseWheelBackwardEvent, self.zoom_out)
        """

        self.AddObserver(vtkCommand.CharEvent, self.on_key_press)

        self._state : None | Literal["PAN", "ROTATE", "ZOOM", "SELECT"] = None

        self.old_x, self.old_y = None, None

        self.zoom_factor = 1.1
        self.mouse_motion_factor = 0.5

    def on_mouse_move(self, caller, event):
        pass

    def on_key_press(self, caller, event) -> None:
            key = (self.GetInteractor().GetKeySym() or "").lower()
    
            if key == "e":
                print("element")
            elif key == "n":
                print("node")
            elif key == "s":
                print("surface")

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.renderer = self.setup_vtk()
        self.camera = self.renderer.GetActiveCamera()

        self.ui.horizontalSlider.setMaximum(100)
        self.ui.horizontalSlider.valueChanged.connect(self.hello)
        self.azimuth_old_value = 0

    def hello(self, value):
        if value > self.azimuth_old_value:
            self.camera.Azimuth(value)
        else:
            self.camera.Azimuth(-value)
        self.renderer.render_window.interactor.Render()
        self.azimuth_old_value = value

        self.print_camera_params()

    def load_actor(self):
        return actor

    def print_camera_params(self):

        camera = self.renderer.GetActiveCamera()

        # Camera Attributes -------------------------

        self.ui.label_5.setText(f"position: {camera.position}\n"
                                f"view up: {camera.view_up}\n"
                                f"focal point: {camera.focal_point}\n"
                                f"orientation: {camera.orientation}\n"
                                f"direction of projection: {camera.direction_of_projection}\n"
                                f"focal distance: {camera.focal_distance}\n"
                                f"view angle: {camera.distance}\n"
                                f"clipping range: {camera.clipping_range}"
                                )

    def setup_vtk(self):

        # Get the QVTKRenderWindowInteractor created by Designer
        self.vtk_widget = self.ui.vtk_widget

        # Get VTK render window
        render_window = self.vtk_widget.GetRenderWindow()

        # Create renderer
        renderer = vtkRenderer()
        renderer.background = colors.white

        render_window.AddRenderer(renderer)      

        # Load actor by a button click
        vtk_actor = self.load_actor()

        renderer.AddActor(vtk_actor)
        renderer.ResetCamera()

        # Get VTK interactor
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor() 
        self.interactor.interactor_style = CustomInteractorStyle(renderer)

        # vtk Camera Actor -------------------------

        camera = vtkCamera()
        camera_actor = vtkCameraActor()
        camera_actor.SetCamera(camera)
        camera_actor.property.color = vtkNamedColors().GetColor3d('Black')

        # Set the camera parameters for the camera actor.
        camera.DeepCopy(renderer.active_camera)
        renderer.AddActor(camera_actor)

        # ----------------------------------------------

        # Don't call render_windw.Start() explicitly! This creates trailed view!
        #render_window.Start()

        # Start interaction
        self.vtk_widget.Initialize()

        return renderer

app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())









