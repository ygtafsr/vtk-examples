
# https://examples.vtk.org/site/Python/Visualization/NamedColors/

"""
vtkNamedColors is essentially a color-name → numerical color-value lookup utility.

from vtkmodules.vtkCommonColor import vtkNamedColors
colors = vtkNamedColors()
print(colors.color_names)

The exact values come from VTK's named-color table.
This makes it directly suitable for properties such as:
actor.property.color = colors.GetColor3d("Tomato")
actor.property.edge_color = colors.GetColor3d("Black")


#### There is another useful VTK color API ###
from vtkmodules.util import colors
This module contains named color values such as:
colors.red
colors.blue
colors.white
colors.black
colors.tomato
colors.ivory
colors.slate_grey
So you can write:
actor.property.color = colors.tomato

### Usage Pipeline:

UnstructuredGrid
      │
      ▼
vtkDataSetMapper
      │
      ▼
vtkActor
      │
      │ property.color
      ▼
Renderer
      │
      ▼
RenderWindow

"""
import numpy as np
from vtkmodules.vtkCommonColor import vtkNamedColors

colors = vtkNamedColors()
red = colors.GetColor3d("Red")
green = colors.GetColor3d("Green")
blue = colors.GetColor3d("Blue")
print(np.array([red, green, blue]))
#[[1.         0.         0.        ]
# [0.         0.50196078 0.        ]
# [0.         0.         1.        ]]

from vtkmodules.util import colors
print(colors.green) # returns RGB tuple : (0.0, 1.0, 0.0)
