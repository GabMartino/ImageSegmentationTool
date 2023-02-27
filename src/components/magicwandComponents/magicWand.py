from random import random

import numpy as np
import cv2 as cv
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider
from scipy.interpolate import splprep, splev


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



    def saveMask(self, callbackMethod):
        pass




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
        
        point 
    '''
    def createMask(self, img, selected_point, avg_color, std_color):
        self.img = img.copy()
        x, y = selected_point
        tolerance = tuple(std_color)#(self.tolerance,) * 3
        lowerTolerance = (int(np.clip(self.tolerance*tolerance[0], self.tolerance*tolerance[0], avg_color[0])),
                          int(np.clip(self.tolerance*tolerance[1], self.tolerance*tolerance[0], avg_color[1])),
                          int(np.clip(self.tolerance*tolerance[2], self.tolerance*tolerance[0], avg_color[2])))
        upperTolerance = (int(np.clip(self.tolerance*tolerance[0], 0, 255 - avg_color[0])),
                          int(np.clip(self.tolerance*tolerance[1], 0, 255 - avg_color[1])),
                          int(np.clip(self.tolerance*tolerance[2], 0, 255 - avg_color[2])))

        h, w = img.shape[:2]
        self.mask = np.zeros((h, w), dtype=np.uint8) ## Create a mask that is the total and final
        self._flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8) ## create an empty mask that is the temporary mask


        self._flood_mask[:] = 0 ## I dont know why again report zero
        cv.floodFill(
            self.img,
            self._flood_mask,
            (x, y),
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

        return self._update()


    '''
        This method find the countour of the mask (that is a binary image)
        
        There are three arguments in cv.findContours() function, first one is source image, 
        second is contour retrieval mode, third is contour approximation method. And it outputs a modified image, 
        the contours and hierarchy. contours is a Python list of all the contours in the image. Each individual contour 
        is a Numpy array of (x,y) coordinates of boundary points of the object.
    '''
    def _find_exterior_contours(self, mask):
        ## lets filter the mask to eliminate some noise
        #mask = cv.morphologyEx(mask, cv.MORPH_OPEN,cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5)))
        #print(mask)
        contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contour = None
        if len(contours) == 2:
            contour = contours[0]
        elif len(contours) == 3:
            contour = contours[1]
        else:
            raise Exception("Check the signature for `cv.findContours()`.")
        print(contour)
        contour = max(contour, key=cv.contourArea) if len(contour) > 0 else None

        #epsilon = 0.0001 * cv.arcLength(big_contour, True)
        #approx = cv.approxPolyDP(big_contour, epsilon, True)


        return contour

    def _update(self):
        """Updates an image in the already drawn window."""
        viz = self.img.copy()
        contours = self._find_exterior_contours(self.mask) ##find countours of the binary image mask
        print(contours.shape)

        ## Generate random color for the mask
        from random import randrange
        maskColor = (randrange(255), randrange(255), randrange(255))

        '''
            Overlap the mask to the image
        '''
        viz = cv.drawContours(viz, [contours], -1, color=maskColor, thickness=-2)
        viz = cv.addWeighted(self.img, 0.70, viz, 0.30, 0)
        viz = cv.drawContours(viz, [contours], -2, color=maskColor, thickness=1)


        return viz



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