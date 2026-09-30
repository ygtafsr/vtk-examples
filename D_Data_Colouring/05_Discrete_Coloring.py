
"""

"""

from dataclasses import dataclass
import numpy as np

# VTK native OpenGL backend
import vtkmodules.vtkInteractionStyle
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.util.numpy_support import numpy_to_vtk

from vtkmodules.util.data_model import (
    UnstructuredGrid,
    Points,
    CellArray
)

from vtkmodules.vtkCommonDataModel import (
    VTK_QUAD
)

from vtkmodules.vtkInteractionWidgets import (
    vtkScalarBarRepresentation,
    vtkScalarBarWidget,
    vtkTextRepresentation,
    vtkTextWidget
)

from vtkmodules.vtkCommonCore import vtkLookupTable
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkDiscretizableColorTransferFunction,
    vtkPolyDataMapper,
    vtkTextActor,
    vtkTextProperty
)


@dataclass(frozen=True)
class ColorTransferFunction:
    @dataclass(frozen=True)
    class ColorSpace:
        VTK_CTF_RGB: int = 0
        VTK_CTF_HSV: int = 1
        VTK_CTF_LAB: int = 2
        VTK_CTF_DIVERGING: int = 3
        VTK_CTF_LAB_CIEDE2000: int = 4
        VTK_CTF_STEP: int = 5

    @dataclass(frozen=True)
    class Scale:
        VTK_CTF_LINEAR: int = 0
        VTK_CTF_LOG10: int = 1

def get_rainbow_ctf(modern=True, discretize=True, reverse=False):
    """
    Generate the color transfer function.

    The seven colors corresponding to the colors that Isaac Newton labeled
        when dividing the spectrum of visible light in 1672 are used.

    The modern variant of these colors is used by default.

    See: [Rainbow](https://en.wikipedia.org/wiki/Rainbow)

    :param modern: Selects either the modern colors or Newton's original seven colors.
    :param discretize: Selects whether the CTF is discretized or not.
    :param reverse: Reverse the colors in the CTF.

    :return: The color transfer function.
    """

    # name: Rainbow, creator: Andrew Maclean
    # interpolationspace: RGB, space: rgb
    # file name:

    indices = {0: -1.0, 1: -2.0 / 3.0, 2: -1.0 / 3.0, 3: 0, 4: 1.0 / 3.0, 5: 2.0 / 3.0, 6: 1.0}

    # Red, Orange #ff8000, Yellow, Green #00ff00, Cyan, Blue, Violet #8000ff
    modern_rainbow = {0: (1.0, 0.0, 0.0), 1: (1.0, 128.0 / 255.0, 0.0), 2: (1.0, 1.0, 0.0), 3: (0.0, 1.0, 0.0),
                      4: (0.0, 1.0, 1.0), 5: (0.0, 0.0, 1.0), 6: (128.0 / 255.0, 0.0, 1.0)}
    # Red, Orange #00a500, Yellow, Green #008000, Blue #0099ff, Indigo #4400ff, Violet #9900ff
    # The mnemonic here is: "Rip out your guts before I vomit."
    newtons_rainbow = {0: (1.0, 0.0, 0.0), 1: (1.0, 165.0 / 255.0, 0.0), 2: (1.0, 1.0, 0.0),
                       3: (0.0, 125.0 / 255.0, 0.0), 4: (0.0, 153.0 / 255.0, 1.0), 5: (68.0 / 255.0, 0, 153.0 / 255.0),
                       6: (153.0 / 255.0, 0.0, 1.0)}
    
    ctf = vtkDiscretizableColorTransferFunction(color_space=ColorTransferFunction.ColorSpace.VTK_CTF_RGB,
                                                scale=ColorTransferFunction.Scale.VTK_CTF_LINEAR,
                                                nan_color=(0.5, 0.5, 0.5),
                                                below_range_color=(0.0, 0.0, 0.0), use_below_range_color=True,
                                                above_range_color=(1.0, 1.0, 1.0), use_above_range_color=True,
                                                number_of_values=len(indices), discretize=discretize)

    if modern:
        if reverse:
            for index, (key, value) in enumerate(reversed(modern_rainbow.items())):
                ctf.AddRGBPoint(indices[index], *value)
        else:
            for k, v in indices.items():
                ctf.AddRGBPoint(v, *modern_rainbow[k])
    else:
        if reverse:
            for index, (key, value) in enumerate(reversed(newtons_rainbow.items())):
                ctf.AddRGBPoint(indices[index], *value)
        else:
            for k, v in indices.items():
                ctf.AddRGBPoint(v, *newtons_rainbow[k])

    ctf.Build()
    return ctf

