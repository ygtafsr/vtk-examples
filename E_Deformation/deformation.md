
### References:

https://vtk.org/doc/nightly/html/classvtkWarpVector.html
https://examples.vtk.org/site/PythonicAPI/VisualizationAlgorithms/DisplacementPlot/
https://examples.vtk.org/site/Cxx/VisualizationAlgorithms/PlateVibration/

### Standard VTK Deformation Model

X_def = X_0 + S*U

X_def = Displayed deformed coordinates
X_0 = original nodal coordinates
U = (Ux, Uy, Uz) = Displacement vector at each node
S = visualization scale factor

### VTK Deformed Geoemetry Pipeline

    Original FEA mesh
        │
        │ PointData: displacement vectors
        ▼
    vtkWarpVector
        │
        │ deformed geometry
        ▼
    vtkDataSetMapper
        │
        ▼
    vtkActor
        │
        ▼
    Renderer

### vtkWarpVector

from vtkmodules.vtkFiltersGeneral import vtkWarpVector

The displacement does not normally replace your mesh coordinates.
Instead, vtkWarpVector creates an output dataset whose points have been moved according to the displacement vectors.

### Implementation Notes

1) Store displacement Vectors as PointData
2) Make the displacement the active vector field
3) Apply vtkWarpVector
4) Connect the mapper to the warped mesh



