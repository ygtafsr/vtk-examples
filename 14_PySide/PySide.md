
:: Resources ::

> https://doc.qt.io/qtforpython-6/tutorials/index.html (Official PySide Tutorial)

> https://www.pythonguis.com/pyside6-tutorial/


# PySide6-VTKInteractorWindow Development+Integration Pipeline

1) QTDesigner -> Create a QWidget as QVTKRenderWindowInteractor placeholder
    (Right Widgets box -> Filter/Search -> "Widget" or use default "QWidget")

2) Right Click the QWidget -> Prmote to..   -> Promoted Class Name :: QVTKRenderWindowInteractor
                                            -> Header File :: vtkmodules.qt.QVTKRenderWindowInteractor.h

3) Save the desing as .ui into project folder 

4) Run Command Prompt in the project directory: 
        pyside6-uic mainwindow.ui -o ui_mainwindow.py
        (This generates ui.mainwindow.py)

## !! Important Notes !!

1) main.py or ui_mainwindow.py should have this imports:

- Register VTK's OpenGL renderer and interaction style before creating the Qt widget.  
  
    import vtkmodules.vtkInteractionStyle  
    import vtkmodules.vtkRenderingOpenGL2  
    from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

# QVTKRenderWindowInteractor

Uses a vtkGenericRenderWindowInteractor () to handle the interactions.
(https://vtk.org/doc/nightly/html/classvtkGenericRenderWindowInteractor.html)  

Use GetRenderWindow() to get the vtkRenderWindow.

# QT-VTK Event Pipeline

