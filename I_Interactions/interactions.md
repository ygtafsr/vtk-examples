
https://examples.vtk.org/site/PythonicAPI/#user-interaction

https://examples.vtk.org/site/PythonicAPI/Snippets/Callbacks/

https://examples.vtk.org/site/PythonicAPI/Picking/AreaPicking/

https://docs.vtk.org/en/latest/release_details/9.7/add-camera-manipulators.html


# Key Concepts:

- Interactor (vtkRenderWindowInteractor)
- Event/QTEvent/VTK Event/Callback
- vtkInteractorObserver (The most basic VTK event handling mechanism)
- InteractorStyle (VTK pre-defined observers for camera movements. Customizable.)
- Camera Manipulators
- vtkWidgets
- vtkCamera
- vtkPicker (AreaPicking, CellPicking, PointPicking)
- vtkRubberBand3D

## vtkRenderWindowInteractor (The most important concept!)

* It takes a vtkRendererWindow and creates an vtk event mechanism on this renderer window. So,
the operating system inputs(signals) converted into "native vtk named" events. For example, a left mouse click
on the renderer window translated into vtk's "LeftButtonPressEvent" or a key press into "KeyPressEvent".

* We the use interactor observers to connect this events to Callback functions(Event Handlers) like:  
interactor.AddObserver("LeftButtonPressEvent", On_Left_Button_Press)  
Now, we can define event handling logic inside On_Left_Button_Press() Callback.

* VTK has other high-level observer mechanisms such as:
    - vtkInteractorStyle (Connects mouse events to camera movements)
    - vtkWidgets
    - vtkPicker
    - vtkRubberBand3D ?


            vtkObject
                │
                ▼
            vtkInteractorObserver
                │
                ├── vtkInteractorStyle
                │
                ├── vtk3DWidget
                │
                └── other interaction observers (vtkPicker, vtkRubberBand ..?)

* The VTK Book explicitly states that vtkInteractorStyle and 3D widgets are subclasses of vtkInteractorObserver.  
  This means they are designed to observe interaction events associated with a render window.  

* We can add a new observer for events directly from vtkRenderWindowInteractor or interactor style classes.

* Generally speaking, it's a platform-independent mechanism for mouse, keyboard and timer events, 
routing those events to vtkInteractorObserver objects and providing facilities such as picking.

        OS
        │
        ├── mouse down
        ├── mouse move
        ├── mouse wheel
        ├── key press
        └── touch
            │
            ▼
        vtkRenderWindowInteractor
            │
            ▼
        VTK events
            │
            ├── LeftButtonPressEvent
            ├── MouseMoveEvent
            ├── KeyPressEvent
            ├── MouseWheelForwardEvent
            └── ...

### VTK Mouse Events
--------------------------------------

| Event                        | Meaning                           |
| ---------------------------- | --------------------------------- |
| `"LeftButtonPressEvent"`     | Left mouse button pressed         |
| `"LeftButtonReleaseEvent"`   | Left mouse button released        |
| `"MiddleButtonPressEvent"`   | Middle/mouse-wheel button pressed |
| `"MiddleButtonReleaseEvent"` | Middle button released            |
| `"RightButtonPressEvent"`    | Right mouse button pressed        |
| `"RightButtonReleaseEvent"`  | Right button released             |
| `"MouseMoveEvent"`           | Mouse moved                       |
| `"MouseWheelForwardEvent"`   | Wheel scrolled forward            |
| `"MouseWheelBackwardEvent"`  | Wheel scrolled backward           |
| `"EnterEvent"`               | Mouse entered render window       |
| `"LeaveEvent"`               | Mouse left render window          |


### VTK Keyboard Events
-------------------------

| Event               | Meaning                             |
| ------------------- | ----------------------------------- |
| `"KeyPressEvent"`   | Key pressed                         |
| `"KeyReleaseEvent"` | Key released                        |
| `"CharEvent"`       | Character/key-press character event |
| `"DeleteEvent"`     | Delete key event                    |
| `"ConfigureEvent"`  | Window configuration changed        |


> KeyPressEvent: reports that a keyboard key was pressed. It is useful for detecting keys such as F1, arrows, Escape, or combinations with Ctrl/Shift. You typically inspect GetKeySym().

> CharEvent: reports the resulting character input after keyboard processing. VTK’s built-in shortcuts, such as q to quit, are handled here by interactor styles.


