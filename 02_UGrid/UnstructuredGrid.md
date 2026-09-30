

A vtkUnstructuredGrid contains a mesh structure, and arrays of data can be attached to either its points or its cells.  

The VTK Book describes a dataset as having geometry + topology + attribute data. Geometry comes from point coordinates; topology comes from cells and their connectivity; attributes are additional values associated with points or cells.


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

