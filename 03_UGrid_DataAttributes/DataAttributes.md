
https://vtk.org/doc/nightly/html/classvtkDataSetAttributes.html


- A vtkUnstructuredGrid contains a mesh structure, and arrays of data
 can be attached to either its points or its cells.

> The VTK Book describes a **dataset** as having **geometry + topology + attribute data**.  
Geometry comes from point coordinates; topology comes from cells and their connectivity;  
attributes are additional values associated with points or cells.

                    vtkUnstructuredGrid
                            │
            ┌──────────────┴──────────────┐
            │                             │
        STRUCTURE                    ATTRIBUTE DATA
            │                             │
        ┌────┴────┐                 ┌──────┼──────┐
        │         │                 │      │      │
    Geometry  Topology         PointData CellData FieldData
        │         │
    Points     Cells
        │         │
    node xyz   connectivity


                         vtkDataSet
                            │
             ┌──────────────┼──────────────┐
             │              │              │
          Points           Cells        FieldData
             │              │              │
             │              │              │
        vtkPointData    vtkCellData        │
             │              │              │
             └──────┬───────┘              │
                    │                      │
             vtkDataSetAttributes          │
                    │                      │
             ┌──────┼───────┐              │
             │      │       │              │
          Arrays  Scalars Vectors       Arrays
                    │
             "active" attributes


## DataSetAttributes

- vtkDataSetAttributes is a container that stores data arrays and gives those arrays semantic roles such as Scalars, Vectors, Normals, and Tensors

- PointData and CellData are specialised versions of this container.  

- vtkPointData and vtkCellData are specialised vtkDataSetAttributes containers. vtkDataSetAttributes manages arrays associated with dataset entities and can assign semantic roles to those arrays.


### Point Data
Point data = data where there is one value/tuple for every point.

Point data can be scalar, vector, tensor, etc.

Suppose your FEA model has 8 nodes. We calculate nodal displacement:

    Node       Ux       Uy       Uz  
    --------------------------------  
    0         0.00     0.00     0.00  
    1         0.10     0.02     0.00  
    2         0.15     0.04     0.01  
    ...  

> point coordinates specify the position of the dataset, whereas attributes are supplemental information such as temperature or mass.

> Number of Points and data size should match. Less or more data causes wrong assignment!


### Cell Data

### Field Data

- There is a broader container called **vtkFieldData** which can store arrays that are **not associated specifically with points or cells.**

### Default Attribute Categories

- vtkDataSetAttributes does more than simply store arbitrary arrays. It knows that some arrays have a particular semantic role.

- For example, VTK can distinguish between:

"Temperature"      → Scalars
"Displacement"     → Vectors
"SurfaceNormal"    → Normals
"Stress"           → Tensors  

If "Temperature" is designated as the active scalars, VTK understands:  
"This array represents the scalar field that should be considered the dataset's scalar attribute."  

- This is particularly important for colour mapping.  
- For example:  

        Temperature
            ↓
        scalar field
            ↓
        mapper
            ↓
        colour map
            ↓
        mesh coloured by temperature

- For examaple Vector Attributes tells VTK:  

"These 3-component values represent vectors."

This becomes useful for things such as:

displacement arrows
velocity glyphs
vector visualization
vector-based filters

- Normals:  

Normals are also vectors, but they have a specific geometric meaning:  
A normal is a vector perpendicular to a surface.  

grid.point_data["Normals"]

--------------------------------------------

> Your FEA model should probably have several IDs:

    PointData
    │
    ├── NodeId
    ├── Displacement
    ├── ReactionForce
    └── Temperature


    CellData
    │
    ├── ElementId
    ├── ComponentId
    ├── MaterialId
    ├── SectionId
    ├── ElementType
    ├── PartId
    ├── ElementSetId
    └── Stress


grid.cell_data["ElementId"] = element_ids
grid.cell_data["ComponentId"] = component_ids
grid.cell_data["MaterialId"] = material_ids
grid.cell_data["SectionId"] = section_ids

You can subsequently ask:

Show component 15
Show material 3
Hide component 8
Show elements in set "CONTACT_SURFACE"
Color by stress
Color by material
Select element 10523
Select component 7

- Seperate Actors for Components:

                    vtkUnstructuredGrid
                           │
             ┌─────────────┼─────────────┐
             │             │             │
         Component 1   Component 2   Component 3
             │             │             │
           Mapper        Mapper        Mapper
             │             │             │
           Actor         Actor         Actor

This is useful when components need independent visualization properties:  

    Component 1 → visible
    Component 2 → hidden
    Component 3 → transparent  


    actor_1.property.opacity = 1.0
    actor_2.property.opacity = 0.3
    actor_3.VisibilityOff()
