# -*- coding: utf-8 -*-
#!/usr/env python3

# Copyright (C) 2017 Gaby Launay

# Author: Gaby Launay  <gaby.launay@tutanota.com>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

__author__ = "Gaby Launay"
__copyright__ = "Gaby Launay 2017"
__credits__ = ""
__license__ = "GPL3"
__version__ = ""
__email__ = "gaby.launay@tutanota.com"
__status__ = "Development"


from camera import Camera
from utils import FrameThread, SaveThread, RecordThread
from gui import PyuEyeQtApp, PyuEyeQtView
from PyQt5 import QtGui
from pyueye import ueye
import cv2
import numpy as np


class CircleDetector(object):
    def __init__(self, nmb_circ, min_dist=100):
        """

        """
        self.nmb_circ = nmb_circ
        self.dp = 1.5
        self.min_dist = min_dist
        self.xy_center = []

    def process(self, image_data):
        """
        Detect circles and draw them on the image
        """
        # Find circles on the given image
        image = image_data.as_1d_image()
        image_bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        circles = cv2.HoughCircles(image_bw, cv2.HOUGH_GRADIENT, self.dp,
                                   self.min_dist)
        # Adapt circle detector parameter to reach the right number of circles
        if circles is None:
            self.dp *= 1.1
        else:
            self.dp /= len(circles[0])/self.nmb_circ
        # Add circles on the image
        if circles is not None:
            circles = np.round(circles[0, :]).astype("int")
            for (x, y, r) in circles:
                cv2.circle(image, (x, y), r, (0, 200, 0), 4)
                cv2.circle(image, (x, y), 0, (200, 0, 0), 10)
            if len(circles) == 1:
                self.xy_center.append([circles[0][0],
                                       circles[0][1]])
        # Add the main circle trajectory on the image
        if len(self.xy_center) > 2:
            for i in range(len(self.xy_center) - 1):
                cv2.line(image,
                         tuple(self.xy_center[i]),
                         tuple(self.xy_center[i + 1]),
                         (200, 0, 0), 4)
        # Return the image to Qt for display
        return QtGui.QImage(image.data,
                            image_data.mem_info.width,
                            image_data.mem_info.height,
                            QtGui.QImage.Format_RGB888)


if __name__ == "__main__":
    with Camera(device_id=0, buffer_count=10) as cam:
        #======================================================================
        # Camera settings
        #======================================================================
        # TODO: Add more config properties (fps, gain, ...)
        cam.set_colormode(ueye.IS_CM_BGR8_PACKED)  # TODO: Make this Grayscale
        cam.set_aoi(0, 0, 1280, 1024)

        #======================================================================
        # Live video
        #======================================================================
        # we need a QApplication, that runs our QT Gui Framework
        app = PyuEyeQtApp()
        # a basic qt window
        view = PyuEyeQtView()
        view.show()
        # a thread that waits for new images and processes all connected views
        thread = FrameThread(cam, view)
        thread.start()
        app.exit_connect(thread.stop)
        # Run and wait for the app to quit
        app.exec_()

        #======================================================================
        # Live video with circle detection
        #======================================================================
        # we need a QApplication, that runs our QT Gui Framework
        app = PyuEyeQtApp()
        # a basic qt window
        view = PyuEyeQtView()
        # Create a circle detector and associate it to the view
        cd = CircleDetector(nmb_circ=1)
        view.user_callback = cd.process
        # Show the view
        view.show()
        # a thread that waits for new images and processes all connected views
        thread = FrameThread(cam, view)
        thread.start()
        app.exit_connect(thread.stop)
        # Run and wait for the app to quit
        app.exec_()

        #======================================================================
        # Save an image
        #======================================================================
        # Create a thread to save just one image
        thread = SaveThread(cam, path="/home/muahah/tmp/ueye_image.png")
        thread.start()
        # Wait for the thread to end
        thread.join()

        #======================================================================
        # Save a video
        #======================================================================
        # Create a thread to save a video
        thread = RecordThread(cam, path="/home/muahah/tmp/ueye_image.avi",
                              nmb_frame=10)
        thread.start()
        # Wait for the thread to edn
        thread.join()
