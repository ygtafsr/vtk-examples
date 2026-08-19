
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QMainWindow

# Register VTK's OpenGL renderer and interaction style before creating the Qt widget.
import vtkmodules.vtkInteractionStyle # for some reason they should be in the import statements !!
import vtkmodules.vtkRenderingOpenGL2 # for some reason they should be in the import statements !!
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import numpy as np

from vtkmodules.util.numpy_support import numpy_to_vtk
from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray
)

from vtkmodules.vtkCommonDataModel import (
    VTK_QUAD
)

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
)


def get_grid():
    
    coordinates = np.array([
        [0.0, 0.0, 0.0],  # point 0
        [1.0, 0.0, 0.0],  # point 1
        [1.0, 1.0, 0.0],  # point 2
        [0.0, 1.0, 0.0],  # point 3
    ], dtype=np.float64)

    points = Points(data=coordinates)

    connectivity = np.array([
        [0, 1, 2, 3],
    ], dtype=np.int64)

    connectivity_flat = connectivity.ravel()

    cell_types = np.array(
        [VTK_QUAD],
        dtype=np.uint8,
    )

    vtk_cell_types = numpy_to_vtk(cell_types, deep=True)

    offsets = np.array([0, 4], dtype=np.int64)

    cells = CellArray(offsets=offsets, connectivity=connectivity_flat)

    # ============================================================
    # 7. Create vtkUnstructuredGrid
    # ============================================================

    grid = UnstructuredGrid(points=points, cells=(vtk_cell_types, cells))

    return grid

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("VTK + PySide6")
        self.resize(1000, 700)

        # Qt widget containing the VTK render window
        self.vtk_widget = QVTKRenderWindowInteractor(self)

        self.setCentralWidget(self.vtk_widget)

        # VTK renderer
        self.renderer = vtkRenderer()
        self.renderer.SetBackground(0.12, 0.16, 0.20)

        # Connect renderer to the Qt widget's render window
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # Get VTK interactor
        self.interactor = self.vtk_widget.GetRenderWindow().GetInteractor()       

        # -------------------------
        # VTK rendering pipeline
        # -------------------------

        ugrid = get_grid()

        mapper = vtkDataSetMapper(input_data=ugrid)

        actor = vtkActor(mapper=mapper)
        #actor.property.representation = VTK_WIREFRAME
        actor.property.color = (0.95, 0.75, 0.25)
        actor.property.line_width = 3

        self.renderer.AddActor(actor)

        # Camera
        self.renderer.ResetCamera()

        # Initialize interaction
        self.vtk_widget.Initialize()

        # Render
        QTimer.singleShot(0, self.vtk_widget.GetRenderWindow().Render)

        # --------------------------------------------


app = QApplication(sys.argv)

window = MainWindow()
window.show()

sys.exit(app.exec())