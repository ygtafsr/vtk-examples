from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

import vtk
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtWidgets import QRubberBand
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

SelectionMode = Literal["element", "node", "surface"]


@dataclass
class SelectionState:
    mode: SelectionMode = "element"
    selected_elements: set[int] = field(default_factory=set)
    selected_nodes: set[int] = field(default_factory=set)
    selected_surfaces: set[int] = field(default_factory=set)
    hidden_elements: set[int] = field(default_factory=set)
    hidden_nodes: set[int] = field(default_factory=set)
    hidden_surfaces: set[int] = field(default_factory=set)


class SolidWorksInteractorStyle(vtk.vtkInteractorStyleTrackballCamera):
    """VTK camera controls with CAD-style shortcuts and pick routing."""

    def __init__(self, viewer: "VtkGridViewer"):
        super().__init__()
        self.viewer = viewer
        self._middle_mode: str | None = None
        self.AddObserver("KeyPressEvent", self._on_key_press)
        self.AddObserver("MiddleButtonPressEvent", self._on_middle_button)
        self.AddObserver("MiddleButtonReleaseEvent", self._on_middle_release)
        self.AddObserver("RightButtonPressEvent", self._on_right_button)
        self.AddObserver("RightButtonReleaseEvent", self._on_right_release)

    def _on_key_press(self, _obj, _event) -> None:
        key = (self.GetInteractor().GetKeySym() or "").lower()
        shift = bool(self.GetInteractor().GetShiftKey())
        ctrl = bool(self.GetInteractor().GetControlKey())

        if key == "e":
            self.viewer.set_selection_mode("element")
        elif key == "n":
            self.viewer.set_selection_mode("node")
        elif key == "s":
            self.viewer.set_selection_mode("surface")
        elif key in {"h", "delete"}:
            if ctrl and shift:
                self.viewer.show_all_active()
            elif ctrl:
                self.viewer.hide_all_active()
            elif shift:
                self.viewer.show_selected_active()
            else:
                self.viewer.hide_selected_active()
        elif key == "escape":
            self.viewer.clear_selection()
        elif key in {"f", "home"}:
            self.viewer.reset_camera()
        else:
            self.OnKeyPress()

    def _on_middle_button(self, _obj, _event) -> None:
        if self.GetInteractor().GetShiftKey():
            self._middle_mode = "pan"
            self.OnMiddleButtonDown()
        else:
            self._middle_mode = "rotate"
            self.OnLeftButtonDown()

    def _on_middle_release(self, _obj, _event) -> None:
        if self._middle_mode == "rotate":
            self.OnLeftButtonUp()
        else:
            self.OnMiddleButtonUp()
        self._middle_mode = None

    def _on_right_button(self, _obj, _event) -> None:
        self.OnRightButtonDown()

    def _on_right_release(self, _obj, _event) -> None:
        self.OnRightButtonUp()

