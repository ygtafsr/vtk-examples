"""
https://examples.vtk.org/site/Cxx/Visualization/ElevationBandsWithGlyphs/
"""

#!/usr/bin/env python3

import copy
import math
from collections import namedtuple
from dataclasses import dataclass
from pathlib import Path

# noinspection PyUnresolvedReferences
import vtkmodules.vtkRenderingOpenGL2
from vtk.util import numpy_support
from vtkmodules.vtkCommonColor import (
    vtkColorSeries,
    vtkNamedColors
)
from vtkmodules.vtkCommonComputationalGeometry import (
    vtkParametricRandomHills,
    vtkParametricTorus
)
from vtkmodules.vtkCommonCore import (
    vtkDoubleArray,
    vtkFloatArray,
    vtkLookupTable,
    vtkPoints,
    vtkVariant,
    vtkVariantArray
)
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkCommonTransforms import vtkTransform
from vtkmodules.vtkFiltersCore import (
    vtkCleanPolyData,
    vtkDelaunay2D,
    vtkElevationFilter,
    vtkGlyph3D,
    vtkMaskPoints,
    vtkPolyDataNormals,
    vtkPolyDataTangents,
    vtkReverseSense,
    vtkTriangleFilter
)
from vtkmodules.vtkFiltersGeneral import (
    vtkTransformFilter
)
from vtkmodules.vtkFiltersModeling import vtkBandedPolyDataContourFilter
from vtkmodules.vtkFiltersSources import (
    vtkArrowSource,
    vtkParametricFunctionSource,
    vtkPlaneSource,
    vtkSphereSource,
    vtkSuperquadricSource
)
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkInteractionWidgets import (
    vtkCameraOrientationWidget,
    vtkOrientationMarkerWidget,
    vtkScalarBarRepresentation,
    vtkScalarBarWidget,
    vtkTextRepresentation,
    vtkTextWidget
)
from vtkmodules.vtkRenderingAnnotation import (
    vtkAxesActor,
    vtkScalarBarActor
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkTextActor,
    vtkTextProperty
)


def get_program_parameters():
    import argparse
    description = 'Color a surface using elevations, adding normal vectors colored by elevation.'
    epilogue = '''
    For example: "parametric hills" -f
                 Will display the surface colored by elevation along with surface normals.
    '''
    parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('surface_name', nargs='?', default='parametric hills',
                        help='The name of the surface - enclose the name in quotes if it has spaces.')
    parser.add_argument('-f', '--frequency_table', action='store_true', help='Display the frequency table.')
    parser.add_argument('-o', '--omw', action='store_true',
                        help='Use an OrientationMarkerWidget instead of a CameraOrientationWidget.')

    args = parser.parse_args()
    return args.surface_name, args.frequency_table, args.omw


