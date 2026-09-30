
### References:


### What is Glyphs?

A glyph is a graphical object that is placed at data locations and whose shape, orientation, size, or color is controlled by the data.

In VTK, glyphs are particularly useful for visualizing vectors, normals, directions, scalar values, and other point-associated data.

### Standard VTK Vector Visualization Model

For vector visualization, think about three separate operations:
1) Translation: Where should the glyph go? point coordinates -> glyph position
2) Orientation: Which direction should it point?
    v=(vx​,vy​,vz​)
    the glyph can be oriented along:
    [v] = v/∥v∥
3) Scaling: s=C∥v∥, C is a Scale Factor

### VTK vtkGlyph3D Pipeline

                            Glyph source
                            vtkPolyData
                                │
                                │
                                ▼
                            ┌─────────┐
    Input dataset ─────────►│         │
    (points + attributes)   │vtkGlyph3D│
                            │         │
                            └────┬────┘
                                 │
                                 ▼
                          glyph geometry
                                 │
                                 ▼
                         vtkPolyDataMapper
                                 │
                                 ▼
                              vtkActor


### vtkGlyph3D

The VTK textbook explicitly describes this as a filter with two inputs:
1) Input — points and their attributes
2) Source — the geometry to copy onto those points

1) The input contains:
    Point coordinates
        +
    PointData
        +
    Vectors
        +
    Scalars
        +
    Normals

2) The source is simply the shape that will be copied.
    cone = vtkConeSource()
    sphere = vtkSphereSource()
    arrow = vtkArrowSource()

    Input                         Source

    points + vectors              cone
        │                         │
        │                         │
        └────────┐     ┌──────────┘
                 ▼     ▼
                vtkGlyph3D
                    │
                    ▼
        many transformed cones

> A glyph is not necessarily an arrow.

You could use:
Sphere       → point marker
Cone         → direction
Arrow        → vector
Cube         → categorical marker
Cylinder     → directional quantity
Axes         → tensor/principal directions
Custom mesh  → engineering symbol