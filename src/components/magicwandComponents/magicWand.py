import numpy as np
import cv2 as cv
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider


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

    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMinimum(1)
        self.slider.setMaximum(150)
        self.slider.setTickPosition(10)
        self.slider.setFixedSize(200, 20)

        labels = QWidget()

        slider_hbox = QHBoxLayout()
        labels.setLayout(slider_hbox)
        slider_hbox.setContentsMargins(0, 0, 0, 0)

        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText(str(self.slider.minimum()))
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText(str(self.slider.maximum()))

        slider_hbox.addWidget(label_minimum, Qt.AlignLeft)
        slider_hbox.addWidget(label_maximum, Qt.AlignRight)

        layout.addWidget(self.slider)
        layout.addWidget(labels)

    def setValueChangedCallback(self, method):
        self.slider.valueChanged.connect(method)



SHIFT_KEY = cv.EVENT_FLAG_SHIFTKEY
ALT_KEY = cv.EVENT_FLAG_ALTKEY

def _find_exterior_contours(img):
    ret = cv.findContours(img, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(ret) == 2:
        return ret[0]
    elif len(ret) == 3:
        return ret[1]
    raise Exception("Check the signature for `cv.findContours()`.")


class MagicWand(QWidget):

    def __init__(self):
        super().__init__()
        self.magicWandRadius = 10
        self.connectivity = 4
        self.tolerance = 32

        self._flood_fill_flags = (
                self.connectivity | cv.FLOODFILL_FIXED_RANGE | cv.FLOODFILL_MASK_ONLY | 255 << 8
        )
        self.setup()
        self.show()


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

        self.slider = MagicWandSlider()



        mainLayout.addWidget(self.wandSet)
        mainLayout.addWidget(self.slider)


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
    def createMask(self, img, selected_point):
        self.img = img
        x, y = selected_point
        tolerance = (self.tolerance,) * 3

        h, w = img.shape[:2]
        self.mask = np.zeros((h, w), dtype=np.uint8)
        self._flood_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)


        self._flood_mask[:] = 0
        cv.floodFill(
            self.img,
            self._flood_mask,
            (x, y),
            0,
            tolerance,
            tolerance,
            self._flood_fill_flags,
        )

        modifier = (ALT_KEY + SHIFT_KEY)

        flood_mask = self._flood_mask[1:-1, 1:-1].copy()
        if modifier == (ALT_KEY + SHIFT_KEY):
            self.mask = cv.bitwise_and(self.mask, flood_mask)
        elif modifier == SHIFT_KEY:
            self.mask = cv.bitwise_or(self.mask, flood_mask)
        elif modifier == ALT_KEY:
            self.mask = cv.bitwise_and(self.mask, cv.bitwise_not(flood_mask))
        else:
            print("ok")
        self.mask = flood_mask

        return self._update()
    def _update(self):
        """Updates an image in the already drawn window."""
        viz = self.img.copy()
        contours = _find_exterior_contours(self.mask)
        viz = cv.drawContours(viz, contours, -1, color=(255,) * 3, thickness=-1)
        viz = cv.addWeighted(self.img, 0.75, viz, 0.25, 0)
        viz = cv.drawContours(viz, contours, -1, color=(255,) * 3, thickness=1)
        return viz
        '''
        
        self.mean, self.stddev = cv.meanStdDev(self.img, mask=self.mask)
        meanstr = "mean=({:.2f}, {:.2f}, {:.2f})".format(*self.mean[:, 0])
        stdstr = "std=({:.2f}, {:.2f}, {:.2f})".format(*self.stddev[:, 0])
        cv.imshow(self.name, viz)
        cv.displayStatusBar(self.name, ", ".join((meanstr, stdstr)))

        '''

        ## TODO: avoid selecting part already selected
        ## TODO: save mask of selected part
        ## TODO: adding mask in the table