def main(argv):
    # ------------------------------------------------------------
    # Create the surface, lookup tables, contour filter etc.
    # ------------------------------------------------------------
    surface_name, frequency_table, use_omw = get_program_parameters()
    available_surfaces = ['hills', 'parametric hills', 'parametric torus', 'plane', 'sphere', 'torus']
    # Surfaces whose curvatures need to be adjusted along the edges of the surface or constrained.
    needs_adjusting = ['hills', 'parametric hills', 'parametric torus', 'plane']

    surface_name = ' '.join(surface_name.lower().replace('_', ' ').split())
    if surface_name in ['parametrichills', 'random hills', 'randomhills']:
        surface_name = 'parametric hills'
    if surface_name == 'parametrictorus':
        surface_name = 'parametric torus'
    if surface_name.lower() not in available_surfaces:
        print('Nonexistent surface:', surface_name)
        print('Available surfaces are:')
        asl = sorted(available_surfaces)
        asl = [asl[i].title() for i in range(0, len(asl))]
        asl = [asl[i:i + 5] for i in range(0, len(asl), 5)]
        for i in range(0, len(asl)):
            s = ', '.join(asl[i])
            if i < len(asl) - 1:
                s += ','
            print(f'   {s}')
        print('If a name has spaces in it, delineate the name with quotes e.g. "parametric hills"')
        return

    source = get_source(surface_name)
    if not source:
        print('The surface is not available.')
        return

    elev_bg = get_elevation_glyphs(surface_name, source,
                                   precision=10, frequency_table=frequency_table,
                                   nearest_integer=False)

    # ------------------------------------------------------------
    # Create the mappers and actors
    # ------------------------------------------------------------

    colors = vtkNamedColors()

    src_mapper = vtkPolyDataMapper(input_connection=elev_bg.bcf.output_port,
                                   lookup_table=elev_bg.lut,
                                   scalar_range=elev_bg.scalar_range,
                                   scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_CELL_DATA)
    src_actor = vtkActor(mapper=src_mapper)

    # Create contour edges.
    edge_mapper = vtkPolyDataMapper(input_data=elev_bg.bcf.contour_edges_output,
                                    resolve_coincident_topology=Mapper.ResolveCoincidentTopology.VTK_RESOLVE_POLYGON_OFFSET)
    edge_actor = vtkActor(mapper=edge_mapper)
    edge_actor.property.color = colors.GetColor3d('Black')

    glyph_mapper = vtkPolyDataMapper(input_connection=elev_bg.glyphs.output_port,
                                     lookup_table=elev_bg.lut1,
                                     scalar_range=elev_bg.scalar_range,
                                     color_mode=Mapper.ColorMode.VTK_COLOR_MODE_MAP_SCALARS,
                                     scalar_visibility=True,
                                     scalar_mode=Mapper.ScalarMode.VTK_SCALAR_MODE_USE_POINT_FIELD_DATA)

    glyph_mapper.SelectColorArray('Elevation')
    glyph_actor = vtkActor(mapper=glyph_mapper)

    window_width = 800
    window_height = 800

    # ------------------------------------------------------------
    # Create the RenderWindow, Renderer and Interactor
    # ------------------------------------------------------------
    ren = vtkRenderer(background=colors.GetColor3d('ParaViewBlueGrayBkg'))
    ren_win = vtkRenderWindow(size=(window_width, window_height),
                              window_name=f'{Path(argv[0]).stem:s}')

    ren_win.AddRenderer(ren)
    iren = vtkRenderWindowInteractor()
    iren.render_window = ren_win

    style = vtkInteractorStyleTrackballCamera()
    iren.interactor_style = style

    # Position the source name according to its length.
    text_positions = get_text_positions(available_surfaces,
                                        justification=TextProperty.Justification.VTK_TEXT_LEFT,
                                        vertical_justification=TextProperty.VerticalJustification.VTK_TEXT_TOP,
                                        width=0.25)

    title_text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'), bold=True, italic=True, shadow=True,
                                          font_size=12,
                                          justification=TextProperty.Justification.VTK_TEXT_LEFT)
    label_text_property = vtkTextProperty(color=colors.GetColor3d('AliceBlue'), bold=False, italic=False, shadow=True,
                                          font_size=12,
                                          justification=TextProperty.Justification.VTK_TEXT_LEFT)
    text_actor = vtkTextActor(input=surface_name.title(), text_scale_mode=vtkTextActor.TEXT_SCALE_MODE_NONE,
                              text_property=title_text_property)
    # Create the text representation. Used for positioning the text actor.
    text_representation = vtkTextRepresentation(enforce_normalized_viewport_bounds=True)
    text_representation.position_coordinate.value = text_positions[surface_name]['p']
    text_representation.position2_coordinate.value = text_positions[surface_name]['p2']
    text_widget = vtkTextWidget(representation=text_representation, text_actor=text_actor,
                                default_renderer=ren, interactor=iren,
                                selectable=False, enabled=True)

    elev_sbp = ScalarBarProperties()
    elev_sbp.title_text = elev_bg.glyph_type.replace('_', '\n') + '\n'
    elev_sbp.number_of_labels = len(elev_bg.labels)
    # lut puts the lowest value at the top of the vertical scalar bar.
    # lutr puts the highest value at the top of the vertical scalar bar.
    elev_sbp.lut = elev_bg.lutr
    elev_sbp.orientation = True
    if elev_sbp.number_of_labels == 1:
        elev_sbp.position_v = position_sbw_v(elev_sbp.number_of_labels, elev_bg.lut_max_bands)
    else:
        elev_sbp.position_v = position_sbw_v(elev_sbp.number_of_labels, elev_bg.lut_max_bands)
    scalar_bar_widget = make_scalar_bar_widget(elev_sbp, title_text_property,
                                               label_text_property, ren, iren)

    # Important: The interactor must be set prior to enabling the widget.
    if use_omw:
        rgba = [0.0] * 4
        colors.GetColor("Carrot", rgba)
        rgb = tuple(rgba[:3])
        omw = vtkOrientationMarkerWidget(orientation_marker=vtkAxesActor(),
                                         interactor=iren, default_renderer=ren,
                                         outline_color=rgb, viewport=(0.8, 0.8, 1.0, 1.0), zoom=1.0, enabled=True,
                                         interactive=True)
    else:
        cow = vtkCameraOrientationWidget(parent_renderer=ren)
        # Enable the widget.
        cow.On()

    # Add actors
    ren.AddViewProp(src_actor)
    ren.AddViewProp(edge_actor)
    ren.AddViewProp(glyph_actor)

    ren.ResetCamera()

    adjust_camera_parameters(surface_name, ren)

    ren_win.Render()
    iren.Start()


