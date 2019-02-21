#!/usr/bin/env python

from pypyueye import Camera, FrameThread, SaveThread, RecordThread, \
    PyuEyeQtApp, PyuEyeQtView, UselessThread, CircleDetector
from pyueye import ueye
import matplotlib.pyplot as plt


if __name__ == "__main__":
    with Camera(device_id=0, buffer_count=100) as cam:
        #======================================================================
        # Camera settings
        #======================================================================
        # TODO: Add more config properties (fps, gain, ...)
        cam.set_colormode(ueye.IS_CM_MONO8)
        #
        cam.set_aoi(0, 0, 800, 800)
        print(f"INITIAL VALUES")
        print(f'fps: {cam.get_fps()}')
        print(f'Available fps range: {cam.get_fps_range()}')
        print(f'Pixelclock: {cam.get_pixelclock()}')
        cam.set_pixelclock(100)
        cam.set_fps(20)
        print("")
        print(f"MODIFIED VALUES")
        print(f'fps: {cam.get_fps()}')
        print(f'Available fps range: {cam.get_fps_range()}')
        print(f'Pixelclock: {cam.get_pixelclock()}')

       # #==============================================================================
       # # Capturing images in memory
       # #==============================================================================
       # import time
       # a = time.time()
       # nmb_ims = 100
       # ims = cam.capture_images(nmb_ims)
       # fps = cam.get_fps()
       # fpsr = cam.get_fps_range()
       # print("")
       # print(f"AFTER CAPTURE VALUES")
       # print(f"Framerate: {fps}")
       # print(f'Measured framerate: {nmb_ims/(time.time() - a)}')
       # print(f"Frame range: {fpsr[0]}, {fpsr[1]}")

       # plt.figure()
       # plt.imshow(ims[-1])
       # plt.show()


       # #======================================================================
       # # Live video
       # #======================================================================
       # # qt only deals with color images ?
       # cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
       # #we need a QApplication, that runs our QT Gui Framework
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
       # # qt only deals with color images ?
       # cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
       # # we need a QApplication, that runs our QT Gui Framework
       # app = PyuEyeQtApp()
       # # a basic qt window
       # view = PyuEyeQtView()
       # # Create a circle detector and associate it to the view
       # cd = CircleDetector(nmb_circ=[1, 1], damp=.1)
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
        # cam.set_colormode(ueye.IS_CM_MONO8)
        # # Create a thread to save a video
        # thread = RecordThread(cam, path="ueye_video.avi",
        #                       nmb_frame=100, verbose=True)
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
