

## Post-Processing Filters

In VTK, probing, thresholding, and extraction are three closely related operations for scientific/FEA post-processing:

- **Probing** → What is the result at this location?
- **Thresholding** → Where is the result above/below a criterion?
- **Extraction** → Give me the actual subset of the model/results that I selected.  

        "Give me stress at x = (12.4, 3.2, 1.0)"
                            ↓
                        PROBE

        "Show me regions where stress > 400 MPa"
                            ↓
                        THRESHOLD

        "Give me the actual elements belonging
        to that >400 MPa region"
                            ↓
                        EXTRACT

## Probing :: vtkProbeFilter, vtkResampleWithDataSet

**vtkProbeFilter:**

> from vtkmodules.vtkFiltersCore import vtkProbeFilter

This filter has two conceptual inputs:

probe = vtkProbeFilter( input_data=probe_geometry, source_data=fea_grid)
probe.update()  
result = probe.output

* The output retains the probe geometry, while data from the source are transferred/interpolated onto its points.

**vtkResampleWithDataSet:**

> from vtkmodules.vtkFiltersCore import vtkResampleWithDataSet

resample = vtkResampleWithDataSet(  input_data=probe_surface, source_data=fea_grid)  
resample.update()  
result = resample.output  

* It is particularly convenient because the input dataset defines the output geometry, while the source provides the values to be sampled.

## Thresholding :: vtkThreshold

* Which elements satisfy a numerical condition? (Exm: σVM​>400 MPa)

**vtkThreshold:**

> from vtkmodules.vtkFiltersCore import vtkThreshold

## Result extraction :: 

Selecting and obtaining a subset of the dataset and/or its result arrays.

* Extract by ID -> vtkSelection + vtkExtractSelection
* vtkSelection 
* vtkExtractSelection
* vtkExtractCells
* !Geometric extraction -> You can also select based on space rather than results
                          Give me all elements inside this sphere.

> from vtkmodules.vtkFiltersExtraction import vtkExtractSelection

