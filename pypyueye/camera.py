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


from pyueye import ueye
from .utils import (uEyeException, Rect, get_bits_per_pixel,
                    ImageBuffer, check, ImageData)


class Camera(object):
    def __init__(self, device_id=0, buffer_count=3):
        self.h_cam = ueye.HIDS(device_id)
        self.buffer_count = buffer_count
        self.img_buffers = []
        self.current_fps = None

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

    def alloc(self):
        """
        Allocate memory for futur images.
        """
        # Get camera settings
        rect = self.get_aoi()
        bpp = get_bits_per_pixel(self.get_colormode())
        # Check that already existing buffers are free
        for buff in self.img_buffers:
            check(ueye.is_FreeImageMem(self.h_cam, buff.mem_ptr, buff.mem_id))
        self.img_buffers = []
        # Create asked buffers
        for i in range(self.buffer_count):
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

    def set_fps(self, fps):
        """
        Set the fps.

        Returns
        =======
        fps: number
            Real fps, can be slightly different than the asked one.
        """
        # checking available fps
        mini, maxi = self.get_fps_range()
        if fps < mini:
            print(f'Warning: Specified fps ({fps:.2f}) not in possible range:'
                  f' [{mini:.2f}, {maxi:.2f}].'
                  f' fps has been set to {mini:.2f}.')
            fps = mini
        if fps > maxi:
            print(f'Warning: Specified fps ({fps:.2f}) not in possible range:'
                  f' [{mini:.2f}, {maxi:.2f}].'
                  f' fps has been set to {maxi:.2f}.')
            fps = maxi
        fps = ueye.c_double(fps)
        new_fps = ueye.c_double()
        check(ueye.is_SetFrameRate(self.h_cam, fps, new_fps))
        self.current_fps = float(new_fps)
        return new_fps

    def get_fps(self):
        """
        Get the current fps.

        Returns
        =======
        fps: number
            Current fps.
        """
        if self.current_fps is not None:
            return self.current_fps
        fps = ueye.c_double()
        check(ueye.is_GetFramesPerSecond(self.h_cam, fps))
        return fps

    def get_fps_range(self):
        """
        Get the current fps available range.

        Returns
        =======
        fps_range: 2x1 array
            range of available fps
        """
        mini = ueye.c_double()
        maxi = ueye.c_double()
        interv = ueye.c_double()
        check(ueye.is_GetFrameTimeRange(
                self.h_cam,
                mini, maxi, interv))
        return [float(1/maxi), float(1/mini)]

    def set_pixelclock(self, pixelclock):
        """
        Set the current pixelclock.

        Params
        =======
        pixelclock: number
            Current pixelclock.
        """
        # Warning
        print('Warning: when changing pixelclock at runtime, you may need to '
              'update the fps and exposure parameters')
        # get pixelclock range
        pcrange = (ueye.c_uint*3)()
        check(ueye.is_PixelClock(self.h_cam, ueye.IS_PIXELCLOCK_CMD_GET_RANGE,
                                 pcrange, 12))
        pcmin, pcmax, pcincr = pcrange
        if pixelclock < pcmin:
            pixelclock = pcmin
            print(f"Pixelclock out of range [{pcmin}, {pcmax}] and set "
                  f"to {pcmin}")
        elif pixelclock > pcmax:
            pixelclock = pcmax
            print(f"Pixelclock out of range [{pcmin}, {pcmax}] and set "
                  f"to {pcmax}")
        # Set pixelclock
        pixelclock = ueye.c_uint(pixelclock)
        check(ueye.is_PixelClock(self.h_cam, ueye.IS_PIXELCLOCK_CMD_SET,
                                 pixelclock, 4))

    def get_pixelclock(self):
        """
        Get the current pixelclock.

        Returns
        =======
        pixelclock: number
            Current pixelclock.
        """
        pixelclock = ueye.c_uint()
        check(ueye.is_PixelClock(self.h_cam, ueye.IS_PIXELCLOCK_CMD_GET,
                                 pixelclock, 4))
        return pixelclock

    def set_exposure(self, exposure):
        """
        Set the exposure.

        Returns
        =======
        exposure: number
            Real exposure, can be slightly different than the asked one.
        """
        new_exposure = ueye.c_double(exposure)
        check(ueye.is_Exposure(self.h_cam,
                               ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
                               new_exposure, 8))
        return new_exposure

    def get_exposure(self):
        """
        Get the current exposure.

        Returns
        =======
        exposure: number
            Current exposure.
        """
        exposure = ueye.c_double()
        check(ueye.is_Exposure(self.h_cam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE,
                               exposure,  8))
        return exposure

    def set_exposure_auto(self, toggle):
        """
        Set auto expose to on/off.

        Params
        =======
        toggle: integer
            1 activate the auto gain, 0 deactivate it
        """
        value = ueye.c_double(toggle)
        value_to_return = ueye.c_double()
        check(ueye.is_SetAutoParameter(self.h_cam,
                                       ueye.IS_SET_ENABLE_AUTO_SHUTTER,
                                       value,
                                       value_to_return))

    def set_gain_auto(self, toggle):
        """
        Set/unset auto gain.

        Params
        ======
        toggle: integer
            1 activate the auto gain, 0 deactivate it
        """
        value = ueye.c_double(toggle)
        value_to_return = ueye.c_double()
        check(ueye.is_SetAutoParameter(self.h_cam,
                                       ueye.IS_SET_ENABLE_AUTO_GAIN,
                                       value,
                                       value_to_return))

    def __get_timeout(self):
        fps = self.get_fps()
        if fps == 0:
            fps = 1
        return int(1.5*(1/fps)+1)*1000

    def capture_video(self, wait=False):
        """
        Begin capturing a video.

        Parameters
        ==========
        wait: boolean
           To wait or not for the camera frames (default to False).
        """
        self.alloc()
        wait_param = ueye.IS_WAIT if wait else ueye.IS_DONT_WAIT
        return ueye.is_CaptureVideo(self.h_cam, wait_param)

    def stop_video(self):
        """
        Stop capturing the video.
        """
        return ueye.is_StopLiveVideo(self.h_cam, ueye.IS_FORCE_VIDEO_STOP)

    def capture_image(self, timeout=None):
        if timeout is None:
            timeout = self.__get_timeout()
        self.capture_video()
        img_buffer = ImageBuffer()
        ret = ueye.is_WaitForNextImage(self.handle(),
                                       timeout,
                                       img_buffer.mem_ptr,
                                       img_buffer.mem_id)
        if ret == ueye.IS_SUCCESS:
            imdata = ImageData(self.handle(), img_buffer)
            data = imdata.as_1d_image()
            imdata.unlock()
            self.stop_video()
        else:
            data = None
        return data

    def capture_images(self, nmb, timeout=None):
        if timeout is None:
            timeout = self.__get_timeout()
        self.capture_video()
        ims = []
        for i in range(nmb):
            img_buffer = ImageBuffer()
            ret = ueye.is_WaitForNextImage(self.handle(),
                                           timeout,
                                           img_buffer.mem_ptr,
                                           img_buffer.mem_id)
            if ret == ueye.IS_SUCCESS:
                imdata = ImageData(self.handle(), img_buffer)
                ims.append(imdata.as_1d_image())
                imdata.unlock()
            else:
                print(f"Warning: Missed {i}th frame !")
                ims.append(None)
        self.stop_video()
        return ims

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