class VtkGridViewer(QVTKRenderWindowInteractor):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.renderer = vtk.vtkRenderer()
        self.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor_style = SolidWorksInteractorStyle(self)
        self.GetRenderWindow().GetInteractor().SetInteractorStyle(self.interactor_style)

        self.grid: vtk.vtkUnstructuredGrid | None = None
        self.surface_grid: vtk.vtkPolyData | None = None
        self.visible_element_ids: list[int] = []
        self.visible_node_ids: list[int] = []
        self.visible_surface_ids: list[int] = []
        self.state = SelectionState()
        self.on_status_changed: Callable[[str], None] | None = None
        self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self._rubber_band.setStyleSheet(
            "QRubberBand { "
            "background-color: rgba(255, 210, 35, 55); "
            "border: 2px dashed rgba(190, 130, 0, 230); "
            "}"
        )
        self._rubber_origin = QPoint()
        self._is_rect_selecting = False

        self.element_actor = _make_actor((0.74, 0.78, 0.82), opacity=1.0)
        self.edge_actor = _make_actor((0.08, 0.10, 0.12), opacity=1.0)
        self.node_actor = _make_actor((0.05, 0.28, 0.60), opacity=1.0)
        self.surface_actor = _make_actor((0.14, 0.58, 0.42), opacity=0.22)
        self.selected_element_actor = _make_actor((1.0, 0.86, 0.05), opacity=1.0)
        self.selected_node_actor = _make_actor((1.0, 0.92, 0.10), opacity=1.0)
        self.selected_surface_actor = _make_actor((1.0, 0.88, 0.12), opacity=0.90)

        self.surface_actor.GetProperty().SetRepresentationToSurface()
        self.edge_actor.GetProperty().SetRepresentationToWireframe()
        self.edge_actor.GetProperty().SetLineWidth(1.0)
        self.selected_element_actor.GetProperty().SetEdgeVisibility(True)
        self.selected_element_actor.GetProperty().SetEdgeColor(0.22, 0.17, 0.02)
        self.selected_element_actor.GetProperty().SetLineWidth(2.0)
        self.selected_element_actor.GetProperty().SetPointSize(9.0)
        self.selected_element_actor.GetProperty().SetSpecular(0.2)
        self.selected_element_actor.GetProperty().SetSpecularPower(10.0)
        self.selected_node_actor.GetProperty().SetSpecular(0.25)
        self.selected_node_actor.GetProperty().SetSpecularPower(12.0)
        self.selected_surface_actor.GetProperty().SetLineWidth(2.0)
        self.selected_surface_actor.GetProperty().SetEdgeVisibility(True)
        self.selected_surface_actor.GetProperty().SetEdgeColor(0.35, 0.26, 0.02)

        for actor in (
            self.element_actor,
            self.edge_actor,
            self.surface_actor,
            self.node_actor,
            self.selected_element_actor,
            self.selected_node_actor,
            self.selected_surface_actor,
        ):
            self.renderer.AddActor(actor)

        self.element_picker = vtk.vtkCellPicker()
        self.element_picker.SetTolerance(0.0008)
        self.surface_picker = vtk.vtkCellPicker()
        self.surface_picker.SetTolerance(0.0008)
        self.node_picker = vtk.vtkPointPicker()
        self.node_picker.SetTolerance(0.02)

        self.renderer.SetBackground(0.98, 0.985, 0.99)
        self._set_status("Open an Ansys .rst file to begin.")

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.grid is not None:
            self._is_rect_selecting = True
            self._rubber_origin = event.position().toPoint()
            self._rubber_band.setGeometry(QRect(self._rubber_origin, self._rubber_origin))
            self._rubber_band.show()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._is_rect_selecting:
            current = event.position().toPoint()
            self._rubber_band.setGeometry(QRect(self._rubber_origin, current).normalized())
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self._is_rect_selecting:
            self._is_rect_selecting = False
            rectangle = self._rubber_band.geometry()
            self._rubber_band.hide()
            self.select_in_rectangle(
                rectangle,
                append=bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier),
                toggle=bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier),
            )
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def set_grid(self, grid: vtk.vtkUnstructuredGrid) -> None:
        self.grid = grid
        self.state = SelectionState()
        self.surface_grid = _extract_surface(grid)
        self._update_all_pipelines()
        self.reset_camera()
        self._set_status(
            f"Loaded {grid.GetNumberOfPoints():,} nodes and {grid.GetNumberOfCells():,} elements."
        )

    def set_selection_mode(self, mode: SelectionMode) -> None:
        self.state.mode = mode
        self._set_status(f"Selection mode: {mode}.")

    def select_in_rectangle(self, rectangle: QRect, append: bool = False, toggle: bool = False) -> None:
        if self.grid is None:
            return
        if rectangle.width() < 2 or rectangle.height() < 2:
            rectangle = rectangle.adjusted(-4, -4, 4, 4)

        if self.state.mode == "node":
            found = self._nodes_in_rectangle(rectangle)
            self._apply_rect_selection(self.state.selected_nodes, found, append, toggle)
            self._update_selected_nodes()
        elif self.state.mode == "surface":
            found = self._cells_in_rectangle(self.surface_grid, self.visible_surface_ids, rectangle)
            self._apply_rect_selection(self.state.selected_surfaces, found, append, toggle)
            self._update_selected_surfaces()
        else:
            found = self._cells_in_rectangle(self.grid, self.visible_element_ids, rectangle)
            self._apply_rect_selection(self.state.selected_elements, found, append, toggle)
            self._update_selected_elements()

        self._set_status(self._selection_summary())
        self.Render()

    def _nodes_in_rectangle(self, rectangle: QRect) -> set[int]:
        selected = set()
        for point_id in self.visible_node_ids:
            if self._world_point_in_rectangle(self.grid.GetPoint(point_id), rectangle):
                selected.add(point_id)
        return selected

    def _cells_in_rectangle(self, dataset, visible_ids: list[int], rectangle: QRect) -> set[int]:
        selected = set()
        if dataset is None:
            return selected
        for cell_id in visible_ids:
            center = _cell_center(dataset, cell_id)
            if self._world_point_in_rectangle(center, rectangle):
                selected.add(cell_id)
        return selected

    def _world_point_in_rectangle(self, point: tuple[float, float, float], rectangle: QRect) -> bool:
        display_x, display_y = self._world_to_qt_display(point)
        return rectangle.contains(QPoint(round(display_x), round(display_y)))

    def _world_to_qt_display(self, point: tuple[float, float, float]) -> tuple[float, float]:
        self.renderer.SetWorldPoint(point[0], point[1], point[2], 1.0)
        self.renderer.WorldToDisplay()
        display_x, display_y, _display_z = self.renderer.GetDisplayPoint()
        render_width, render_height = self.GetRenderWindow().GetSize()
        widget_width = max(self.width(), 1)
        widget_height = max(self.height(), 1)
        qt_x = display_x * widget_width / max(render_width, 1)
        qt_y = widget_height - (display_y * widget_height / max(render_height, 1))
        return qt_x, qt_y

    def _apply_rect_selection(
        self,
        selected: set[int],
        found: set[int],
        append: bool,
        toggle: bool,
    ) -> None:
        if toggle:
            for item_id in found:
                self._toggle_id(selected, item_id)
            return

        if append:
            selected.update(found)
            return

        selected.clear()
        selected.update(found)

    def hide_selected_active(self) -> None:
        if self.state.mode == "element":
            self.state.hidden_elements.update(self.state.selected_elements)
            self.state.selected_elements.clear()
        elif self.state.mode == "node":
            self.state.hidden_nodes.update(self.state.selected_nodes)
            self.state.selected_nodes.clear()
        else:
            self.state.hidden_surfaces.update(self.state.selected_surfaces)
            self.state.selected_surfaces.clear()
        self._update_all_pipelines()

    def show_selected_active(self) -> None:
        if self.state.mode == "element":
            self.state.hidden_elements.difference_update(self.state.selected_elements)
        elif self.state.mode == "node":
            self.state.hidden_nodes.difference_update(self.state.selected_nodes)
        else:
            self.state.hidden_surfaces.difference_update(self.state.selected_surfaces)
        self._update_all_pipelines()

    def hide_all_active(self) -> None:
        if self.grid is None:
            return
        if self.state.mode == "element":
            self.state.hidden_elements = set(range(self.grid.GetNumberOfCells()))
        elif self.state.mode == "node":
            self.state.hidden_nodes = set(range(self.grid.GetNumberOfPoints()))
        elif self.surface_grid is not None:
            self.state.hidden_surfaces = set(range(self.surface_grid.GetNumberOfCells()))
        self._update_all_pipelines()

    def show_all_active(self) -> None:
        if self.state.mode == "element":
            self.state.hidden_elements.clear()
        elif self.state.mode == "node":
            self.state.hidden_nodes.clear()
        else:
            self.state.hidden_surfaces.clear()
        self._update_all_pipelines()

    def clear_selection(self) -> None:
        self.state.selected_elements.clear()
        self.state.selected_nodes.clear()
        self.state.selected_surfaces.clear()
        self._update_selected_elements()
        self._update_selected_nodes()
        self._update_selected_surfaces()
        self._set_status("Selection cleared.")
        self.Render()

    def reset_camera(self) -> None:
        self.renderer.ResetCamera()
        self.Render()

    def _update_all_pipelines(self) -> None:
        self._update_elements()
        self._update_nodes()
        self._update_surfaces()
        self._update_selected_elements()
        self._update_selected_nodes()
        self._update_selected_surfaces()
        self._set_status(self._visibility_summary())
        self.Render()

    def _update_elements(self) -> None:
        visible_grid, self.visible_element_ids = _extract_visible_cells(
            self.grid, self.state.hidden_elements
        )
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputData(visible_grid)
        self.element_actor.SetMapper(mapper)
        self.edge_actor.SetMapper(mapper)
        self.element_picker.InitializePickList()
        self.element_picker.AddPickList(self.element_actor)
        self.element_picker.PickFromListOn()

    def _update_nodes(self) -> None:
        point_poly, self.visible_node_ids = _visible_points_polydata(
            self.grid, self.state.hidden_nodes
        )
        glyph = vtk.vtkGlyph3DMapper()
        source = vtk.vtkSphereSource()
        source.SetRadius(_model_radius(self.grid) * 0.006)
        source.SetThetaResolution(10)
        source.SetPhiResolution(10)
        glyph.SetInputData(point_poly)
        glyph.SetSourceConnection(source.GetOutputPort())
        glyph.ScalingOff()
        self.node_actor.SetMapper(glyph)
        self.node_picker.InitializePickList()
        self.node_picker.AddPickList(self.node_actor)
        self.node_picker.PickFromListOn()

    def _update_surfaces(self) -> None:
        visible_surface, self.visible_surface_ids = _extract_visible_cells(
            self.surface_grid, self.state.hidden_surfaces
        )
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(visible_surface)
        self.surface_actor.SetMapper(mapper)
        self.surface_picker.InitializePickList()
        self.surface_picker.AddPickList(self.surface_actor)
        self.surface_picker.PickFromListOn()

    def _update_selected_elements(self) -> None:
        selected = self.state.selected_elements - self.state.hidden_elements
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(_surface_from_cells(self.grid, selected))
        self.selected_element_actor.SetMapper(mapper)

    def _update_selected_nodes(self) -> None:
        selected = self.state.selected_nodes - self.state.hidden_nodes
        point_poly = _points_polydata(self.grid, selected)
        source = vtk.vtkSphereSource()
        source.SetRadius(_model_radius(self.grid) * 0.011)
        source.SetThetaResolution(16)
        source.SetPhiResolution(16)
        glyph = vtk.vtkGlyph3DMapper()
        glyph.SetInputData(point_poly)
        glyph.SetSourceConnection(source.GetOutputPort())
        glyph.ScalingOff()
        self.selected_node_actor.SetMapper(glyph)

    def _update_selected_surfaces(self) -> None:
        selected = self.state.selected_surfaces - self.state.hidden_surfaces
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(_extract_only_cells(self.surface_grid, selected))
        self.selected_surface_actor.SetMapper(mapper)

    def _toggle_id(self, selected: set[int], item_id: int) -> None:
        if item_id in selected:
            selected.remove(item_id)
        else:
            selected.add(item_id)

    def _selection_summary(self) -> str:
        return (
            f"Selected: {len(self.state.selected_elements)} elements, "
            f"{len(self.state.selected_nodes)} nodes, "
            f"{len(self.state.selected_surfaces)} surfaces."
        )

    def _visibility_summary(self) -> str:
        return (
            f"Hidden: {len(self.state.hidden_elements)} elements, "
            f"{len(self.state.hidden_nodes)} nodes, "
            f"{len(self.state.hidden_surfaces)} surfaces."
        )

    def _set_status(self, message: str) -> None:
        if self.on_status_changed:
            self.on_status_changed(message)


