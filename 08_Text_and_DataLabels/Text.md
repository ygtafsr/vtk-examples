
# VTK TEXT ANNOTATIONS

For VTK, there are two fundamentally different ways to create text annotations, 
depending on whether the text belongs to the 3D scene or the 2D screen.  

* Method-1 :: use vtkTextActor
* Method-2 :: use vtkVectorText
* Method-3 :: use vtkLabelPlacementMapper

## Method 1 :: vtkTextActor
### The Pipeline for vtkTextActor is:

TextData    
      ↓   
vtkTextActor  
      ↓   
vtkRenderer 


## Method 2 :: vtkVectorText + vtkFollower  
### The Pipeline for vtkVectorText is:

vtkVectorText  
      ↓  
vtkPolyDataMapper  
      ↓  
vtkFollower  
      ↓  
vtkRenderer  

### The vtkFollower is used instead of vtkActor because it automatically faces the active camera. !!!

vtkVectorText
    = generates the TEXT GEOMETRY

vtkPolyDataMapper
    = converts that geometry for rendering

vtkFollower
    = places/orients the text in 3D and faces the camera

vtkTextActor
    = renders TEXT AS A 2D SCREEN OVERLAY

 
## Method 3 :: vtkLabelPlacementMapper

But there is an even better architecture for thousands or millions of FEA nodes: don't create thousands of independent text pipelines. At that scale, we should look at batched label rendering / vtkLabelPlacementMapper / point-data labels, depending on the interaction requirements.