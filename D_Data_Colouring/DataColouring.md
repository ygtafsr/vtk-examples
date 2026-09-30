
### Resources:

https://vtk.org/doc/nightly/html/classvtkLookupTable.html

https://vtk.org/doc/nightly/html/classvtkLogLookupTable.html

https://vtk.org/doc/nightly/html/classvtkColorTransferFunction.html

https://vtk.org/doc/nightly/html/classvtkDiscretizableColorTransferFunction.html

https://vtk.org/doc/nightly/html/classvtkColorSeries.html

https://vtk.org/doc/nightly/html/classvtkScalarBarActor.html


# Colour Mapping Concepts
------------------------

| Class                      | Think of it as                 | Mapping                      |
| -------------------------- | ------------------------------ | ---------------------------- |
| `vtkColorSeries`           | **Palette**                    | predefined colours           |
| `vtkLookupTable`           | **Colour table**               | scalar → table colour        |
| `vtkColorTransferFunction` | **Continuous colour function** | scalar → interpolated colour |
| `vtkScalarBarActor`        | **Legend**                     | displays the mapping         |


## 1) vtkLookupTable

vtkLookupTable is 1D tabular array used colour mapping.  
Scalar values are converted (mapped) into colours through its lookup table:

    Scalar        Colour
    ──────────────────────
    0             Blue
    100           Cyan
    200           Green
    300           Yellow
    400           Red


lut = vtkLookupTable(  
    number_of_table_values=5,  
    range=(0.0, 500.0),  
)  

lut.SetTableValue(0, 0.0, 0.0, 1.0, 1.0)  
lut.SetTableValue(1, 0.0, 1.0, 1.0, 1.0)  
lut.SetTableValue(2, 0.0, 1.0, 0.0, 1.0)  
lut.SetTableValue(3, 1.0, 1.0, 0.0, 1.0)  
lut.SetTableValue(4, 1.0, 0.0, 0.0, 1.0)  

> The lookup table has a minimum and maximum scalar range; values outside that range are clamped to the end colours.


    PointData
        │
        │ scalar = 300 MPa
        ▼
    vtkDataSetMapper (Maps a scalar range [100, 500] to normalised range [0, 1])
        │
        │ scalar_range = (100, 500)
        ▼
    normalised scalar
        │
        │ 300 → 0.5
        ▼
    vtkLookupTable
        │
        │ index ≈ 128
        ▼
    RGB colour
        │
        ▼
      Actor

There are therefore two steps:

- mapper.scalar_range determines how the scalar value is normalised.
- The lookup table determines what colour corresponds to that normalised position.

> We can create a lookup table directly or through vtkColorSeries object.

## 2) vtkColorSeries

Provides predefined palette of colours.

    vtkColorSeries
        │
        │ palette
        ▼
    vtkLookupTable
        │
        │ scalar → colour
        ▼
    vtkDataSetMapper

from vtkmodules.vtkCommonColor import vtkColorSeries  
colors = vtkColorSeries()  
lut = colors.CreateLookupTable()  

#### PointData

Suppose:
node 0 → 100 MPa
node 1 → 200 MPa
node 2 → 300 MPa
node 3 → 400 MPa

VTK can interpolate these values across the element. (via element shape functions)
For a 4-node quad: σ(ξ,η)=N1​σ1​+N2​σ2​+N3​σ3​+N4​σ4​
This is why point-data colouring produces smooth gradients.

### Contouring (vtkContourFilter)
------------------------

We solve for locations satisfying: σ(r,s) = C
and construct geometry from those locations.

contour ≠ threshold
Contour finds : σ=300
Treshold finds : σ>300

### Colour Legends and Scalar Bars

from vtkmodules.vtkRenderingAnnotation import vtkScalarBarActor

Pipeline:

            UnstructuredGrid
                │
                ▼
            vtkDataSetMapper
                │
                │ lookup table
                ▼
            vtkActor
                │
                ▼
            Renderer

The scalar bar is associated with the same lookup table:
> The scalar bar should use the same LUT

            ┌──────────────────┐
            │ vtkLookupTable    │
            └────────┬─────────┘
                    │
            ┌────────┴─────────┐
            │                  │
            ▼                  ▼
    vtkDataSetMapper    vtkScalarBarActor
            │                  │
            ▼                  ▼
        vtkActor          colour legend

--------------------------------

For your FEA implementation, I would learn these in this order:



Isolines vs isosurfaces

Thresholding: vtkThreshold
Clipping: vtkClipDataSet



The next particularly important topic is how VTK interpolates PointData between FEA nodes, because that explains why a VTK contour plot looks the way it does and connects directly to the finite-element shape functions you already know.