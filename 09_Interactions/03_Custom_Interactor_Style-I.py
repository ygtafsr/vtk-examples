
"""
https://vtk.org/doc/nightly/html/classvtkInteractorStyleUser.html

implementation of the class vtkInteractorStyleUser

"""

from typing import Any

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
)

from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleUser,
    vtkInteractorStyleTrackballCamera,
    vtkInteractorStyleRubberBandPick,
)

class CustomInteractorStyle(vtkInteractorStyleTrackballCamera):

    def __init__(self, **properties: Any) -> None:
        super().__init__(**properties)

        self.AddObserver(vtkCommand.MiddleButtonPressEvent, self.on_middle_button_down)
        self.AddObserver(vtkCommand.MiddleButtonReleaseEvent, self.on_middle_button_up)
        self.AddObserver(vtkCommand.RightButtonPressEvent, self.on_right_button_down)
        self.AddObserver(vtkCommand.RightButtonReleaseEvent, self.on_right_button_up)
        self.AddObserver(vtkCommand.LeftButtonPressEvent, self.on_left_button_down)
        self.AddObserver(vtkCommand.LeftButtonReleaseEvent, self.on_left_button_up)
        self.AddObserver(vtkCommand.MouseWheelForwardEvent, self.on_middle_button_forward)
        #self.AddObserver(vtkCommand.MouseWheelBackwardEvent, self.on_middle_button_backward)
        self.AddObserver(vtkCommand.CharEvent, self.on_char)

        
        
    # Supress Left Button
    def on_left_button_down(self, caller, event):
        pass
        #self.StartSelect()

    def on_left_button_up(self, caller, event):
        pass
        #self.StopSelect()

    # Supress Keyboard Events
    def on_char(self, caller, event):
        pass

    # Rotate
    def on_middle_button_down(self, caller, event):
        print(self.center_of_rotation)
        self.StartRotate()

    def on_middle_button_up(self, caller, event):
        self.EndRotate()

    # Pan
    def on_right_button_down(self, caller, event):
        self.StartPan()

    def on_right_button_up(self, caller, event):
        self.EndPan()

    def on_middle_button_forward(self, caller, event):
        
        print("Middle button scrolled forward")

    def on_middle_button_backward(self, caller, event):
        self.StartZoom()
        print("Middle button scrolled backward")


    
from Data.grid_three_hex import grid


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

style = CustomInteractorStyle()
interactor.interactor_style = style

# ---------------------------------------------

render_window.Render()
interactor.Start()