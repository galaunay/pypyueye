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
from PyQt4 import QtGui
import cv2


error_codes = {ueye.IS_INVALID_EXPOSURE_TIME: "Invalid exposure time",
               ueye.IS_INVALID_CAMERA_HANDLE: "Invalid camera handle",
               ueye.IS_INVALID_MEMORY_POINTER: "Invalid memory pointer",
               ueye.IS_INVALID_PARAMETER: "Invalid parameter",
               ueye.IS_IO_REQUEST_FAILED: "IO request failed",
               ueye.IS_NO_ACTIVE_IMG_MEM: "No active IMG memory",
               ueye.IS_NO_USB20: "No USB2",
               ueye.IS_NO_SUCCESS: "No success",
               ueye.IS_NOT_CALIBRATED: "Not calibrated",
               ueye.IS_NOT_SUPPORTED: "Not supported",
               ueye.IS_OUT_OF_MEMORY: "Out of memory",
               ueye.IS_TIMED_OUT: "Timed out",
               ueye.IS_SUCCESS: "Success",
               ueye.IS_CANT_OPEN_DEVICE: "Cannot open device",
               ueye.IS_ALL_DEVICES_BUSY: "All device busy",
               ueye.IS_TRANSFER_ERROR: "Transfer error"}


bits_per_pixel = {ueye.IS_CM_SENSOR_RAW8: 8,
                  ueye.IS_CM_SENSOR_RAW10: 16,
                  ueye.IS_CM_SENSOR_RAW12: 16,
                  ueye.IS_CM_SENSOR_RAW16: 16,
                  ueye.IS_CM_MONO8: 8,
                  ueye.IS_CM_RGB8_PACKED: 24,
                  ueye.IS_CM_BGR8_PACKED: 24,
                  ueye.IS_CM_RGBA8_PACKED: 32,
                  ueye.IS_CM_BGRA8_PACKED: 32,
                  ueye.IS_CM_BGR10_PACKED: 32,
                  ueye.IS_CM_RGB10_PACKED: 32,
                  ueye.IS_CM_BGRA12_UNPACKED: 64,
                  ueye.IS_CM_BGR12_UNPACKED: 48,
                  ueye.IS_CM_BGRY8_PACKED: 32,
                  ueye.IS_CM_BGR565_PACKED: 16,
                  ueye.IS_CM_BGR5_PACKED: 16,
                  ueye.IS_CM_UYVY_PACKED: 16,
                  ueye.IS_CM_UYVY_MONO_PACKED: 16,
                  ueye.IS_CM_UYVY_BAYER_PACKED: 16,
                  ueye.IS_CM_CBYCRY_PACKED: 16}


def get_bits_per_pixel(color_mode):
    """
    Returns the number of bits per pixel for the given color mode.
    """
    if color_mode not in bits_per_pixel.keys():
        raise uEyeException(f'Unknown color mode: {color_mode}')
    return bits_per_pixel[color_mode]


class uEyeException(Exception):
    def __init__(self, error_code):
        self.error_code = error_code

    def __str__(self):
        if self.error_code in error_codes.keys():
                return error_codes[self.error_code]
        else:
            for att, val in ueye.__dict__.items():
                if att[0:2] == "IS" and val == self.error_code \
                   and ("FAILED" in att or
                        "INVALID" in att or
                        "ERROR" in att or
                        "NOT" in att):
                    return "Err: {} ({} ?)".format(str(self.error_code),
                                                   att)
            return "Err: " + str(self.error_code)


def check(error_code):
    """
    Check an error code, and raise an error if adequate.
    """
    if error_code != ueye.IS_SUCCESS:
        raise uEyeException(error_code)


class ImageBuffer:
    def __init__(self):
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()


class MemoryInfo:
    def __init__(self, h_cam, img_buff):
        self.x = ueye.int()
        self.y = ueye.int()
        self.bits = ueye.int()
        self.pitch = ueye.int()
        self.img_buff = img_buff
        rect_aoi = ueye.IS_RECT()
        check(ueye.is_AOI(h_cam,
                          ueye.IS_AOI_IMAGE_GET_AOI,
                          rect_aoi, ueye.sizeof(rect_aoi)))
        self.width = rect_aoi.s32Width.value
        self.height = rect_aoi.s32Height.value
        check(ueye.is_InquireImageMem(h_cam,
                                      self.img_buff.mem_ptr,
                                      self.img_buff.mem_id,
                                      self.x, self.y,
                                      self.bits, self.pitch))


class ImageData:
    def __init__(self, h_cam, img_buff):
        self.h_cam = h_cam
        self.img_buff = img_buff
        self.mem_info = MemoryInfo(h_cam, img_buff)
        self.color_mode = ueye.is_SetColorMode(h_cam, ueye.IS_GET_COLOR_MODE)
        self.bits_per_pixel = get_bits_per_pixel(self.color_mode)
        self.array = ueye.get_data(self.img_buff.mem_ptr,
                                   self.mem_info.width,
                                   self.mem_info.height,
                                   self.mem_info.bits,
                                   self.mem_info.pitch,
                                   True)

    def as_cv_image(self):
        return QtGui.QImage(self.as_1d_image().data,
                            self.mem_info.width,
                            self.mem_info.height,
                            QtGui.QImage.Format_RGB888)

    def as_1d_image(self):
        channels = int((7 + self.bits_per_pixel) / 8)
        import numpy
        if channels > 1:
            return numpy.reshape(self.array, (self.mem_info.height,
                                              self.mem_info.width, channels))
        else:
            return numpy.reshape(self.array, (self.mem_info.height,
                                              self.mem_info.width))

    def unlock(self):
        check(ueye.is_UnlockSeqBuf(self.h_cam, self.img_buff.mem_id,
                                   self.img_buff.mem_ptr))


class Rect:
    def __init__(self, x=0, y=0, width=0, height=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
