#!/usr/bin/env python

#------------------------------------------------------------------------------
#                 PyuEye example - camera modul
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
from pyueye_example_utils import (uEyeException, Rect, get_bits_per_pixel,
                                  ImageBuffer, check)


class Camera(object):
    def __init__(self, device_id=0):
        self.h_cam = ueye.HIDS(device_id)
        self.img_buffers = []

    def __enter__(self):
        self.init()
        return self

    def __exit__(self, _type, value, traceback):
        self.exit()

    def handle(self):
        """
        Return the camera handle.
        """
        return self.h_cam

    def alloc(self, buffer_count=3):
        """
        Allocate memory for futur images.

        Parameters
        ==========
        buffer_count: integer
            Number of memory buffer to use.
        """
        # Get camera settings
        rect = self.get_aoi()
        bpp = get_bits_per_pixel(self.get_colormode())
        # Check that already existing buffers are free
        for buff in self.img_buffers:
            check(ueye.is_FreeImageMem(self.h_cam, buff.mem_ptr, buff.mem_id))
        # Create asked buffers
        for i in range(buffer_count):
            buff = ImageBuffer()
            ueye.is_AllocImageMem(self.h_cam,
                                  rect.width, rect.height, bpp,
                                  buff.mem_ptr, buff.mem_id)
            check(ueye.is_AddToSequence(self.h_cam, buff.mem_ptr, buff.mem_id))
            self.img_buffers.append(buff)
        # Check that ...
        ueye.is_InitImageQueue(self.h_cam, 0)

    def init(self):
        """
        Initialize a connection to the camera.

        Returns
        =======
        ret: integer
            Return code from the camera.
        """
        ret = ueye.is_InitCamera(self.h_cam, None)
        if ret != ueye.IS_SUCCESS:
            self.h_cam = None
            raise uEyeException(ret)
        return ret

    def exit(self):
        """
        Close the connection to the camera.
        """
        ret = None
        if self.h_cam is not None:
            ret = ueye.is_ExitCamera(self.h_cam)
        if ret == ueye.IS_SUCCESS:
            self.h_cam = None

    def get_aoi(self):
        """
        Get the current area of interest.

        Returns
        =======
        rect: Rect object
            Area of interest
        """
        rect_aoi = ueye.IS_RECT()
        ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_GET_AOI, rect_aoi,
                    ueye.sizeof(rect_aoi))
        return Rect(rect_aoi.s32X.value,
                    rect_aoi.s32Y.value,
                    rect_aoi.s32Width.value,
                    rect_aoi.s32Height.value)

    def set_aoi(self, x, y, width, height):
        """
        Set the area of interest.

        Parameters
        ==========
        x, y, width, height: integers
            Position and size of the area of interest.
        """
        rect_aoi = ueye.IS_RECT()
        rect_aoi.s32X = ueye.int(x)
        rect_aoi.s32Y = ueye.int(y)
        rect_aoi.s32Width = ueye.int(width)
        rect_aoi.s32Height = ueye.int(height)
        return ueye.is_AOI(self.h_cam, ueye.IS_AOI_IMAGE_SET_AOI, rect_aoi,
                           ueye.sizeof(rect_aoi))

    def capture_video(self, wait=False):
        """
        Begin capturing a video.

        Parameters
        ==========
        wait: boolean
           To wait or not for the camera frames (default to False).
        """
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_CaptureVideo(self.h_cam, wait_param)

    def stop_video(self):
        """
        Stop capturing the video.
        """
        return ueye.is_StopLiveVideo(self.h_cam, ueye.IS_FORCE_VIDEO_STOP)

    def freeze_video(self, wait=False):
        """
        Freeze the video capturing.

        Parameters
        ==========
        wait: boolean
           To wait or not for the camera frames (default to False).
        """
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_FreezeVideo(self.h_cam, wait_param)

    def set_colormode(self, colormode):
        """
        Set the colormode.

        Parameters
        ==========
        colormode: pyueye color mode
            Colormode, as 'pyueye.IS_CM_BGR8_PACKED' for example.
        """
        check(ueye.is_SetColorMode(self.h_cam, colormode))

    def get_colormode(self):
        """
        Get the current colormode.
        """
        ret = ueye.is_SetColorMode(self.h_cam, ueye.IS_GET_COLOR_MODE)
        return ret

    def get_format_list(self):
        """

        """
        count = ueye.UINT()
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_NUM_ENTRIES,
                                  count, ueye.sizeof(count)))
        format_list = ueye.IMAGE_FORMAT_LIST(ueye.IMAGE_FORMAT_INFO *
                                             count.value)
        format_list.nSizeOfListEntry = ueye.sizeof(ueye.IMAGE_FORMAT_INFO)
        format_list.nNumListElements = count.value
        check(ueye.is_ImageFormat(self.h_cam, ueye.IMGFRMT_CMD_GET_LIST,
                                  format_list, ueye.sizeof(format_list)))
        return format_list