def make_scalar_bar_widget(scalar_bar_properties, title_text_property, label_text_property, default_renderer,
                           interactor):
    """
    Make a scalar bar widget.

    :param scalar_bar_properties: The lookup table, title name, maximum dimensions in pixels and position.
    :param title_text_property: The properties for the title.
    :param label_text_property: The properties for the labels.
    :param default_renderer: The default renderer.
    :param interactor: The vtkInteractor.
    :return: The scalar bar widget.
    """
    sb_actor = vtkScalarBarActor(lookup_table=scalar_bar_properties.lut, title=scalar_bar_properties.title_text,
                                 unconstrained_font_size=True, number_of_labels=scalar_bar_properties.number_of_labels,
                                 title_text_property=title_text_property, label_text_property=label_text_property

                                 )
    sb_actor.SetLabelFormat('{:0.2f}')

    sb_rep = vtkScalarBarRepresentation(enforce_normalized_viewport_bounds=True,
                                        orientation=scalar_bar_properties.orientation)

    # Set the position.
    sb_rep.position_coordinate.SetCoordinateSystemToNormalizedViewport()
    sb_rep.position2_coordinate.SetCoordinateSystemToNormalizedViewport()
    if scalar_bar_properties.orientation:
        sb_rep.position_coordinate.value = scalar_bar_properties.position_v['p']
        sb_rep.position2_coordinate.value = scalar_bar_properties.position_v['p2']
    else:
        sb_rep.position_coordinate.value = scalar_bar_properties.position_h['p']
        sb_rep.position2_coordinate.value = scalar_bar_properties.position_h['p2']

    widget = vtkScalarBarWidget(representation=sb_rep, scalar_bar_actor=sb_actor, default_renderer=default_renderer,
                                interactor=interactor, enabled=True)

    return widget


coordinates = np.array([
    [0.0, 0.0, 0.0],    # point 0
    [5.0, 0.0, 0.0],    # point 1
    [10.0, 0.0, 0.0],   # point 2
    [15.0, 0.0, 0.0],   # point 3
    [0.0, 5.0, 0.0],    # point 4
    [5.0, 5.0, 0.0],    # point 5
    [10.0, 5.0, 0.0],   # point 6
    [15.0, 5.0, 0.0],   # point 7
], dtype=np.float64)

points = Points(data=coordinates)

# ============================================================
# Create vtkCellArray
# ============================================================

connectivity = np.array(
    [
        [0, 1, 5, 4],
        [1, 2, 6, 5],
        [2, 3, 7, 6],
    ], dtype=np.int64)

connectivity_flat = connectivity.ravel()

cell_types = np.array(
    [
        [VTK_QUAD],
        [VTK_QUAD],
        [VTK_QUAD],
    ], dtype=np.uint8)

vtk_cell_types = numpy_to_vtk(cell_types, deep=True)

offsets = np.array([0, 4, 8, 12], dtype=np.int64)

cells = CellArray(offsets=offsets, connectivity=connectivity_flat)

# ============================================================
# Create vtkUnstructuredGrid
# ============================================================

grid = UnstructuredGrid(points=points, cells=(vtk_cell_types, cells))

# -------------------------
# Create Scalar Data
# -------------------------

stress = np.array(
    [100, 150, 200, 250,
     300, 350, 400, 450],
    dtype=np.float64,
)

grid.point_data["von_mises_stress"] = stress
print(grid.point_data["von_mises_stress"][1])

### !!! Set Active Scalars !!!
grid.point_data.SetActiveScalars("von_mises_stress")


# ============================================================
# VTK rendering pipeline
# ============================================================

mapper = vtkDataSetMapper(input_data=grid)
mapper.scalar_visibility = True
mapper.scalar_range = (stress.min(), stress.max())

# Create a lookup table scalar to colour mapping adjustment
lookup = vtkLookupTable(number_of_table_values=4,
                        range=(100, 450))
mapper.lookup_table = lookup

actor = vtkActor(mapper=mapper)
#actor.property.representation = VTK_WIREFRAME
actor.property.edge_visibility = True
actor.property.edge_color = (0.1, 0.1, 0.1)
actor.property.line_width = 1

# ============================================================
# Renderer
# ============================================================

renderer = vtkRenderer()

renderer.AddActor(actor)
renderer.SetBackground(0.15, 0.15, 0.15)
renderer.ResetCamera()


# ============================================================
# Render Window
# ============================================================

render_window = vtkRenderWindow()

render_window.AddRenderer(renderer)
render_window.SetSize(1000, 700)


# ============================================================
# Interactor
# ============================================================

interactor = vtkRenderWindowInteractor()

interactor.SetRenderWindow(render_window)


# Color Mapping


ctf[names[0]] = get_rainbow_ctf(modern=modern, discretize=discretize, reverse=False)
ctf[names[1]] = rescale_ctf(ctf[names[0]], *scalar_range)
ctf[names[2]] = get_rainbow_ctf(modern=modern, discretize=discretize, reverse=True)



# ============================================================
# Start
# ============================================================

render_window.Render()
interactor.Start()