def generate_elevations(src):
    """
    Generate elevations over the surface.
    :param: src - the vtkPolyData source.
    :return: - vtkPolyData source with elevations.
    """
    bounds = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    src.GetBounds(bounds)
    if abs(bounds[2]) < 1.0e-8 and abs(bounds[3]) < 1.0e-8:
        bounds[2] = 0.0
        bounds[3] = 1.0e-8
    elev_filter = vtkElevationFilter(input_data=src,
                                     low_point=(0, bounds[2], 0),
                                     high_point=(0, bounds[3], 0),
                                     scalar_range=(bounds[2], bounds[3]))
    elev_filter.update()
    return elev_filter.GetPolyDataOutput()


def get_hills():
    # Create four hills on a plane.
    # This will have regions of negative, zero and positive Gaussian curvatures.

    x_res = 50
    y_res = 50
    x_min = -5.0
    x_max = 5.0
    dx = (x_max - x_min) / (x_res - 1)
    y_min = -5.0
    y_max = 5.0
    dy = (y_max - y_min) / (x_res - 1)

    # Make a grid.
    points = vtkPoints()
    for i in range(0, x_res):
        x = x_min + i * dx
        for j in range(0, y_res):
            y = y_min + j * dy
            points.InsertNextPoint(x, y, 0)

    # Add the grid points to a polydata object.
    plane = vtkPolyData(points=points)

    # Triangulate the grid.
    delaunay = vtkDelaunay2D(input_data=plane)

    polydata = delaunay.update().output

    elevation = vtkDoubleArray(number_of_tuples=points.number_of_points)

    #  We define the parameters for the hills here.
    # [[0: x0, 1: y0, 2: x variance, 3: y variance, 4: amplitude]...]
    hd = [[-2.5, -2.5, 2.5, 6.5, 3.5], [2.5, 2.5, 2.5, 2.5, 2],
          [5.0, -2.5, 1.5, 1.5, 2.5], [-5.0, 5, 2.5, 3.0, 3]]
    xx = [0.0] * 2
    for i in range(0, points.number_of_points):
        x = list(polydata.GetPoint(i))
        for j in range(0, len(hd)):
            xx[0] = (x[0] - hd[j][0] / hd[j][2]) ** 2.0
            xx[1] = (x[1] - hd[j][1] / hd[j][3]) ** 2.0
            x[2] += hd[j][4] * math.exp(-(xx[0] + xx[1]) / 2.0)
            polydata.GetPoints().SetPoint(i, x)
            elevation.SetValue(i, x[2])

    textures = vtkFloatArray(name='Textures', number_of_components=2, number_of_tuples=2 * polydata.number_of_points)

    for i in range(0, x_res):
        tc = [i / (x_res - 1.0), 0.0]
        for j in range(0, y_res):
            # tc[1] = 1.0 - j / (y_res - 1.0)
            tc[1] = j / (y_res - 1.0)
            textures.SetTuple(i * y_res + j, tc)

    polydata.GetPointData().SetScalars(elevation)
    polydata.GetPointData().GetScalars().name = 'Elevation'
    polydata.GetPointData().TCoords = textures

    normals = vtkPolyDataNormals(feature_angle=30, splitting=False)

    tr = vtkTransform()
    tr.RotateX(-90)

    tf = vtkTransformFilter(transform=tr)

    return (polydata >> normals >> tf).update().output


def get_parametric_hills():
    """
    Make a parametric hills surface as the source.
    :return: vtkPolyData with normal and scalar data.
    """
    random_seed = 1
    number_of_hills = 30
    # If you want a plane
    # hill_amplitude=0
    fn = vtkParametricRandomHills(random_seed=random_seed, number_of_hills=number_of_hills)
    fn.AllowRandomGenerationOn()

    u_resolution = 50
    v_resolution = 50
    source = vtkParametricFunctionSource(parametric_function=fn,
                                         u_resolution=u_resolution, v_resolution=v_resolution,
                                         generate_texture_coordinates=True)
    source.SetScalarModeToZ()
    source.update()
    # Rename the scalars to 'Elevation' since we are using the Z-scalars as elevations.
    source.output.GetPointData().GetScalars().SetName('Elevation')

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    tr = vtkTransform()
    tr.Translate(0.0, 5.0, 15.0)
    tr.RotateX(-90.0)

    tf = vtkTransformFilter(transform=tr)

    return (source >> tangents >> tf).update().output


