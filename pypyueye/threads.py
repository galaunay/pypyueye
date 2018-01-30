#!/usr/bin/env python

#------------------------------------------------------------------------------
#                 PyuEye example - utilities modul
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

from pyueye import ueye
from threading import Thread
from .utils import ImageData, ImageBuffer
import cv2


class GatherThread(Thread):
    def __init__(self, cam, copy=True):
        """
        Thread used for gather images.
        """
        super().__init__()
        self.timeout = 1000
        self.cam = cam
        self.cam.capture_video()
        self.running = True
        self.copy = copy

    def run(self):
        while self.running:
            img_buffer = ImageBuffer()
            ret = ueye.is_WaitForNextImage(self.cam.handle(),
                                           self.timeout,
                                           img_buffer.mem_ptr,
                                           img_buffer.mem_id)
            if ret == ueye.IS_SUCCESS:
                imdata = ImageData(self.cam.handle(), img_buffer)
                self.process(imdata)

    def process(self, image_data):
        pass

    def stop(self):
        self.cam.stop_video()
        self.running = False


class FrameThread(GatherThread):
    def __init__(self, cam, views=None, copy=True):
        """
        Thread used for live display.
        """
        super().__init__(cam=cam, copy=copy)
        self.views = views

    def process(self, image_data):
        if self.views:
            if type(self.views) is not list:
                self.views = [self.views]
            for view in self.views:
                view.handle(image_data)


class UselessThread(GatherThread):
    def __init__(self, cam, views=None, copy=True):
        """
        Thread used for debugging only.
        """
        super().__init__(cam=cam, copy=copy)
        self.views = views

    def process(self, image_data):
        print(self.cam.get_exposure())
        import numpy as np
        new_exp = np.random.rand()*20
        self.cam.set_exposure(new_exp)
        print(f"nex exposure {new_exp}")
        print(self.cam.get_exposure())


class SaveThread(GatherThread):
    def __init__(self, cam, path, copy=True):
        """
        Thread used for saving images.
        """
        super().__init__(cam=cam, copy=copy)
        self.path = path

    def process(self, image_data):
        cv2.imwrite(self.path, image_data.as_1d_image())
        self.stop()


class RecordThread(GatherThread):
    def __init__(self, cam, path, nmb_frame=10, copy=True, verbose=False):
        """
        Thread used to record videos.
        """
        super().__init__(cam=cam, copy=copy)
        self.nmb_frame = nmb_frame
        self.verbose = verbose
        self.ind_frame = 0
        self.path = path
        aoi = self.cam.get_aoi()
        # TODO: add real fps
        # Create videowriter instance
        fourcc = cv2.VideoWriter_fourcc("M", "P", "E", "G")
        self.vw = cv2.VideoWriter(self.path,
                                  fourcc=fourcc,
                                  fps=24,
                                  frameSize=(aoi.width, aoi.height),
                                  isColor=0)

    def process(self, imdata):
        self.vw.write(imdata.as_1d_image()[:, :, 2])
        self.ind_frame += 1
        if self.verbose:
            print(f"\r{self.ind_frame}/{self.nmb_frame} frames taken", end="")
        # stop
        if self.ind_frame >= self.nmb_frame:
            if self.verbose:
                print("")
            self.stop()

    def stop(self):
        self.vw.release()
        super().stop()
