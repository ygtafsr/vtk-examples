
# VTK native OpenGL backend
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from Data.grid_three_hex import grid

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from vtkmodules.util import colors

from vtkmodules.vtkRenderingUI import vtkWin32RenderWindowInteractor


# ------------------------------------------
# ---------- Rendering Pipeline ------------
# ------------------------------------------

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
# "LeftButtonPressEvent" like events rise in vtkRenderWindowInteractor
# and interactor reference is assigned to "caller" parameter of the callback.

interactor = vtkRenderWindowInteractor(render_window= render_window)

# Callback function
def On_Left_Button_Press(caller, event):
    print(caller.event_position) # caller base :: vtkRenderWindowInteractor

interactor.AddObserver("LeftButtonPressEvent", On_Left_Button_Press)

# -------------------------------------------

render_window.Render()
interactor.Start()