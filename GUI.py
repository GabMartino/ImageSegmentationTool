import os
import pathlib
import sys

import cv2
import hydra
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QImage, QPalette, QIcon, QCursor, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QToolBar, QAction, QGridLayout, \
    QHBoxLayout, QFileDialog, QWidget, QPushButton, QVBoxLayout, QMessageBox, QSizePolicy
from PIL import Image
from matplotlib import pyplot as plt


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



class Window(QMainWindow):
    """Main Window."""
    def __init__(self, width=1024, height=640, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Image Segmentation tool")
        self.setGeometry(100, 100, width, height)

        self.indexImage = None
        self.fileList = None


        self.UIComponents()
        self.createActions()
        self.setupMenus()
        self.show()

    def UIComponents(self):
        ## Widget of the UI
        self.mainWidget = QWidget()

        ## Layout of the main Widget
        layout = QHBoxLayout()

        ## Create Image Viewer and a toolbar
        self.imageViewer = QWidget()
        self.toolbar = QWidget()

        layout.addWidget(self.imageViewer, int(self.width()*0.75))
        layout.addWidget(self.toolbar, int(self.width()*0.25))

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

        self.setupToolbar()
        self.setupImageViewer()



    def setupMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.menuBar().addMenu(self.fileMenu)

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.openFile)


    def createMask(self, info):
        overlay_size, click_pos  = info
        image = self.imageLabel.pixmap().toImage()
        import qimage2ndarray
        image_np = qimage2ndarray.rgb_view(image).copy()
        #cv2.floodFill(image_np, None, seedPoint=click_pos, newVal=(255, 0, 0), loDiff=(5, 5, 5, 5), upDiff=(5, 5, 5, 5))
        #self.maskOverlay

    def activateWand(self, event):
        if self.fileList is not None:
            if self.imageLabel.mousePressCallback == self.createMask:
                self.imageLabel.setMouseReleaseFunctionCallback(None)
                self.imageLabel.setCursor(QCursor(Qt.ArrowCursor))
                print("wand deactivated", self.imageLabel.mousePressEvent)
            else:
                self.imageLabel.setMouseReleaseFunctionCallback(self.createMask)
                self.imageLabel.setCursor(QCursor(Qt.CrossCursor))
                print("wand activated", self.imageLabel.mousePressEvent)


    def setupToolbar(self):

        toolbarLayout = QVBoxLayout()
        self.toolbar.setLayout(toolbarLayout)
        ######################################################
        ############à MAGIC WAND ##################À
        magicWandSpace = QWidget()
        magicWandLayout = QVBoxLayout()
        magicWandSpace.setLayout(magicWandLayout)

        self.magicWandButton= QPushButton()
        qico = QPixmap("resources/magic-wand.png")
        ico = QIcon(qico)
        self.magicWandButton.setIcon(ico)
        self.magicWandButton.setIconSize(qico.rect().size()*0.05)
        self.magicWandButton.setCheckable(True)
        self.magicWandButton.clicked.connect(self.activateWand)

        magicWandLayout.addWidget(self.magicWandButton)

        ########### Image button selector ######################

        buttonsSpace = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsSpace.setLayout(buttonsLayout)

        nextImageButton = QPushButton(self.toolbar)
        nextImageButton.setText("Next")
        nextImageButton.clicked.connect(lambda: self.showImage(increment=True))

        previuousImageButton = QPushButton(self.toolbar)
        previuousImageButton.setText("Previous")
        previuousImageButton.clicked.connect(lambda: self.showImage(increment=False))

        self.imageCounter = QLabel()
        #imageCounter.setText(str(self.indexImage)+"/"+str(len(self.fileList)))
        self.imageCounter.setAlignment(Qt.AlignCenter)


        buttonsLayout.addWidget(previuousImageButton, Qt.AlignLeft)
        buttonsLayout.addWidget(self.imageCounter, Qt.AlignCenter)
        buttonsLayout.addWidget(nextImageButton, Qt.AlignRight)

        ##########################################################ÀÀ
        toolbarLayout.addWidget(magicWandSpace, Qt.AlignTop)
        toolbarLayout.addWidget(buttonsSpace, Qt.AlignBottom)


    def setupImageViewer(self):

        imageViewerLayout = QGridLayout()
        self.imageViewer.setLayout(imageViewerLayout)

        self.imageLabel = CustomImageView()
        #self.imageLabel.setBackgroundRole(QPalette.Base)
        #self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        #self.imageLabel.setScaledContents(True)
        #self.imageLabel.setAlignment(Qt.AlignCenter)
        #self.imageLabel.setText("Open an Image folder to start labeling segments...")
        #self.imageLabel.mousePressEvent = self.openFile ## at first upload images
        self.imageLabel.setMouseReleaseFunctionCallback(self.openFile)
        #painter = QPainter(self)

        imageViewerLayout.addWidget(self.imageLabel)

    def _createActions(self):


        self.openAction = QAction("&Open...", self) ## Create action for open
        self.saveAction = QAction("&Save", self) ## Create action for save

    '''
        In the menuBar we need to open a folder with all the images
    '''
    def _createMenuBar(self):
        menuBar = QMenuBar(self) ## Create a menu bar
        fileMenu = QMenu("&File", self) ## set the name of menu

        fileMenu.addAction(self.openAction) ## Add the openAction in the filemenu
        fileMenu.addAction(self.saveAction) ## Add the saveAction in the filemenu

        menuBar.addMenu(fileMenu)  ## Add the menu in the menu bar
        self.setMenuBar(menuBar)

    def _connectActions(self):
        # Connect File actions
        self.openAction.triggered.connect(self.openFile) ## Connect the action to a method
        self.saveAction.triggered.connect(self.saveFile) ## Connect the action to a method


    def openFile(self, info):
        # Logic for opening an existing file goes here...
        options = QFileDialog.Options()
        dialog = QFileDialog()
        #dialog.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        actualDir = os.getcwd()
        foo_dir = dialog.getExistingDirectory(self, 'Select Images Directory', directory=actualDir, options=options)
        if foo_dir:
            self.actualDirectory = foo_dir
            self.fileList = os.listdir(self.actualDirectory)
            self.fileList = [filename for filename in self.fileList if pathlib.Path(filename).suffix in [".jpeg", ".jpg", ".png", ".gif", ".JPG", ".JPEG"]]
            if len(self.fileList) <= 0:
                QMessageBox.information(self, "Image Viewer", "The selected directory has no valid images.")
                return
            self.indexImage = 0
            self.showImage(firstCall=True)

            self.imageLabel.setMouseReleaseFunctionCallback(None)  ## Removed if already called
        else:
            QMessageBox.information(self, "Image Viewer", "Empty Directory")



    def showImage(self, increment=True, firstCall=False):
        if not firstCall :
            if increment:
                self.indexImage = (self.indexImage + 1) % len(self.fileList)
            else:
                self.indexImage = (self.indexImage - 1) % len(self.fileList)

        filename = self.actualDirectory + "/" + self.fileList[self.indexImage]
        image = QImage(filename)
        if image.isNull():
            QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
            return

        self.imageLabel.setPixmap(QPixmap.fromImage(image))
        self.imageCounter.setText(str(self.indexImage + 1) + "/" + str(len(self.fileList)))


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg):

    app = QApplication(sys.argv)
    win = Window(cfg.window.width, cfg.window.height)
    win.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()