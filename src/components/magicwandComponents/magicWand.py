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

    def __init__(self, startPosition, title):
        super().__init__()
        self.title = title
        self.setup(startPosition)

    def updateCurrentSliderPositionLabel(self):
        self.label_current.setText(str(self.slider.sliderPosition()))
    def setup(self, startPosition):

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMinimum(1)
        self.slider.setMaximum(150)
        self.slider.setTickPosition(10)
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

SHIFT_KEY = cv.EVENT_FLAG_SHIFTKEY
ALT_KEY = cv.EVENT_FLAG_ALTKEY




class MagicWand(QWidget):

    def __init__(self):
        super().__init__()

        self.magicWandRadius = 10
        self.connectivity = 4
        self.tolerance = 32
        self.modifier = None
        self._flood_fill_flags = (
                self.connectivity | cv.FLOODFILL_FIXED_RANGE | cv.FLOODFILL_MASK_ONLY | 255 << 8
        )
        self.setup()
        self.show()

    def updateTolerance(self):
        self.tolerance = self.toleranceSlider.slider.sliderPosition()

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

        self.slider = MagicWandSlider(self.magicWandRadius, "MagicWand Size" )
        self.toleranceSlider = MagicWandSlider(self.tolerance, "MagicWand Tolerance")
        self.toleranceSlider.setValueChangedCallback(self.updateTolerance)


        mainLayout.addWidget(self.wandSet)
        mainLayout.addWidget(self.slider)
        mainLayout.addWidget(self.toleranceSlider)


    def setViewedColor(self, color):
        if color is not None:
            r, g, b = color
            print(color)
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
        
    '''
    def createMask(self, img, selected_point):
        self.img = img
        x, y = selected_point
        tolerance = (self.tolerance,) * 3

        h, w = img.shape[:2]
        self.mask = np.zeros((h, w), dtype=np.uint8) ## Create a mask that is the total and final
        self._flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8) ## create an empty mask that is the temporary mask


        self._flood_mask[:] = 0 ## I dont know why again report zero
        cv.floodFill(
            self.img,
            self._flood_mask,
            (x, y),
            0,
            tolerance,
            tolerance,
            self._flood_fill_flags,
        )

        flood_mask = self._flood_mask[1:-1, 1:-1].copy() ## make a copy removing 2 pixels
        if self.modifier == "SHIFT":
            self.mask = cv.bitwise_or(self.mask, flood_mask) ## if the shift is press "ADD" the last mask with the new one
        elif self.modifier == "ALT":
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
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN,cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5)))
        print(mask)
        contours = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        contour = contours[0] if len(contours) == 2 else contours[1]
        big_contour = max(contour, key=cv.contourArea)

        epsilon = 0.0001 * cv.arcLength(big_contour, True)
        approx = cv.approxPolyDP(big_contour, epsilon, True)


        return approx

    def _update(self):
        """Updates an image in the already drawn window."""
        viz = self.img.copy()
        contours = self._find_exterior_contours(self.mask) ##find countours of the binary image mask
        #print(contours.shape)
        viz = cv.drawContours(viz, [contours], -1, color=(255,) * 3, thickness=-1)
        viz = cv.addWeighted(self.img, 0.75, viz, 0.25, 0)
        viz = cv.drawContours(viz, [contours], -2, color=(255,) * 3, thickness=1)
        return viz


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Shift:
            self.modifier = "SHIFT"
        elif event.key() == QtCore.Qt.Key_Alt:
            self.modifier = "ALT"

        event.accept()