def _make_actor(color: tuple[float, float, float], opacity: float) -> vtk.vtkActor:
    actor = vtk.vtkActor()
    actor.GetProperty().SetColor(*color)
    actor.GetProperty().SetOpacity(opacity)
    return actor


def _extract_surface(grid: vtk.vtkUnstructuredGrid) -> vtk.vtkPolyData:
    solid_grid = _extract_dimension_cells(grid, dimension=3)
    surface = vtk.vtkDataSetSurfaceFilter()
    surface.SetInputData(solid_grid)
    surface.Update()
    output = vtk.vtkPolyData()
    output.ShallowCopy(surface.GetOutput())
    return output


def _surface_from_cells(grid: vtk.vtkUnstructuredGrid | None, cell_ids: set[int]) -> vtk.vtkPolyData:
    if grid is None or not cell_ids:
        return vtk.vtkPolyData()

    append = vtk.vtkAppendPolyData()
    solid_ids = {
        cell_id
        for cell_id in cell_ids
        if 0 <= cell_id < grid.GetNumberOfCells()
        and grid.GetCell(cell_id).GetCellDimension() == 3
    }
    lower_dimension_ids = cell_ids - solid_ids

    if solid_ids:
        selected_grid = _extract_only_cells(grid, solid_ids)
        surface = vtk.vtkDataSetSurfaceFilter()
        surface.SetInputData(selected_grid)
        surface.Update()
        append.AddInputData(surface.GetOutput())

    if lower_dimension_ids:
        append.AddInputData(_cells_to_polydata(grid, lower_dimension_ids))

    append.Update()
    output = vtk.vtkPolyData()
    output.ShallowCopy(append.GetOutput())
    return output


