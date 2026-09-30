#!/usr/bin/env python3

from dataclasses import dataclass
from pathlib import Path
from sys import argv

# noinspection PyUnresolvedReferences
import vtkmodules.vtkInteractionStyle
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingFreeType
# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkFiltersCore import vtkElevationFilter
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkScalarBarRepresentation,
    vtkScalarBarWidget,
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDiscretizableColorTransferFunction,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def get_program_parameters():
    import argparse
    description = 'Demonstrates how to adjust the colormap scalar range and reverse it.'
    epilogue = '''
    Demonstrates how to adjust a colormap so that the colormap
     scalar range matches the scalar range on the object. 
    Reversal of the colors is also demonstrated. 
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-n', '--newton', action='store_true',
                        help='Use the Newtonian colors colors instead of the modern colors.')
    parser.add_argument('-c', '--continuous', action='store_true',
                        help='Build a continuous colormap.')

    args = parser.parse_args()
    return args.newton, args.continuous


def main():
    newtonian, continuous = get_program_parameters()
    modern = not newtonian
    discretize = not continuous

    ctf_names = ['Modern Rainbow', 'Newton\'s Rainbow']
    if modern:
        ctf_name = ctf_names[0]
    else:
        ctf_name = ctf_names[1]

    colors = vtkNamedColors()

    # RenderWindow Dimensions.
    renderer_width = 400
    renderer_height = 400
    grid_dimensions = 2
    window_width = renderer_width * grid_dimensions
    window_height = renderer_height * grid_dimensions

    ren_win = vtkRenderWindow(size=(window_width, window_height), window_name=f'{Path(argv[0]).name:s}')
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    # Define names.
    names = ['Original', 'Rescaled', 'Original Reversed', 'Rescaled Reversed']
    text_positions = get_text_positions(names, justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                        vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_BOTTOM,
                                        width=0.5,
                                        height=0.1)
    ctf_name_pos = get_text_positions(ctf_names, justification=TextProperty.Justification.VTK_TEXT_LEFT,
                                      vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_TOP,
                                      width=0.7,
                                      height=0.1)

    # Create text properties.
    text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'),
                                    bold=True, italic=False, shadow=True,
                                    font_size=12, font_family_as_string='Courier',
                                    justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                    vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)
    title_text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'),
                                          bold=True, italic=True, shadow=False,
                                          font_size=12,
                                          justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                          vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)
    label_text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'),
                                          bold=False, italic=False, shadow=False,
                                          font_size=12,
                                          justification=TextProperty.Justification.VTK_TEXT_CENTERED,
                                          vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_CENTERED)

    source = vtkConeSource(center=(0.0, 0.0, 0.0), resolution=1, direction=(0, 1, 0), angle=15)
    bounds = source.update().output.bounds
    scalar_range = (bounds[2], bounds[3])
    elevation_filter = vtkElevationFilter(scalar_range=scalar_range, low_point=(0, bounds[2], 0),
                                          high_point=(0, bounds[3], 0))
    source >> elevation_filter

    ctf = dict()
    ctf[names[0]] = get_rainbow_ctf(modern=modern, discretize=discretize, reverse=False)
    ctf[names[1]] = rescale_ctf(ctf[names[0]], *scalar_range)
    ctf[names[2]] = get_rainbow_ctf(modern=modern, discretize=discretize, reverse=True)
    ctf[names[3]] = rescale_ctf(ctf[names[2]], *scalar_range)

    renderers = list()
    text_widgets = list()
    sb_widgets = list()

    # Define viewport boundaries.
    viewports = {names[0]: (0.0, 0.5, 0.5, 1.0),
                 names[1]: (0.0, 0.0, 0.5, 0.5),
                 names[2]: (0.5, 0.5, 1.0, 1.0),
                 names[3]: (0.5, 0.0, 1.0, 0.5),
                 }

    for name in names:
        mapper = vtkPolyDataMapper(lookup_table=ctf[name],
                                   scalar_range=scalar_range,
                                   color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS,
                                   interpolate_scalars_before_mapping=True)
        elevation_filter >> mapper
        actor = vtkActor(mapper=mapper)

        ren = vtkRenderer(viewport=viewports[name], background=colors.GetColor3d('ParaViewBlueGrayBkg'))
        ren.AddActor(actor)

        # Add a title.
        if ' ' in name:
            text_actor = vtkTextActor(input=name.replace(' ', '\n'),
                                      text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_VIEWPORT,
                                      text_property=text_property)
        else:
            text_actor = vtkTextActor(input=name,
                                      text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_VIEWPORT,
                                      text_property=text_property)

        # Create the text representation. Used for positioning the text actor.
        text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
        text_representation.position_coordinate.value = text_positions[name]['p']
        text_representation.position2_coordinate.value = text_positions[name]['p2']

        # Create the text widget, setting the default renderer and interactor.
        text_widgets.append(
            vtkTextWidget(representation=text_representation, text_actor=text_actor,
                          default_renderer=ren, interactor=iren, selectable=False))
        if name == names[0]:
            ctf_text_actor = vtkTextActor(input=ctf_name,
                                          text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_VIEWPORT,
                                          text_property=title_text_property)

            ctf_text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
            ctf_text_representation.position_coordinate.value = ctf_name_pos[ctf_name]['p']
            ctf_text_representation.position2_coordinate.value = ctf_name_pos[ctf_name]['p2']

            # Create the text widget, setting the default renderer and interactor.
            text_widgets.append(
                vtkTextWidget(representation=ctf_text_representation, text_actor=ctf_text_actor,
                              default_renderer=ren, interactor=iren, selectable=False))

        # Add a scalar bar.
        sb_properties = ScalarBarProperties()
        if ' ' in name:
            sb_properties.title_text = name.replace(' ', '\n') + '\n'
        else:
            sb_properties.title_text = name + '\n\n'
        sb_properties.lut = ctf[name]

        # Create the scalar bar, setting the default renderer and interactor.
        sb_widgets.append(make_scalar_bar_widget(sb_properties, text_property, label_text_property,
                                                 default_renderer=ren, interactor=iren))
        renderers.append(ren)

    for ren in renderers:
        ren_win.AddRenderer(ren)

    ren_win.Render()

    for i in range(0, len(renderers)):
        if i % 2 == 0:
            camera = renderers[i].active_camera
            camera.position = (0, 0, 2.69986)
            camera.focal_point = (0, 0, 1.16016e-17)
            camera.view_up = (0, 1, 0)
            camera.distance = 2.69986
            camera.clipping_range = (2.5289, 2.92158)
        else:
            camera = renderers[i].active_camera
            camera.position = (0, 0, 2.68382)
            camera.focal_point = (0, 0, 1.16016e-17)
            camera.view_up = (0, 1, 0)
            camera.distance = 2.68382
            camera.clipping_range = (2.51388, 2.90422)

    for widget in text_widgets:
        widget.On()
    for widget in sb_widgets:
        widget.On()

    ren_win.Render()
    iren.Start()


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


def rescale(values, new_min=0, new_max=1):
    """
    Rescale the values.

    See: https://stats.stackexchange.com/questions/25894/changing-the-scale-of-a-variable-to-0-100

    :param values: The values to be rescaled.
    :param new_min: The new minimum value.
    :param new_max: The new maximum value.
    :return: The rescaled values.
    """
    res = list()
    old_min, old_max = min(values), max(values)
    for v in values:
        new_v = (new_max - new_min) / (old_max - old_min) * (v - old_min) + new_min
        # new_v1 = (new_max - new_min) / (old_max - old_min) * (v - old_max) + new_max
        res.append(new_v)
    return res


def rescale_ctf(old_ctf, new_min=0, new_max=1):
    """
    Rescale the color transfer function.

    :param old_ctf: The color transfer function to rescale.
    :param new_min: The new minimum value.
    :param new_max: The new maximum value.
    :return: A new rescaled color transfer function.
    """
    if new_min > new_max:
        r0 = new_max
        r1 = new_min
    else:
        r0 = new_min
        r1 = new_max

    xv = list()
    rgbv = list()
    nv = [0] * 6
    for i in range(0, old_ctf.GetNumberOfValues()):
        old_ctf.GetNodeValue(i, nv)
        x = nv[0]
        rgb = nv[1:4]
        xv.append(x)
        rgbv.append(rgb)
    xvr = rescale(xv, r0, r1)

    new_ctf = vtkDiscretizableColorTransferFunction(color_space=old_ctf.color_space, scale=old_ctf.scale,
                                                    nan_color=old_ctf.nan_color,
                                                    number_of_values=len(xvr), discretize=old_ctf.discretize
                                                    )
    new_ctf.below_range_color = old_ctf.below_range_color
    new_ctf.use_below_range_color = old_ctf.use_below_range_color
    new_ctf.above_range_color = old_ctf.above_range_color
    new_ctf.use_above_range_color = old_ctf.use_above_range_color

    for i in range(0, len(xvr)):
        new_ctf.AddRGBPoint(xvr[i], *rgbv[i])

    return new_ctf


def get_text_positions(names, justification=0, vertical_justification=0, width=0.96, height=0.1):
    """
    Get viewport positioning information for a list of names.

    :param names: The list of names.
    :param justification: Horizontal justification of the text, default is left.
    :param vertical_justification: Vertical justification of the text, default is bottom.
    :param width: Width of the bounding_box of the text in screen coordinates.
    :param height: Height of the bounding_box of the text in screen coordinates.
    :return: A list of positioning information.
    """
    # The gap between the left or right edge of the screen and the text.
    dx = 0.02
    width = abs(width)
    if width > 0.96:
        width = 0.96

    y0 = 0.01
    height = abs(height)
    if height > 0.9:
        height = 0.9
    dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_TOP:
        y0 = 1.0 - (dy + y0)
        dy = height
    if vertical_justification == TextProperty.VerticalJustification.VTK_TEXT_CENTERED:
        y0 = 0.5 - (dy / 2.0 + y0)
        dy = height

    name_len_min = 0
    name_len_max = 0
    first = True
    for k in names:
        sz = len(k)
        if first:
            name_len_min = name_len_max = sz
            first = False
        else:
            name_len_min = min(name_len_min, sz)
            name_len_max = max(name_len_max, sz)
    text_positions = dict()
    for k in names:
        sz = len(k)
        delta_sz = width * sz / name_len_max
        if delta_sz > width:
            delta_sz = width

        if justification == TextProperty.Justification.VTK_TEXT_CENTERED:
            x0 = 0.5 - delta_sz / 2.0
        elif justification == TextProperty.Justification.VTK_TEXT_RIGHT:
            x0 = 1.0 - dx - delta_sz
        else:
            # Default is left justification.
            x0 = dx

        # For debugging!
        # print(
        #     f'{k:16s}: (x0, y0) = ({x0:3.2f}, {y0:3.2f}), (x1, y1) = ({x0 + delta_sz:3.2f}, {y0 + dy:3.2f})'
        #     f', width={delta_sz:3.2f}, height={dy:3.2f}')
        text_positions[k] = {'p': [x0, y0, 0], 'p2': [delta_sz, dy, 0]}

    return text_positions


class ScalarBarProperties:
    """
    The properties needed for scalar bars.
    """
    named_colors = vtkNamedColors()

    lut = None
    # These are in pixels.
    maximum_dimensions = {'width': 100, 'height': 260}
    title_text = '',
    number_of_labels: int = 7
    # Orientation vertical=True, horizontal=False.
    orientation: bool = True
    # Horizontal and vertical positioning.
    # These are the defaults, don't change these.
    default_v = {'p': (0.85, 0.1), 'p2': (0.1, 0.7)}
    default_h = {'p': (0.10, 0.1), 'p2': (0.7, 0.1)}
    # Modify these as needed.
    position_v = {'p': (0.80, 0.15), 'p2': (0.1, 0.7)}
    position_h = {'p': (0.125, 0.05), 'p2': (0.75, 0.1)}


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


@dataclass(frozen=True)
class Mapper:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_MODE_DEFAULT: int = 0
        VTK_COLOR_MODE_MAP_SCALARS: int = 1
        VTK_COLOR_MODE_DIRECT_SCALARS: int = 2

    @dataclass(frozen=True)
    class ResolveCoincidentTopology:
        VTK_RESOLVE_OFF: int = 0
        VTK_RESOLVE_POLYGON_OFFSET: int = 1
        VTK_RESOLVE_SHIFT_ZBUFFER: int = 2

    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_DEFAULT: int = 0
        VTK_SCALAR_MODE_USE_POINT_DATA: int = 1
        VTK_SCALAR_MODE_USE_CELL_DATA: int = 2
        VTK_SCALAR_MODE_USE_POINT_FIELD_DATA: int = 3
        VTK_SCALAR_MODE_USE_CELL_FIELD_DATA: int = 4
        VTK_SCALAR_MODE_USE_FIELD_DATA: int = 5


@dataclass(frozen=True)
class TextProperty:
    @dataclass(frozen=True)
    class Justification:
        VTK_TEXT_LEFT: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_RIGHT: int = 2

    @dataclass(frozen=True)
    class VerticalJustification:
        VTK_TEXT_BOTTOM: int = 0
        VTK_TEXT_CENTERED: int = 1
        VTK_TEXT_TOP: int = 2


if __name__ == '__main__':
    main()