def get_parametric_torus():
    """
    Make a parametric torus as the source.
    :return: vtkPolyData with normal and scalar data.
    """

    fn = vtkParametricTorus(ring_radius=5, cross_section_radius=2)

    source = vtkParametricFunctionSource(parametric_function=fn,
                                         u_resolution=50, v_resolution=50,
                                         generate_texture_coordinates=True)
    source.SetScalarModeToZ()
    source.update()
    # Rename the scalars to 'Elevation' since we are using the Z-scalars as elevations.
    source.output.GetPointData().GetScalars().SetName('Elevation')

    # Build the tangents.
    tangents = vtkPolyDataTangents()

    tr = vtkTransform()
    tr.RotateX(-90.0)

    t = vtkTransformFilter(transform=tr)

    return (source >> tangents >> t).update().output


def get_plane():
    """
    Make a plane as the source.
    :return: vtkPolyData with normal and scalar data.
    """

    source = vtkPlaneSource(origin=(-10.0, -10.0, 0.0),
                            point2=(-10.0, 10.0, 0.0), point1=(10.0, -10.0, 0.0),
                            x_resolution=10, y_resolution=10)

    tr = vtkTransform()
    tr.Translate(0.0, 0.0, 0.0)
    tr.RotateX(-90.0)

    tf = vtkTransformFilter(transform=tr)

    # We have a m x n array of quadrilaterals arranged as a regular tiling in a
    # plane. So pass it through a triangle filter since the curvature filter only
    # operates on polys.
    tri = vtkTriangleFilter()

    # Pass it though a CleanPolyDataFilter and merge any points which
    # are coincident, or very close
    cleaner = vtkCleanPolyData(tolerance=0.005)

    return (source >> tf >> tri >> cleaner).update().output


def get_sphere():
    source = vtkSphereSource(center=(0.0, 0.0, 0.0), radius=1.0,
                             theta_resolution=32, phi_resolution=32)

    return source.update().output


def get_torus():
    """
    Make a torus as the source.
    :return: vtkPolyData with normal and scalar data.
    """
    source = vtkSuperquadricSource(center=(0.0, 0.0, 0.0), scale=(1.0, 1.0, 1.0),
                                   phi_resolution=64,
                                   theta_resolution=64, theta_roundness=1,
                                   thickness=0.5, size=10, toroidal=True)

    # The quadric is made of strips, so pass it through a triangle filter as
    # the curvature filter only operates on polys
    tri = vtkTriangleFilter()

    # The quadric has nasty discontinuities from the way the edges are generated
    # so let's pass it though a CleanPolyDataFilter and merge any points which
    # are coincident, or very close
    cleaner = vtkCleanPolyData(tolerance=0.005)

    return (source >> tri >> cleaner).update().output


def get_source(source):
    surface = source.lower()
    if surface == 'hills':
        return get_hills()
    elif surface == 'parametric hills':
        return get_parametric_hills()
    elif surface == 'parametric torus':
        return get_parametric_torus()
    elif surface == 'plane':
        return generate_elevations(get_plane())
    elif surface == 'sphere':
        return generate_elevations(get_sphere())
    elif surface == 'torus':
        return generate_elevations(get_torus())
    print('The surface is not available.')
    print('Using parametric hills instead.')
    return get_parametric_hills()


def reverse_lut(lut):
    """
    Create a lookup table with the colors reversed.
    :param: lut - An indexed lookup table.
    :return: The reversed indexed lookup table.
    """
    lutr = vtkLookupTable()
    lutr.DeepCopy(lut)
    t = lut.number_of_table_values - 1
    rev_range = reversed(list(range(t + 1)))
    for i in rev_range:
        rgba = [0.0] * 3
        v = float(i)
        lut.GetColor(v, rgba)
        rgba.append(lut.GetOpacity(v))
        lutr.SetTableValue(t - i, rgba)
    t = lut.number_of_annotated_values - 1
    rev_range = reversed(list(range(t + 1)))
    for i in rev_range:
        lutr.SetAnnotation(t - i, lut.GetAnnotation(i))
    return lutr


def get_glyphs(src, scale_factor=1.0, reverse_normals=False):
    """
    Glyph the normals on the surface.

    You may need to adjust the parameters for mask_pts, arrow and glyph for a
    nice appearance.

    :param: src - the polydata surface to glyph.
    :param: reverse_normals - if True the normals on the surface are reversed.
    :return: The glyph object.

    """
    if reverse_normals:
        # Sometimes the contouring algorithm can create a volume whose gradient
        # vector and ordering of polygon (using the right hand rule) are
        # inconsistent. vtkReverseSense cures this problem.
        reverse = vtkReverseSense(reverse_cells=True, reverse_normals=True)
        # Choose a random subset of points.
        mask_pts = vtkMaskPoints(on_ratio=5, random_mode=True)
        src >> reverse >> mask_pts
    else:
        # Choose a random subset of points.
        mask_pts = vtkMaskPoints(on_ratio=5, random_mode=True)
        src >> mask_pts

    # Source for the glyph filter
    arrow = vtkArrowSource(tip_resolution=16, tip_length=0.3, tip_radius=0.1)

    # glyph = vtkGlyph3D()
    glyphs = vtkGlyph3D(source_connection=arrow.output_port,
                        input_connection=mask_pts.output_port,
                        scaling=True, scale_mode=Glyph3D.ScaleMode.VTK_SCALE_BY_VECTOR,
                        scale_factor=scale_factor, orient=True, clamping=False,
                        vector_mode=Glyph3D.VectorMode.VTK_USE_NORMAL,
                        color_mode=Glyph3D.ColorMode.VTK_COLOR_BY_VECTOR)
    return glyphs