def _cells_to_polydata(dataset, cell_ids: set[int]) -> vtk.vtkPolyData:
    output = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    polys = vtk.vtkCellArray()
    lines = vtk.vtkCellArray()
    verts = vtk.vtkCellArray()
    point_map: dict[int, int] = {}

    for cell_id in sorted(cell_ids):
        if not 0 <= cell_id < dataset.GetNumberOfCells():
            continue
        cell = dataset.GetCell(cell_id)
        original_ids = cell.GetPointIds()
        new_ids = vtk.vtkIdList()
        for idx in range(original_ids.GetNumberOfIds()):
            original_id = original_ids.GetId(idx)
            if original_id not in point_map:
                point_map[original_id] = points.InsertNextPoint(dataset.GetPoint(original_id))
            new_ids.InsertNextId(point_map[original_id])

        dimension = cell.GetCellDimension()
        if dimension == 2:
            polys.InsertNextCell(new_ids)
        elif dimension == 1:
            lines.InsertNextCell(new_ids)
        else:
            verts.InsertNextCell(new_ids)

    output.SetPoints(points)
    output.SetPolys(polys)
    output.SetLines(lines)
    output.SetVerts(verts)
    return output


def _extract_visible_cells(dataset, hidden_ids: set[int]):
    if dataset is None:
        return vtk.vtkUnstructuredGrid(), []
    all_ids = set(range(dataset.GetNumberOfCells()))
    visible_ids = sorted(all_ids - hidden_ids)
    return _extract_only_cells(dataset, set(visible_ids)), visible_ids


