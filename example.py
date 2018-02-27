#!/usr/bin/env python

from pypyueye import Camera, FrameThread, SaveThread, RecordThread, \
    PyuEyeQtApp, PyuEyeQtView, UselessThread, CircleDetector
from pyueye import ueye


if __name__ == "__main__":
    with Camera(device_id=0, buffer_count=10) as cam:
        #======================================================================
        # Camera settings
        #======================================================================
        # TODO: Add more config properties (fps, gain, ...)
        cam.set_colormode(ueye.IS_CM_BGR8_PACKED)  # TODO: Make this Grayscale
        cam.set_aoi(0, 0, 800, 400)
        cam.set_fps(4)
        cam.get_fps()

        # #======================================================================
        # # Live video
        # #======================================================================
        # # we need a QApplication, that runs our QT Gui Framework
        # app = PyuEyeQtApp()
        # # a basic qt window
        # view = PyuEyeQtView()
        # view.show()
        # # a thread that waits for new images and processes all connected views
        # thread = FrameThread(cam, view)
        # thread.start()
        # app.exit_connect(thread.stop)
        # # Run and wait for the app to quit
        # app.exec_()

        # #======================================================================
        # # Live video with circle detection
        # #======================================================================
        # # we need a QApplication, that runs our QT Gui Framework
        # app = PyuEyeQtApp()
        # # a basic qt window
        # view = PyuEyeQtView()
        # # Create a circle detector and associate it to the view
        # cd = CircleDetector(nmb_circ=1, damp=.1)
        # view.user_callback = cd.process
        # # Show the view
        # view.show()
        # # a thread that waits for new images and processes all connected views
        # thread = FrameThread(cam, view)
        # thread.start()
        # app.exit_connect(thread.stop)
        # # Run and wait for the app to quit
        # app.exec_()

        # #======================================================================
        # # Save an image
        # #======================================================================
        # # Create a thread to save just one image
        # thread = SaveThread(cam, path="/home/muahah/tmp/ueye_image.png")
        # thread.start()
        # # Wait for the thread to end
        # thread.join()

        # #======================================================================
        # # Save a video
        # #======================================================================
        # # Create a thread to save a video
        # thread = RecordThread(cam, path="/home/muahah/tmp/ueye_image.avi",
        #                       nmb_frame=10, verbose=True)
        # thread.start()
        # # Wait for the thread to edn
        # thread.join()

        # #======================================================================
        # # Debugging
        # #======================================================================
        # import time
        # # a thread that do nearly nothing
        # thread = UselessThread(cam)
        # thread.start()
        # time.sleep(10)
        # thread.stop()
        # # Run and wait for the app to quit
