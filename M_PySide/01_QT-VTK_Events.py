import sys

from PySide6.QtWidgets import QApplication, QMainWindow


from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
)

import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2


from vtkmodules.util import colors

from ui_mainwindow import Ui_MainWindow

from _ugrid_data import actor

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

from vtkmodules.vtkCommonColor import vtkNamedColors

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

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setup_vtk()

        self.ui.horizontalSlider.valueChanged.connect(self.hello)

    def hello(self):
        print("Hello")

    def load_actor(self):
        return actor

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

        # ----------------------------------------------

        # Don't call render_windw.Start() explicitly! This creates trailed view!
        #render_window.Start()

        # Start interaction
        self.vtk_widget.Initialize()


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())