import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util import colors
from vtkmodules.util.data_model import PolyData, Points, CellArray

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
)

from vtkmodules.vtkRenderingCore import VTK_WIREFRAME

# ============================================================
# Rectangle geometry
# ============================================================

points = Points(data=[
    [0.0, 0.0, 0.0],
    [5.0, 0.0, 0.0],
    [5.0, 3.0, 0.0],
    [0.0, 3.0, 0.0],
])

polys = CellArray(
    offsets=[0, 4],
    connectivity=[0, 1, 2, 3],
)

rectangle = PolyData(
    points=points,
    polys=polys,
)


# ============================================================
# Mapper
# ============================================================

# Surface
surface_mapper = vtkPolyDataMapper(
    input_data=rectangle
)

# Boundary
boundary_mapper = vtkPolyDataMapper(
    input_data=rectangle
)



# ============================================================
# Actor
# ============================================================


surface_actor = vtkActor(
    mapper=surface_mapper
)

surface_actor.property.color = (0.2, 0.6, 1.0)
surface_actor.property.opacity = 0.1
surface_actor.property.edge_visibility = False


boundary_actor = vtkActor(
    mapper=boundary_mapper
)

boundary_actor.property.representation = VTK_WIREFRAME
boundary_actor.property.color = (0.2, 0.6, 1.0)
boundary_actor.property.opacity = 1.0
boundary_actor.property.line_width = 2.0


# ============================================================
# Rendering
# ============================================================

renderer = vtkRenderer()
renderer.background = colors.white
renderer.AddActor(surface_actor)
renderer.AddActor(boundary_actor)

render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.size = (800, 600)

interactor = vtkRenderWindowInteractor()
interactor.render_window = render_window

renderer.ResetCamera()

render_window.Render()
interactor.Start()