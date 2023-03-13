import cv2
import numpy as np
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPalette, QPainter, QPen, QBrush, QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QSizePolicy, QWidget, QGridLayout
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



    '''
        
            When clicked on the image overlay 
            trigger a callback, setted in 'mousePressedCallback'
            
    '''
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

        pixmap = convert_nparray_to_QPixmap(masks)
        self.setPixmap(pixmap)

        #painter = QPainter(self.pixmap().copy())
        #painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        #painter.drawPixmap()

    '''
        The image should be in QImage type
    '''
    def updateImage(self, image):
        self.setPixmap(QPixmap.fromImage(image).scaled(self.size(), Qt.KeepAspectRatio))

class ImageOverlay(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        layout = QGridLayout()
        self.setLayout(layout)

        self.imageOverlay = CustomImageView()


        guide = QLabel()
        guide.setFixedHeight(35)
        guide.setText("KEEP PRESSED 'SHIFT'/'CTRL' KEY TO ADD/REMOVE AREAS TO THE MASK")

        #self.keyPressedLabel = QLabel()
        #self.keyPressedLabel.setStyleSheet("color: red; padding: 0px 0px 0px 20px ;")
        # keyPressed.setText("TEST")
        guide.setFixedHeight(35)

        layout.addWidget(self.imageOverlay, 0, 0, 1, 2)
        layout.addWidget(guide, 1, 0)
        #layout.addWidget(self.keyPressedLabel, 1, 1) ## label to

        #self.toolbar.magicWand.variableHook = self.keyPressedLabel
        self.show()

    def setMouseReleaseFunctionCallback(self, method):
        self.imageOverlay.setMouseReleaseFunctionCallback(method)

    def updateImage(self, image):
        self.imageOverlay.updateImage(image)