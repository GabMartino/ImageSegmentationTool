from random import random

import numpy as np
import cv2 as cv
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from scipy.interpolate import splprep, splev

from SegmentationLabeling.src.utils.utils import drawMaskOnImage


class MagicWandButton(QPushButton):

    def __init__(self, ico_path):
        super().__init__()
        self.ico_path = ico_path
        self.setup()
        self.show()
    def setup(self):
        qico = QPixmap(self.ico_path)
        ico = QIcon(qico)
        self.setIcon(ico)

        self.setFixedSize(QSize(40, 40))
        self.setIconSize(QSize(20, 20))
        self.setCheckable(True)

    def setClickCallback(self, method):
        self.clicked.connect(method)

class ColorPreview(QLabel):

    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.setFixedSize(40, 40)
        self.setStyleSheet("border: 2px solid black")


class ColorLabel(QLabel):

    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.setFixedSize(QSize(100, 30))


class MagicWandSlider(QWidget):

    def __init__(self, startPosition, title, min, max, tick=1.):
        super().__init__()
        self.title = title
        self.min = min
        self.max = max
        self.tick = tick

        self.setup(startPosition)

    def updateCurrentSliderPositionLabel(self):
        self.label_current.setText(str(self.slider.sliderPosition()))
    def setup(self, startPosition):

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMinimum(self.min)
        self.slider.setMaximum(self.max)
        #self.slider.setTickPosition(10)
        self.slider.setTickInterval(self.tick)
        self.slider.setSliderPosition(startPosition)
        self.slider.valueChanged.connect(self.updateCurrentSliderPositionLabel)
        #self.slider.setFixedSize(200, 20)
        #self.slider.set

        labels = QWidget()

        slider_hbox = QHBoxLayout()
        labels.setLayout(slider_hbox)
        slider_hbox.setContentsMargins(0, 5, 0, 0)

        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText(str(self.slider.minimum()))
        self.label_current = QLabel(alignment=Qt.AlignCenter)
        self.label_current.setText(str(self.slider.sliderPosition()))
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText(str(self.slider.maximum()))

        slider_hbox.addWidget(label_minimum, Qt.AlignLeft)
        slider_hbox.addWidget(self.label_current, Qt.AlignCenter)
        slider_hbox.addWidget(label_maximum, Qt.AlignRight)

        label = QLabel()
        label.setText(self.title)
        layout.addWidget(label)
        layout.addWidget(self.slider)
        layout.addWidget(labels)

    def setValueChangedCallback(self, method):
        self.slider.valueChanged.connect(method)



