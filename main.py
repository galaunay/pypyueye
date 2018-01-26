#!/usr/bin/env python

#------------------------------------------------------------------------------
#                 PyuEye example - main modul
#
# Copyright (c) 2017 by IDS Imaging Development Systems GmbH.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#------------------------------------------------------------------------------

import pdb
import sys
sys.path.append('/home/muahah/Postdoc_GSLIPS/180119-test_ueye_cam')
from camera import Camera
from utils import FrameThread, SaveThread, RecordThread
from gui import PyuEyeQtApp, PyuEyeQtView
from PyQt5 import QtGui
import time

from pyueye import ueye

import cv2
import numpy as np

def process_image(self, image_data):
    # find circles
    image = image_data.as_1d_image()
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(image, cv2.HOUGH_GRADIENT, self.dp, 100)
    # adapt dp to reach the right number of circles
    if circles is None:
        self.dp *= 1.1
    else:
        self.dp /= len(circles[0])/self.nmb_circ
    # make a color image again to mark the circles in green
    image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (x, y, r) in circles:
            cv2.circle(image, (x, y), r, (0, 255, 0), 4)
            cv2.circle(image, (x, int(y-r/3)), 0, (255, 0, 0), 10)
        if len(circles) == 1:
            self.xy.append([circles[0][0],
                            int(circles[0][1] - circles[0][2]/3)])
    if len(self.xy) > 2:
        for i in range(len(self.xy) - 1):
            cv2.line(image, tuple(self.xy[i]), tuple(self.xy[i + 1]),
                     (255, 0, 0), 4)
    # show the image with Qt
    return QtGui.QImage(image.data,
                        image_data.mem_info.width,
                        image_data.mem_info.height,
                        QtGui.QImage.Format_RGB888)


def main():
    # camera class to simplify uEye API access
    cam = Camera()
    cam.init()
    cam.set_colormode(ueye.IS_CM_BGR8_PACKED)
    cam.set_aoi(0,0, 1280, 1024)
    cam.alloc()
    cam.capture_video()

    #==============================================================================
    # View live video
    #==============================================================================
    # we need a QApplication, that runs our QT Gui Framework
    app = PyuEyeQtApp()
    # a basic qt window
    view = PyuEyeQtView()
    view.dp = 1.5
    view.nmb_circ = 1
    view.xy = []
    view.show()
    view.user_callback = process_image
    # a thread that waits for new images and processes all connected views
    thread = FrameThread(cam, view)
    thread.start()
    # cleanup
    # app.exit_connect(thread.stop)
    app.exec_()
    cam.stop_video()
    cam.exit()


    # #=======================================================j==================
    # # Save an image
    # #==========================================================================
    # # a thread that waits for a new image and save it to a file
    # thread = SaveThread(cam, path="/home/muahah/tmp/ueye_image.png")
    # thread.start()
    # while thread.running:
    #     time.sleep(1)
    # cam.stop_video()
    # cam.exit()

    # #=======================================================j==================
    # # Save a video
    # #==========================================================================
    # #False Falsei thread that waits for a new image and save it to a file
    # raise Exception("Not working yet")
    # thread = RecordThread(cam, path="/home/muahah/tmp/ueye_image.avi",
    #                       nmb_frame=10)
    # thread.start()
    # while thread.running:
    #     time.sleep(1)
    # cam.stop_video()
    # cam.exit()

if __name__ == "__main__":
    main()