def get_bands(scalar_range, number_of_bands, precision=2, nearest_integer=False):
    """
    Divide a range into bands
    :param: scalar_range - [min, max] the range that is to be covered by the bands.
    :param: number_of_bands - The number of bands, a positive integer.
    :param: precision - The decimal precision of the bounds.
    :param: nearest_integer - If True then [floor(min), ceil(max)] is used.
    :return: A dictionary consisting of the band number and [min, midpoint, max] for each band.
    """
    prec = abs(precision)
    if prec > 14:
        prec = 14

    bands = dict()
    if (scalar_range[1] < scalar_range[0]) or (number_of_bands <= 0):
        return bands
    x = list(scalar_range)
    if nearest_integer:
        x[0] = math.floor(x[0])
        x[1] = math.ceil(x[1])
    dx = (x[1] - x[0]) / float(number_of_bands)
    b = [x[0], x[0] + dx / 2.0, x[0] + dx]
    i = 0
    while i < number_of_bands:
        b = list(map(lambda ele_b: round(ele_b, prec), b))
        if i == 0:
            b[0] = x[0]
        bands[i] = b
        b = [b[0] + dx, b[1] + dx, b[2] + dx]
        i += 1
    return bands


def get_custom_bands(scalar_range, number_of_bands, my_bands):
    """
    Divide a range into custom bands.

    You need to specify each band as a list [r1, r2] where r1 < r2 and append these to a list.
    The list should ultimately look like this: [[r1, r2], [r2, r3], [r3, r4]...]

    :param: scalar_range - [min, max] the range that is to be covered by the bands.
    :param: number_of_bands - the number of bands, a positive integer.
    :return: A dictionary consisting of band number and [min, midpoint, max] for each band.
    """
    bands = dict()
    if (scalar_range[1] < scalar_range[0]) or (number_of_bands <= 0):
        return bands
    x = my_bands
    # Determine the index of the range minimum and range maximum.
    idx_min = 0
    for idx in range(0, len(my_bands)):
        if my_bands[idx][1] > scalar_range[0] >= my_bands[idx][0]:
            idx_min = idx
            break

    idx_max = len(my_bands) - 1
    for idx in range(len(my_bands) - 1, -1, -1):
        if my_bands[idx][1] > scalar_range[1] >= my_bands[idx][0]:
            idx_max = idx
            break

    # Set the minimum to match the range minimum.
    x[idx_min][0] = scalar_range[0]
    x[idx_max][1] = scalar_range[1]
    x = x[idx_min: idx_max + 1]
    for idx, e in enumerate(x):
        bands[idx] = [e[0], e[0] + (e[1] - e[0]) / 2, e[1]]
    return bands


def get_frequencies(bands, src):
    """
    Count the number of scalars in each band.
    The scalars used are the active scalars in the polydata.

    :param: bands - The bands.
    :param: src - The vtkPolyData source.
    :return: The frequencies of the scalars in each band.
    """
    freq = dict()
    for i in range(len(bands)):
        freq[i] = 0
    tuples = src.GetPointData().GetScalars().GetNumberOfTuples()
    for i in range(tuples):
        x = src.GetPointData().GetScalars().GetTuple1(i)
        for j in range(len(bands)):
            if x <= bands[j][2]:
                freq[j] += 1
                break
    return freq


def adjust_ranges(bands, freq):
    """
    The bands and frequencies are adjusted so that the first and last
     frequencies in the range are non-zero.
    :param bands: The dictionary containing the bands.
    :param freq: The frequency dictionary.
    :return: Adjusted bands and frequencies.
    """
    # Get the indices of the first and last non-zero elements.
    first = 0
    for k, v in freq.items():
        if v != 0:
            first = k
            break
    rev_keys = list(freq.keys())[::-1]
    last = rev_keys[0]
    for idx in list(freq.keys())[::-1]:
        if freq[idx] != 0:
            last = idx
            break
    # Now adjust the ranges.
    min_key = min(freq.keys())
    max_key = max(freq.keys())
    for idx in range(min_key, first):
        freq.pop(idx)
        bands.pop(idx)
    for idx in range(last + 1, max_key + 1):
        freq.popitem()
        bands.popitem()
    old_keys = freq.keys()
    adj_freq = dict()
    adj_bands = dict()

    for idx, k in enumerate(old_keys):
        adj_freq[idx] = freq[k]
        adj_bands[idx] = bands[k]

    return adj_bands, adj_freq


