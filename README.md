# Pypyueye

Convenience wrapper around [pyueye](https://pypi.python.org/pypi/pyueye) API for IDS cameras.

Pypyueye allows to easily display live videos, save images or record videos usin IDS cameras.
It is also easy to plug the live video through [opencv](https://opencv.org/) for live image analysis.

## Installation

```Python
python setup.py install
```

The dependencies (`pyueye` and `opencv`) should be installed automatically.

You still have to install the IDS driver for the camera you intend to use.

## Usage

The following script allows to display the live video:
```Python
from pypyueye import Camera, FrameThread, PyuEyeQtApp, PyuEyeQtView
from pyueye import ueye

with Camera(device_id=0, buffer_count=10) as cam:
    #======================================================================
    # Camera settings
    #======================================================================
    cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
    cam.set_aoi(0, 0, 800, 400)
    cam.set_fps(4)

    #======================================================================
    # Get Live video
    #======================================================================
    # Set up the view
    app = PyuEyeQtApp()
    view = PyuEyeQtView()
    view.show()
    # Set up the thread gathering images
    thread = FrameThread(cam, view)
    thread.start()
    # Stop the thread on view closing
    app.exit_connect(thread.stop)
    app.exec_()
```

See [example.py](https://github.com/galaunay/pypyueye/blob/master/example.py) for more examples.

## Documentation

Pypyueye is documented inline.
The documentation of the [Camera](https://github.com/galaunay/pypyueye/blob/master/pypyueye/camera.py#L35) class is a good start.