VTK Interaction System Summary
-----------------------------------------


                         OPERATING SYSTEM
                              │
                    mouse / keyboard / etc.
                              │
                              ▼
                 ┌──────────────────────────┐
                 │ vtkRenderWindowInteractor│
                 │                          │
                 │ receives input           │
                 │ translates input         │
                 └────────────┬─────────────┘
                              │
                              ▼
                         VTK EVENT
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
          OBSERVERS                  INTERACTOR STYLE (vtkInteractorObserver > vtkInteractorStyle)
                 │                         │
                 │                         │ interprets
                 │                         ▼
                 │                       CAMERA
                 │                         │
                 ▼                         │
         application logic (our callbak)   │
                 │                         │
                 └────────────┬────────────┘
                              ▼
                         RENDERER
                              │
                              ▼
                       RENDER WINDOW
                              │
                              ▼
                           SCREEN


> And then widgets fit in as another observer:

                         VTK EVENT
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
           Callback    InteractorStyle   Widget (vtkInteractorObserver > vtk3DWidget)
                │            │            │
                ▼            ▼            ▼
          App logic       Camera        Widget
                                          │
                                          ▼
                                        Scene



## Interaction styles

* The interaction style classes provide **event handling mechanisms** for vtkRenderWindowInteractor events.
* They basically provide implicit camera and renderer manipulation methods defined their Callback functions
  such as OnLeftButtonDown(), OnMouseMove().
* We can override their Callback functions with style.AddObserver("EventName", Callback) signature.

### Common Interactor Styles
----------------------------------
- vtkInteractorStyle (Parent Class)
- vtkInteractorStyleTrackballCamera (Concrete Class)
- vtkInteractorStyleRubberBand3D
- vtkInteractorStyleManipulator (Customizable Camera Actions)

### How to set Intearctor Style for an Interactor?
-----------------------------------
interactor = vtkRenderWindowInteractor()  
style = vtkInteractorStyleTrackballCamera()  

interactor.render_window = render_window  
interactor.interactor_style = style  

## Picking

* Picking converts a 2D screen coordinate into information about the 3D scene.
   
        2D SCREEN
            │
            Mouse
            │
            │ screen coordinates (x, y)
            ▼
            vtkRenderWindowInteractor
            │
            │ VTK event
            ▼
            Picker
            │
            ├── vtkPropPicker      → Actor / Prop
            ├── vtkPointPicker     → Point / Node
            ├── vtkCellPicker      → Cell / Element
            └── vtkWorldPointPicker → World coordinate
            │
            ▼
            Picked information
            │
            ├── ID
            ├── coordinates
            ├── actor
            └── dataset/data


| Picker                | Answers                    | FEA use       |
| --------------------- | -------------------------- | ------------- |
| `vtkPicker`           | Which prop's bounding box? | Low           |
| `vtkPropPicker`       | Which actor/prop?          | Medium        |
| `vtkPointPicker`      | Which point/node?          | **High**      |
| `vtkCellPicker`       | Which cell/element?        | **Very high** |
| `vtkWorldPointPicker` | What 3D world coordinate?  | **High**      |

    '''
    x, y = interactor.GetEventPosition()  

    picker = vtkPropPicker()  

    picker.Pick(x, y, 0, renderer)  

    actor = picker.GetActor()  
    '''

* vtkCellPicker shoots one ray from the camera through one screen position.
  vtkCellPicker performs surface/cell intersection along that ra
*  

### vtkHardwareSelector 
* It selects rendered primitives (such as visible cells) from a 2D screen rectangle.
* vtkHardwareSelector fundamentally concerned with what is actually rendered/visible in the selection region.
  So the front surface can be selected while the occluded back surface is not.

### vtkAreaPicker
* It constructs a 3D frustum corresponding to the rectangle which is A screen rectangle defines a volume in 3D space.
* vtkAreaPicker selects geometry/props inside a 3D frustum. Consequently, geometry located within that spatial volume 
  can be considered for selection, including geometry that is not necessarily the frontmost visible surface.

                     Rectangle
                         │
             ┌───────────┼───────────┐
             │           │           │
             ▼           ▼           ▼
       vtkAreaPicker   Hardware   Frustum
                         Selector   Selection
             │           │           │
             ▼           ▼           ▼
          3D props    Visible     Dataset
          /volume      cells      geometry

> Selection:

The VTK textbook also discusses selection/extraction as a separate concept from picking: selecting data means choosing cells/points within a defined region and extracting the associated attributes.

### vtkRenderedAreaPicker

picker.AreaPick(
    x0,
    y0,
    x1,
    y1,
    renderer,
)


## vtkCamera






# VTK Event Handling Mechanisms:

1) Observer approach:

> You can explicitly listen for the event:

    '''
    def on_key_press(caller, event):  

    if caller.GetKeySym() == "r":  
        renderer.ResetCamera()

    interactor.AddObserver(
    "KeyPressEvent",
    on_key_press)
    '''


2) InteractorStyle approach:

> The style itself can define how interaction behaves.

    '''
    style = vtkInteractorStyleTrackballCamera()

    interactor.SetInteractorStyle(style)
    '''
