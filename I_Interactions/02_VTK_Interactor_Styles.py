"""
#########################################################################
# Example of vtk Event -> interactor style -> camera manipulation logic #
#########################################################################

* This example do not use pure event-observer logic. Instead, it uses 
  VTK predefined vtkInteractorStyleTrackballCamera interactor object
  which has own Event -> Render Camera interaction logic.

###  Pipeline for interactor events -> Interactor Observer Logic ###

                     OPERATING SYSTEM
                          │
                mouse / keyboard / etc.
                          │
                          ▼
             ┌──────────────────────────┐
             │ vtkRenderWindowInteractor│
             │                          │
             │ receives input           │
             │ translates input         │
             └────────────┬─────────────┘
                          │
                          ▼
                      VTK EVENT
                          │
                          │
                          ▼
                   INTERACTOR STYLE (vtkInteractorObserver > vtkInteractorStyleTrackballCamera)
                          │
                          │ interprets
                          ▼
                  CAMERA MANIPULATION
                          │
                          │ 
                          ▼
                       RENDERER

###  Common vtk interactor observers ###

vtkInteractorStyleTrackballCamera :: Allows "predefined" camera manipulations
vtkInteractorStyleManipulator :: Allows "custom" camera manipulations
vtkInteractorStyleTrackballActor :: Allows interaction with actors

"""

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

from vtkmodules.vtkInteractionStyle import (
    vtkInteractorStyleTrackballCamera,
)

from ZZ_Data.grid_three_hex import grid


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
style = vtkInteractorStyleTrackballCamera()

interactor.render_window = render_window
interactor.interactor_style = style


#### Predefined Interactor Styles' Manipulation #### 
"""
* The C++ behavior does not translate directly to Python VTK wrappers.

* VTK's current PythonicAPI examples therefore use AddObserver() on the interactor style 
  rather than overriding OnLeftButtonDown()

* Some interactor style classes provides explicit Pan(), Rotate() like camera manipulation
  functions so that we can customize their behaviour. But others do not allow this like
  vtkInteractorStyleRubberBand3D.

* We can define AddObserver() for both interactor and style. Since style is a high level
  implementation on interactor, if we AddObserver() for interactor, style overrides it by
  it pre-defined observers.
"""
def on_left_button_down(caller, event):
    print("LEFT DOWN")  # This interrupts vtkInteractorStyleTrackballCamera's
                        # OnLeftButtonDown() Callback Function.

style.AddObserver("LeftButtonPressEvent",
                   on_left_button_down)
#####


# -------------------------------------------

render_window.Render()
interactor.Start()


    