def _extract_only_cells(dataset, cell_ids: set[int]):
    if dataset is None:
        return vtk.vtkUnstructuredGrid()

    if isinstance(dataset, vtk.vtkPolyData):
        return _extract_only_polydata_cells(dataset, cell_ids)

    ids = vtk.vtkIdList()
    for cell_id in sorted(cell_ids):
        if 0 <= cell_id < dataset.GetNumberOfCells():
            ids.InsertNextId(cell_id)

    extract = vtk.vtkExtractCells()
    extract.SetInputData(dataset)
    extract.SetCellList(ids)
    extract.Update()

    output = vtk.vtkUnstructuredGrid()
    output.ShallowCopy(extract.GetOutput())
    return output


def _extract_dimension_cells(grid: vtk.vtkUnstructuredGrid, dimension: int) -> vtk.vtkUnstructuredGrid:
    ids = vtk.vtkIdList()
    for cell_id in range(grid.GetNumberOfCells()):
        if grid.GetCell(cell_id).GetCellDimension() == dimension:
            ids.InsertNextId(cell_id)

    extract = vtk.vtkExtractCells()
    extract.SetInputData(grid)
    extract.SetCellList(ids)
    extract.Update()

    output = vtk.vtkUnstructuredGrid()
    output.ShallowCopy(extract.GetOutput())
    return output


def _extract_only_polydata_cells(polydata: vtk.vtkPolyData, cell_ids: set[int]) -> vtk.vtkPolyData:
    return _cells_to_polydata(polydata, cell_ids)


def _visible_points_polydata(grid: vtk.vtkUnstructuredGrid | None, hidden_ids: set[int]) -> vtk.vtkPolyData:
    if grid is None:
        return vtk.vtkPolyData(), []
    point_ids = sorted(set(range(grid.GetNumberOfPoints())) - hidden_ids)
    return _points_polydata(grid, set(point_ids)), point_ids


def _points_polydata(grid: vtk.vtkUnstructuredGrid | None, point_ids: set[int]) -> vtk.vtkPolyData:
    poly = vtk.vtkPolyData()
    points = vtk.vtkPoints()
    verts = vtk.vtkCellArray()
    if grid is None:
        return poly

    for point_id in sorted(point_ids):
        if 0 <= point_id < grid.GetNumberOfPoints():
            new_id = points.InsertNextPoint(grid.GetPoint(point_id))
            verts.InsertNextCell(1)
            verts.InsertCellPoint(new_id)

    poly.SetPoints(points)
    poly.SetVerts(verts)
    return poly


def _cell_center(dataset, cell_id: int) -> tuple[float, float, float]:
    cell = dataset.GetCell(cell_id)
    point_ids = cell.GetPointIds()
    count = point_ids.GetNumberOfIds()
    if count == 0:
        return 0.0, 0.0, 0.0

    x_sum = 0.0
    y_sum = 0.0
    z_sum = 0.0
    for idx in range(count):
        x, y, z = dataset.GetPoint(point_ids.GetId(idx))
        x_sum += x
        y_sum += y
        z_sum += z

    return x_sum / count, y_sum / count, z_sum / count


def _model_radius(grid: vtk.vtkUnstructuredGrid | None) -> float:
    if grid is None or grid.GetNumberOfPoints() == 0:
        return 1.0
    bounds = grid.GetBounds()
    dx = bounds[1] - bounds[0]
    dy = bounds[3] - bounds[2]
    dz = bounds[5] - bounds[4]
    return max((dx * dx + dy * dy + dz * dz) ** 0.5, 1.0)
