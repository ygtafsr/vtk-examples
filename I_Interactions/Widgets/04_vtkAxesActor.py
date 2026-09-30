"""
https://vtk.org/doc/nightly/html/classvtkAxesActor.html
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

from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor

# -- Import Common Data --
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from ZZ_Data.grid_three_hex import grid
# -----------------

mapper = vtkDataSetMapper(input_data=grid())
renderer = vtkRenderer()
renderer.background = colors.white

camera = renderer.GetActiveCamera()
camera.parallel_projection = True

render_window = vtkRenderWindow(size=(1000, 700))
render_window.AddRenderer(renderer)

interactor = vtkRenderWindowInteractor()
style = vtkInteractorStyleTrackballCamera()

interactor.render_window = render_window
interactor.interactor_style = style

# ugrid actor ---

actor = vtkActor(mapper=mapper)
actor.property.edge_visibility = True
actor.property.edge_color = colors.black
actor.property.line_width = 1
actor.property.color = colors.warm_grey

# Axes Actor ---

axes = vtkAxesActor(shaft_type=vtkAxesActor.CYLINDER_SHAFT, 
                    tip_type=vtkAxesActor.CONE_TIP,
                    x_axis_label_text='X', 
                    y_axis_label_text='Y', 
                    z_axis_label_text='Z',
                    total_length=(1.0, 1.0, 1.0))

axes.cylinder_radius = 1.25 * axes.cylinder_radius
axes.cone_radius = 1.25 * axes.cone_radius
axes.sphere_radius = 1.5 * axes.sphere_radius

axes.x_axis_caption_actor2d.caption_text_property.color = colors.firebrick
axes.y_axis_caption_actor2d.caption_text_property.color = colors.green_dark
axes.z_axis_caption_actor2d.caption_text_property.color = colors.blue

# Orientation Marker Widget ---

widget = vtkOrientationMarkerWidget(orientation_marker=axes,
                                    interactor=interactor, 
                                    default_renderer=renderer,
                                    outline_color=colors.blue, 
                                    viewport=(0.0, 0.0, 0.2, 0.2),
                                    zoom=1.5,
                                    enabled=True,
                                    interactive=True)

# --------------

renderer.AddActor(actor)
renderer.AddActor(axes)
renderer.ResetCamera()

render_window.Render()
interactor.Start()


    
