import numpy as np

from vtkmodules.util.data_model import Points, PolyData
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
)

from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import (
    vtkCellArray,
    vtkPolyData
)

from vtkmodules.vtkCommonColor import vtkNamedColors

from vtkmodules.vtkFiltersSources import vtkSphereSource

from vtkmodules.util.data_model import PolyData, Points, CellArray


def add_3d_point(renderer : vtkRenderer, coordinates : np.ndarray) -> None:



    sphereSource = vtkSphereSource(center=coordinates,
                                   radius=0.05,
                                   phi_resolution=100,
                                   theta_resolution=100)

    mapper = vtkPolyDataMapper()
    mapper = vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())

    actor = vtkActor(mapper=mapper)
    actor.property.color = vtkNamedColors().GetColor3d('Tomato')
    actor.property.point_size = 20

    renderer.AddActor(actor)

    """
    points = Points(data=coordinates)
    vertices = CellArray()
    vertices.InsertNextCell(1, [0])
    poly_data = PolyData(points=points)
    mapper = vtkPolyDataMapper(input_data=poly_data)
    actor = vtkActor(mapper=mapper)
    actor.property.color = (1.0, 0.0, 0.0)
    actor.property.point_size = 15
    renderer.AddActor(actor)
    """