def get_elevation_glyphs(surface_name, source,
                         precision, frequency_table=False, nearest_integer=False):
    """
    Get elevation glyphs and the corresponding banded polydata filter for the surface.
    :param: surface_name - the name of the surface.
    :param: src - the polydata surface to glyph.
    :param: precision - the precision level.
    :param: frequency_table - If true, display a frequency table corresponding to the bands.
    :param: nearest_integer - If true, use the nearest integer when generating the bands.
    :return: A dataclass holding glyphs, bcf, lut, lutr, lut1, lut1r scalar_range, labels

    """
    # The length of the normal arrow glyphs.
    scale_factor = 1.0
    if surface_name == 'hills':
        scale_factor = 0.5
    elif surface_name == 'sphere':
        scale_factor = 0.2

    source.point_data.active_scalars = 'Elevation'
    scalar_range = source.point_data.GetScalars('Elevation').range

    max_lut_bands = 0

    color_series = vtkColorSeries()
    if surface_name in ['hills', 'parametric hills']:
        color_series.color_scheme = color_series.BREWER_DIVERGING_BROWN_BLUE_GREEN_8
        max_lut_bands = 8
    else:
        color_series.color_scheme = color_series.BREWER_DIVERGING_BROWN_BLUE_GREEN_6
        max_lut_bands = 6

    lut = vtkLookupTable()
    color_series.BuildLookupTable(lut, color_series.CATEGORICAL)
    lut.nan_color = (0, 0, 0, 1)
    lut.table_range = scalar_range

    if surface_name in ['plane']:
        lut.number_of_table_values = 1

    lut1 = vtkLookupTable()
    color_series.BuildLookupTable(lut1, color_series.ORDINAL)
    lut1.nan_color = (0, 0, 0, 1)
    lut1.table_range = scalar_range

    number_of_bands = lut.number_of_table_values
    lut1.number_of_table_values = number_of_bands

    bands = get_bands(scalar_range, number_of_bands, precision, nearest_integer)
    if surface_name == 'parametric hills':
        # These are my custom bands.
        # Generated by first running:
        # bands = get_bands(scalar_range, number_of_bands, precision, False)
        # then:
        #  freq = get_frequencies(bands, source)
        #  print_bands_frequencies(bands, freq)
        # Finally using the output to create this table:
        my_bands = [
            [0, 1.0], [1.0, 2.0], [2.0, 3.0],
            [3.0, 4.0], [4.0, 5.0], [5.0, 6.0],
            [6.0, 7.0], [7.0, 8.0]]
        # Comment this out if you want to see how allocating
        # equally spaced bands works.
        bands = get_custom_bands(scalar_range, number_of_bands, my_bands)

    # Adjust the number of table values and scalar range.
    scalar_range = (bands[0][0], bands[len(bands) - 1][2])
    lut.table_range = scalar_range
    lut.number_of_table_values = len(bands)
    lut1.table_range = scalar_range
    lut1.number_of_table_values = len(bands)

    if frequency_table:
        print(f'{surface_name.title()} Elevation')
        # The number of scalars in each band.
        freq = get_frequencies(bands, source)
        bands, freq = adjust_ranges(bands, freq)
        print_bands_frequencies(bands, freq)

    # We will use the midpoint of the band as the label.
    labels = []
    for k in bands:
        labels.append('{:4.2f}'.format(bands[k][1]))

    # Annotate
    values = vtkVariantArray()
    for i in range(len(labels)):
        values.InsertNextValue(vtkVariant(labels[i]))
    for i in range(values.GetNumberOfTuples()):
        lut.SetAnnotation(i, values.GetValue(i).ToString())

    # Create the contour bands.
    # We will use an indexed lookup table.
    bcf = vtkBandedPolyDataContourFilter(input_data=source,
                                         scalar_mode=BandedPolyDataContourFilter.ScalarMode.VTK_SCALAR_MODE_INDEX,
                                         generate_contour_edges=True)
    # Use either the minimum or maximum value for each band.
    for i in range(len(bands)):
        bcf.SetValue(i, bands[i][2])

    glyphs = get_glyphs(source, scale_factor, reverse_normals=False)

    BandedGlyphs = namedtuple('BandedGlyphs',
                              ['glyph_type', 'glyphs', 'bcf',
                               'lut_max_bands', 'lut', 'lutr',
                               'lut1_max_bands', 'lut1', 'lut1r',
                               'scalar_range', 'labels'])
    bg = BandedGlyphs
    bg.glyph_type = 'Elevation'
    bg.glyphs = glyphs
    bg.bcf = bcf
    bg.lut_max_bands = max_lut_bands
    bg.lut = lut
    bg.lutr = reverse_lut(lut)
    bg.lut1_max_bands = max_lut_bands
    bg.lut1 = lut1
    bg.lut1r = reverse_lut(lut1)
    bg.scalar_range = scalar_range
    bg.labels = labels

    return bg


