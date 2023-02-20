import os
import sys

import hydra
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QPixmap, QImage, QPalette
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QToolBar, QAction, QGridLayout, \
    QHBoxLayout, QFileDialog, QWidget, QPushButton, QVBoxLayout, QMessageBox, QSizePolicy
from PIL import Image

# Image View class
class CustomImageView(QWidget):

    # constructor which inherit original
    # ImageView
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressPos = event.pos()

    def mouseReleaseEvent(self, event):
        # ensure that the left button was pressed *and* released within the
        # geometry of the widget; if so, emit the signal;
        if (self.pressPos is not None and
                event.button() == Qt.LeftButton and
                event.pos() in self.rect()):
            self.clicked.emit()
        self.pressPos = None


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, width=1024, height=640, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Image Segmentation tool")
        self.setGeometry(100, 100, width, height)

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

    def setupToolbar(self):

        toolbarLayout = QVBoxLayout()
        self.toolbar.setLayout(toolbarLayout)
        ######################################################à
        ########### Image button selector ######################


        buttonsSpace = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsSpace.setLayout(buttonsLayout)

        nextImageButton = QPushButton(self.toolbar)
        nextImageButton.setText("Next")

        previuousImageButton = QPushButton(self.toolbar)
        previuousImageButton.setText("Previous")

        imageCounter = QLabel()
        imageCounter.setText("1/N")
        imageCounter.setAlignment(Qt.AlignCenter)


        buttonsLayout.addWidget(nextImageButton, Qt.AlignRight)
        buttonsLayout.addWidget(imageCounter, Qt.AlignCenter)
        buttonsLayout.addWidget(previuousImageButton, Qt.AlignLeft)

        ##########################################################ÀÀ
        toolbarLayout.addWidget(buttonsSpace, Qt.AlignBottom)


    def setupImageViewer(self):

        imageViewerLayout = QGridLayout()
        self.imageViewer.setLayout(imageViewerLayout)


        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        self.imageLabel.setAlignment(Qt.AlignCenter)
        self.imageLabel.setText("Open an Image folder to start labeling segments...")

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


    def openFile(self):
        # Logic for opening an existing file goes here...

        options = QFileDialog.Options()
        dialog = QFileDialog()
        #dialog.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        foo_dir = dialog.getExistingDirectory(self, 'Select Image Directory', "./", options=options)

        self.actualDirectory = foo_dir
        self.fileList = os.listdir(self.actualDirectory)
        self.indexImage = 0
        self.showImage(firstCall=True)



    def showImage(self, increment=True, firstCall=False):
        if not firstCall:
            if increment:
                self.indexImage = (self.indexImage + 1)//len(self.fileList)
            else:
                self.indexImage = (self.indexImage - 1) // len(self.fileList)

        filename = self.actualDirectory + "/" + self.fileList[self.indexImage]
        image = QImage(filename)
        print(image, filename)
        if image.isNull():
            QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
            return

        self.imageLabel.setPixmap(QPixmap.fromImage(image))




    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.pressPos = event.pos()

    def mouseReleaseEvent(self, event):
        # ensure that the left button was pressed *and* released within the
        # geometry of the widget; if so, emit the signal;
        if (self.pressPos is not None and
                event.button() == Qt.LeftButton and
                event.pos() in self.rect()):
            self.clicked.emit()
        self.pressPos = None


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg):

    app = QApplication(sys.argv)
    win = Window(cfg.window.width, cfg.window.height)
    win.show()
    sys.exit(app.exec_())
if __name__ == "__main__":
    main()