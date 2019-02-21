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

"""  """

__author__ = "Gaby Launay"
__copyright__ = "Gaby Launay 2017"
__credits__ = ""
__license__ = "GPL3"
__version__ = ""
__email__ = "gaby.launay@tutanota.com"
__status__ = "Development"

import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui


class CircleDetector(object):
    def __init__(self, nmb_circ, min_dist=100, damp=0.1):
        """

        """
        self.nmb_circ = nmb_circ
        self.dp_damp = damp
        try:
            nmb_circ[0]
        except TypeError:
            self.nmb_circ = [nmb_circ, nmb_circ]
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
            fact = (1.0 + self.dp_damp*.1)
            self.dp *= fact
            #print(f"No circles, increasing dp from {self.dp} to {self.dp / fact}")
        elif len(circles[0]) < self.nmb_circ[0]:
            fact = len(circles[0])/np.mean(self.nmb_circ)
            fact = 1 + (fact - 1)*self.dp_damp
            #print(f"Increasing dp from {self.dp} to {self.dp / fact}")
            self.dp /= fact
        elif len(circles[0]) > self.nmb_circ[1]:
            fact = len(circles[0])/np.mean(self.nmb_circ)
            fact = 1 + (fact - 1)*self.dp_damp
            #print(f"Decreasing dp from {self.dp} to {self.dp / fact}")
            self.dp /= fact
        else:
            #print(f"dp ok at {self.dp}")
            pass
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
            ind0 = len(self.xy_center) - 20
            if ind0 < 0:
                ind0 = 0
            for i in np.arange(ind0, len(self.xy_center) - 1):
                cv2.circle(image, tuple(self.xy_center[i]),
                           2, (200, 0, 0), 4)
        # Return the image to Qt for display
        return QtGui.QImage(image.data,
                            image_data.mem_info.width,
                            image_data.mem_info.height,
                            QtGui.QImage.Format_RGB888)