class ScalarBarProperties:
    """
    The properties needed for scalar bars.
    """

    lut = None
    # These are in pixels
    maximum_dimensions = {'width': 100, 'height': 260}
    title_text = '',
    number_of_labels: int = 5
    label_format = '{:0.2f}'
    # Orientation vertical=True, horizontal=False.
    orientation: bool = True
    # Horizontal and vertical positioning.
    # These are the default positions, don't change these.
    default_v = {'p': (0.85, 0.05), 'p2': (0.1, 0.7)}
    default_h = {'p': (0.125, 0.05), 'p2': (0.75, 0.1)}
    # Modify these as needed.
    position_v = copy.deepcopy(default_v)
    position_h = copy.deepcopy(default_h)


def make_scalar_bar_widget(scalar_bar_properties, title_text_property, label_text_property, renderer,
                           interactor):
    """
    Make a scalar bar widget.

    :param scalar_bar_properties: The lookup table, title name, maximum dimensions in pixels and position.
    :param title_text_property: The properties for the title.
    :param label_text_property: The properties for the labels.
    :param renderer: The default renderer.
    :param interactor: The vtkInteractor.
    :return: The scalar bar widget.
    """
    sb_actor = vtkScalarBarActor(lookup_table=scalar_bar_properties.lut, title=scalar_bar_properties.title_text,
                                 unconstrained_font_size=True,
                                 number_of_labels=scalar_bar_properties.number_of_labels,
                                 title_text_property=title_text_property, label_text_property=label_text_property,
                                 label_format=scalar_bar_properties.label_format,
                                 )

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

    widget = vtkScalarBarWidget(representation=sb_rep, scalar_bar_actor=sb_actor, default_renderer=renderer,
                                interactor=interactor, enabled=True)

    return widget


def position_sbw_h(num_bands, max_bands):
    """
    Position the vertical scalar bar widget.
    :param: num_bands - the number of bands in the scalar bar.
    :param: max_bands - the maximum number of bands.
    :return: The scalar bar position.
    """

    max_bands = abs(max_bands)
    num_bands = abs(num_bands)
    if num_bands > max_bands:
        num_bands = max_bands
    if num_bands == 0:
        num_bands = 1
    # Origin of the scalar bar.
    xy0 = [0.125, 0.05]
    # Width and height of the scalar bar.
    dxy = [0.75, 0.1]
    if num_bands >= max_bands:
        return {'p': tuple(xy0), 'p2': tuple(dxy)}

    dx = dxy[0] - xy0[0] * num_bands / max_bands
    dxy[0] = dxy[0] * num_bands / max_bands
    if num_bands == 1:
        xy0[0] = 0.5 - dx * num_bands / (max_bands * 2)
    else:
        xy0[0] = 0.5 - dx * (num_bands + 1) / (max_bands * 2)
    return {'p': tuple(xy0), 'p2': tuple(dxy)}


def position_sbw_v(num_bands, max_bands):
    """
    Position the vertical scalar bar widget.
    :param: num_bands - the number of bands in the scalar bar.
    :param: max_bands - the maximum number of bands.
    :return: The scalar bar position.
    """

    max_bands = abs(max_bands)
    num_bands = abs(num_bands)
    if num_bands > max_bands:
        num_bands = max_bands
    if num_bands == 0:
        num_bands = 1
    # Origin of the scalar bar.
    xy0 = [0.9, 0.25]
    # Width and height of the scalar bar.
    dxy = [0.08, 0.5]
    if num_bands >= max_bands:
        return {'p': tuple(xy0), 'p2': tuple(dxy)}

    dy = dxy[1] - xy0[1] * num_bands / max_bands
    dxy[1] = dxy[1] * num_bands / max_bands
    if num_bands == 1:
        xy0[1] = 0.5 - dy * num_bands / (max_bands * 2)
    else:
        xy0[1] = 0.5 - dy * (num_bands + 1) / (max_bands * 2)
    return {'p': tuple(xy0), 'p2': tuple(dxy)}


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


