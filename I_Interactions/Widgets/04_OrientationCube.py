"""
https://vtk.org/doc/nightly/html/classvtkAnnotatedCubeActor.html

There are Three VTK Camera Orientation widget approach:

| Requirement                                 | VTK solution                                           |
| ------------------------------------------- | ------------------------------------------------------ |
| Show orientation cube                       | `vtkOrientationMarkerWidget` + `vtkAnnotatedCubeActor` |
| Control camera orientation                  | `vtkCameraOrientationWidget`                           |
| CAD-style clickable cube controlling camera | **Custom cube + picking/camera logic**                 |


    Cube face
    ↓
    Picking
    ↓
    Determine orientation
    ↓
    Set camera position/view-up
    ↓
    Render

"""



