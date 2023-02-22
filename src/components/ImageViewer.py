import cv2
import numpy as np
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPalette, QPainter, QPen, QBrush, QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QSizePolicy
from matplotlib import pyplot as plt

def convert_nparray_to_QPixmap(img):
    w,h,ch = img.shape
    # Convert resulting image to pixmap
    if img.ndim == 1:
        img =  cv2.cvtColor(img,cv2.COLOR_GRAY2RGB)

    qimg = QImage(img.data, h, w, 3*h, QImage.Format_RGB888)
    qpixmap = QPixmap(qimg)

    return qpixmap


# Image View class
class CustomImageView(QLabel):

    # constructor which inherit original
    # ImageView
    def __init__(self):
        super().__init__()
        self.setBackgroundRole(QPalette.Base)
        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.setScaledContents(True)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Open an Image folder to start labeling segments...")

        self.mousePressCallback = None
        self.setUpdatesEnabled(True)

    def setMouseReleaseFunctionCallback(self, method):
        self.mousePressCallback = method


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressPos = event.pos()

    def mouseReleaseEvent(self, event):
        # ensure that the left button was pressed *and* released within the
        # geometry of the widget; if so, emit the signal;
        if (self.pressPos is not None and
                event.button() == Qt.LeftButton and
                event.pos() in self.rect()):
            if self.mousePressCallback is not None:
                info = (self.rect().size(), event.pos())
                self.mousePressCallback(info)
        self.pressPos = None


    def drawSegment(self, masks):
        print(masks.shape)
        pixmap = convert_nparray_to_QPixmap(masks)
        self.setPixmap(pixmap)

        #painter = QPainter(self.pixmap().copy())
        #painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        #painter.drawPixmap()