def print_bands_frequencies(bands, freq, precision=2):
    """
    Print each band and the number of scalars in each band.

    :param bands: The bands.
    :param freq: The frequencies.
    :param precision: The precision for the ranges in each band.
    """

    prec = abs(precision)
    if prec > 14:
        prec = 14

    if len(bands) != len(freq):
        print('Bands and Frequencies must be the same size.')
        return
    s = f'Bands & Frequencies:\n'
    total = 0
    width = prec + 6
    for k, v in bands.items():
        total += freq[k]
        for j, q in enumerate(v):
            if j == 0:
                s += f'{k:4d} ['
            if j == len(v) - 1:
                s += f'{q:{width}.{prec}f}]: {freq[k]:8d}\n'
            else:
                s += f'{q:{width}.{prec}f}, '
    width = 3 * width + 13
    s += f'{"Total":{width}s}{total:8d}\n'
    print(s)


def adjust_camera_parameters(surface_name, ren):
    """
    Adjust the camera parameters.

    :param surface_name: The name of the surface.
    :param ren: The surface renderer.

    """
    if surface_name == 'hills':
        camera = ren.active_camera
        camera.position = (18.6531, 19.2019, 0.192411)
        camera.focal_point = (0.916665, -0.0420811, -1.13654)
        camera.view_up = (-0.735704, 0.67718, 0.012917)
        camera.distance = 26.2045
        camera.clipping_range = (14.1162, 38.9096)
    elif surface_name == 'parametric hills':
        camera = ren.GetActiveCamera()
        camera.position = (7.68312, 50.6754, 37.3518)
        camera.focal_point = (2.09893, 7.79798, 7.36641)
        camera.view_up = (-0.0355891, 0.575838, -0.816789)
        camera.distance = 52.6192
        camera.clipping_range = (31.3381, 80.4166)
    elif surface_name == 'parametric torus':
        camera = ren.active_camera
        camera.position = (-1.38419, 24.2883, 34.9246)
        camera.focal_point = (-2.07248e-07, 3.63658e-06, 0.016056)
        camera.view_up = (0.010284, 0.821007, -0.570825)
        camera.distance = 42.5493
        camera.clipping_range = (25.2917, 64.5115)
    elif surface_name == 'plane':
        camera = ren.active_camera
        camera.position = (-0.516003, 22.5763, 51.9171)
        camera.focal_point = (-5.77108e-08, 0.500002, 5.80651e-06)
        camera.view_up = (-0.000956134, 0.920254, -0.391321)
        camera.distance = 56.4182
        camera.clipping_range = (36.7854, 81.268)
    elif surface_name == 'torus':
        camera = ren.active_camera
        camera.position = (-2.02659, 35.5605, 51.1256)
        camera.focal_point = (0, 0, 0.0160508)
        camera.view_up = (0.010284, 0.821007, -0.570825)
        camera.distance = 62.2964
        camera.clipping_range = (38.14, 92.8545)


@dataclass(frozen=True)
class BandedPolyDataContourFilter:
    @dataclass(frozen=True)
    class ScalarMode:
        VTK_SCALAR_MODE_INDEX: int = 0
        VTK_SCALAR_MODE_VALUE: int = 1


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
class Curvatures:
    @dataclass(frozen=True)
    class CurvatureType:
        VTK_CURVATURE_GAUSS: int = 0
        VTK_CURVATURE_MEAN: int = 1
        VTK_CURVATURE_MAXIMUM: int = 2
        VTK_CURVATURE_MINIMUM: int = 3


@dataclass(frozen=True)
class Glyph3D:
    @dataclass(frozen=True)
    class ColorMode:
        VTK_COLOR_BY_SCALE: int = 0
        VTK_COLOR_BY_SCALAR: int = 1
        VTK_COLOR_BY_VECTOR: int = 2

    @dataclass(frozen=True)
    class IndexMode:
        VTK_INDEXING_OFF: int = 0
        VTK_INDEXING_BY_SCALAR: int = 1
        VTK_INDEXING_BY_VECTOR: int = 2

    @dataclass(frozen=True)
    class ScaleMode:
        VTK_SCALE_BY_SCALAR: int = 0
        VTK_SCALE_BY_VECTOR: int = 1
        VTK_SCALE_BY_VECTORCOMPONENTS: int = 2
        VTK_DATA_SCALING_OFF: int = 3

    @dataclass(frozen=True)
    class VectorMode:
        VTK_USE_VECTOR: int = 0
        VTK_USE_NORMAL: int = 1
        VTK_VECTOR_ROTATION_OFF: int = 2
        VTK_FOLLOW_CAMERA_DIRECTION: int = 3

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
    import sys

    main(sys.argv)