class MagicWand(QWidget):

    def __init__(self):
        super().__init__()
        self.magicWandRadius = 10
        self.connectivity = 4
        self.tolerance = 1
        self.modifier = None
        self._flood_fill_flags = (
                self.connectivity | cv.FLOODFILL_FIXED_RANGE | cv.FLOODFILL_MASK_ONLY | 255 << 8
        )

        self.variableHook = None
        self.setup()
        self.show()

    def updateTolerance(self):
        self.tolerance = self.toleranceSlider.slider.sliderPosition()/10

    def setup(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.wandSet = QWidget()

        lineLayout = QHBoxLayout()
        self.wandSet.setLayout(lineLayout)

        self.button = MagicWandButton("resources/magic-wand.png")
        self.colorSelected = ColorPreview()
        self.colorLabel = ColorLabel()

        lineLayout.addWidget(self.button)
        lineLayout.addWidget(self.colorSelected)
        lineLayout.addWidget(self.colorLabel)

        self.slider = MagicWandSlider(self.magicWandRadius, "MagicWand Size", 1, 150 )
        self.toleranceSlider = MagicWandSlider(self.tolerance, "MagicWand Tolerance", 1, 50)
        self.toleranceSlider.setValueChangedCallback(self.updateTolerance)



        mainLayout.addWidget(self.wandSet)
        mainLayout.addWidget(self.slider)
        mainLayout.addWidget(self.toleranceSlider)


    def setViewedColor(self, color):
        if color is not None:
            r, g, b = color
            palette = QPalette()
            palette.setColor(self.colorSelected.backgroundRole(), QColor(r, g, b))
            self.colorSelected.setAutoFillBackground(True)
            self.colorSelected.setPalette(palette)

            def rgb_to_hex(r, g, b):
                return '#{:02x}{:02x}{:02x}'.format(r, g, b)

            colorText = "(" + str(r) + ", " + str(g) + ", " + str(b) + ")\n"
            colorText += rgb_to_hex(r, g, b)
            self.colorLabel.setText(colorText)
        else:
            self.colorLabel.setText("Unselected Color")

    def getMask(self):
        return self.mask


    '''
        This method create a mask from a selected point in the 2D space of the image (x,y) and the image itself
        Let's consider a selected point with r, g, b
        and a standard deviation of x, y, z so the lower and upper tolerance will be
        
            r - std_r <= ri <= r + std_r
            
        but also 
                0 <= r_i <= 255
            
        so
            std_r = r
            std_r = 255 - r
        
        point out that the axis of the image are inverted (width, height, 3)
        
    '''
    def createMask(self, img, selected_point, avg_color, std_color, temporary_mask=None):
        self.img = img.copy()
        x, y = selected_point
        tolerance = tuple(std_color)#(self.tolerance,) * 3
        lowerTolerance = (int(np.clip(self.tolerance*tolerance[0], self.tolerance*tolerance[0], avg_color[0])),
                          int(np.clip(self.tolerance*tolerance[1], self.tolerance*tolerance[0], avg_color[1])),
                          int(np.clip(self.tolerance*tolerance[2], self.tolerance*tolerance[0], avg_color[2])))
        upperTolerance = (int(np.clip(self.tolerance*tolerance[0], 0, 255 - avg_color[0])),
                          int(np.clip(self.tolerance*tolerance[1], 0, 255 - avg_color[1])),
                          int(np.clip(self.tolerance*tolerance[2], 0, 255 - avg_color[2])))

        w, h = img.shape[:2]
        self.mask = np.zeros((w, h), dtype=np.uint8) if temporary_mask is None else temporary_mask ## Create a mask that is the total and final
        self._flood_mask = np.zeros((w + 2, h + 2), dtype=np.uint8) ## create an empty mask that is the temporary mask


        self._flood_mask[:] = 0 ## I dont know why again report zero
        cv.floodFill(
            self.img,
            self._flood_mask,
            (y, x),
            0,
            lowerTolerance,
            upperTolerance,
            self._flood_fill_flags,
        )

        flood_mask = self._flood_mask[1:-1, 1:-1].copy() ## make a copy removing 2 pixels
        if self.modifier == "SHIFT": ## ADD AREAS TO MASK
            self.mask = cv.bitwise_or(self.mask, flood_mask) ## if the shift is press "ADD" the last mask with the new one

        elif self.modifier == "CTRL": ## REMOVE AREAS TO MASK
            self.mask = cv.bitwise_and(self.mask, cv.bitwise_not(flood_mask)) ## if ALT is pressed make the AND with NOT of the new new mask -> delete part

        else:
            self.mask = flood_mask ## otherwise simply overwrite

        return drawMaskOnImage(self.img, self.mask)



    def keyPressEvent(self, event):

        if event.isAutoRepeat():
            return

        if event.key() == QtCore.Qt.Key_Shift:
            self.modifier = "SHIFT"
            self.variableHook.setText("SHIFT PRESSED")
        elif event.key() == QtCore.Qt.Key_Control:
            self.modifier = "CTRL"
            self.variableHook.setText("CTRL PRESSED")


        event.accept()

    def keyReleaseEvent(self, event):

       # if event.isAutoRepeat():
        #    return
        self.modifier = None
        self.variableHook.setText("")