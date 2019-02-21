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


from PyQt5 import QtCore
from PyQt5 import QtWidgets, QtGui
from pyueye import ueye


def get_qt_format(ueye_color_format):
    color_formats = {ueye.IS_CM_SENSOR_RAW8: QtGui.QImage.Format_Mono,
                     ueye.IS_CM_MONO8: QtGui.QImage.Format_Mono,
                     ueye.IS_CM_RGB8_PACKED: QtGui.QImage.Format_RGB888,
                     ueye.IS_CM_BGR8_PACKED: QtGui.QImage.Format_RGB888,
                     ueye.IS_CM_RGBA8_PACKED: QtGui.QImage.Format_RGB32,
                     ueye.IS_CM_BGRA8_PACKED: QtGui.QImage.Format_RGB32}
    return color_formats[ueye_color_format]


class PyuEyeQtView(QtWidgets.QWidget):

    update_signal = QtCore.pyqtSignal(QtGui.QImage, name="update_signal")

    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.image = None
        self.graphics_view = QtWidgets.QGraphicsView(self)
        self.v_layout = QtWidgets.QVBoxLayout(self)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.scene = QtWidgets.QGraphicsScene()
        self.graphics_view.setScene(self.scene)
        self.v_layout.addWidget(self.graphics_view)
        self.scene.drawBackground = self.draw_background
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.update_signal.connect(self.update_image)
        self.processors = []
        self.resize(640, 512)
        self.v_layout.addLayout(self.h_layout)
        self.setLayout(self.v_layout)

    # def on_update_canny_1_slider(self, value):
    #     pass  # print(value)

    # def on_update_canny_2_slider(self, value):
    #     pass  # print(value)

    def draw_background(self, painter, rect):
        if self.image:
            image = self.image.scaled(rect.width(), rect.height(),
                                      QtCore.Qt.KeepAspectRatio)
            painter.drawImage(rect.x(), rect.y(), image)

    def update_image(self, image):
        self.scene.update()

    def user_callback(self, image_data):
        return image_data.as_cv_image()

    def handle(self, image_data):
        self.image = self.user_callback(image_data)
        self.update_signal.emit(self.image)
        # unlock the buffer so we can use it again
        image_data.unlock()

    def shutdown(self):
        self.close()

    def add_processor(self, callback):
        self.processors.append(callback)


class PyuEyeQtApp:
    def __init__(self, args=[]):
        self.qt_app = QtWidgets.QApplication(args)

    def exec_(self):
        self.qt_app.exec_()

    def exit_connect(self, method):
        self.qt_app.aboutToQuit.connect(method)
