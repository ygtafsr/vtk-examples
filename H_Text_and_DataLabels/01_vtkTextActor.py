import vtkmodules.vtkRenderingFreeType
import vtkmodules.vtkRenderingOpenGL2

from vtkmodules.vtkRenderingCore import (
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkTextActor,
)


# --------------------------------------------------
# Renderer
# --------------------------------------------------

renderer = vtkRenderer()
renderer.SetBackground(0.1, 0.2, 0.3)

# --------------------------------------------------
# Render window
# --------------------------------------------------

render_window = vtkRenderWindow()
render_window.AddRenderer(renderer)
render_window.SetSize(800, 600)

# --------------------------------------------------
# Interactor
# --------------------------------------------------

interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# --------------------------------------------------
# Text actor
# --------------------------------------------------

text = vtkTextActor()
text.SetInput("Maximum Stress: 423 MPa")
text.SetDisplayPosition(20, 550)
text.GetTextProperty().SetFontSize(30)
text.GetTextProperty().SetColor(1.0, 1.0, 1.0)
text.GetTextProperty().BoldOn()

renderer.AddActor(text)

interactor.Initialize()
render_window.Render()
interactor.Start()