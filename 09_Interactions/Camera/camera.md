

### Resources:

https://examples.vtk.org/site/PythonicAPI/Visualization/DistanceToCamera/


# Cameras

https://book.vtk.org/en/latest/VTKBook/03Chapter3.html#cameras

There are a number of important factors that determine how a 3D scene gets projected onto a plane to form a 2D image.
These are the "position", "orientation", and "focal point" of the camera, the method of camera projection, and the location of the camera clipping planes.

Concepts:  

- "Position" of the Camera
- "Location" of the Camera
- "Orientation" of the Camera
- "Focal Point" of the Camera


## Camera View

Together these completely define the camera view:

### 1) Location of the Camera

The "position" and "focal point" of the camera define the location of the camera and where it points.  

### 2) Direction of Projection

The vector defined from the camera position to the focal point is called the direction of projection.

### 3) The Camera Image Plane

The camera image plane is located at the focal point and is typically perpendicular to the projection vector.

### 4) Camera Orientations

The camera orientation is controlled by the "position + focal point -> Location" plus the camera "view-up vector". Together these completely define the camera view.


## Orthographic projection (or parallel projection)

Orthographic projection is a parallel mapping process. In orthographic projection (or parallel projection) all rays of light entering the camera are parallel to the projection vector.

## Perspective projection

Perspective projection occurs when all light rays go through a common point (i.e., the viewpoint or center of projection). To apply perspective projection we must specify a perspective angle or camera view angle.

## Clipping Planes

The front and back clipping planes intersect the projection vector, and are usually perpendicular to it. The clipping planes are used to eliminate data either too close to the camera or too far away. As a result only actors or portions of actors within the clipping planes are (potentially) visible. Clipping planes are typically perpendicular to the direction of projection. Their locations can be set using the camera’s clipping range. The location of the planes are measured from the camera’s position along the direction of projection. The front clipping plane is at the minimum range value, and the back clipping plane is at the maximum range value. 

## View Frustum

Taken together these camera parameters define a rectangular pyramid, with its apex at the camera’s position and extending along the direction of projection. The pyramid is truncated at the top with the front clipping plane and at the bottom by the back clipping plane. The resulting view frustum defines the region of 3D space visible to the camera.

## Camera Manipulation

While a camera can be manipulated by directly setting the attributes mentioned above, there are some common operations that make the job easier.

1) Azimuth

Changing the azimuth of a camera rotates its position around its view up vector, centered at the focal point. Think of this as moving the camera to the left or right while always keeping the distance to the focal point constant. 

2) Elevation

Changing a camera’s elevation rotates its position around the cross product of its direction of projection and view up centered at the focal point. This corresponds to moving the camera up and down.

3) Roll

To roll the camera, we rotate the view up vector about the view plane normal. Roll is sometimes called twist.

-------------
> The next two motions keep the camera’s position constant and instead modify the focal point.
-------------

4) Yaw

Changing the yaw rotates the focal point about the view up centered at the camera’s position. This is like an azimuth, except that the focal point moves instead of the position.

5) Pitch

Changes in pitch rotate the focal point about the cross product of the direction of projection and view up centered at the camera’s position.

6) Dolly

Dollying in and out moves the camera’s position along the direction of projection, either closer or farther from the focal point. This operation is specified as the ratio of its current distance to its new distance. A value greater than one will dolly in, while a value less than one will dolly out.

7) Zoom

Finally, zooming changes the camera’s view angle, so that more or less of the scene falls within the view frustum.