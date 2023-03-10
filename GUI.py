import os
import pathlib
import sys

import hydra
import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QCursor
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QAction, QGridLayout, \
    QHBoxLayout, QFileDialog, QWidget, QMessageBox

from SegmentationLabeling.src.components.ImagePreview.ImageViewer import CustomImageView
from SegmentationLabeling.src.components.Toolbar.Toolbar import Toolbar


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, width=1024, height=640, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle("Image Segmentation tool")
        self.setGeometry(100, 100, width, height)

        self.indexImage = None
        self.fileList = None
        self.actualQImage = None

        self.temp_mask = None

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
        self.toolbar = Toolbar()

        layout.addWidget(self.imageViewer, int(self.width()*0.75))
        layout.addWidget(self.toolbar, int(self.width()*0.25))

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)


        self.setupImageViewer()
        self.setupToolbar()

        self.masks = {}



    def setupMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.menuBar().addMenu(self.fileMenu)

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.openFile)


    def createMask(self, info):


        def findAverageColorInRoundArea(image, center, radius):
            x, y = center
            square_patch = image[x - radius:x + radius, y - radius: y + radius]
            ## TODO: implement round patch
            square_patch = square_patch.reshape((square_patch.shape[0]*square_patch.shape[1], square_patch.shape[2]))
            averageColor = np.mean(square_patch, axis=0).astype(int) if np.any(square_patch) else None
            stds_colors = np.std(square_patch, axis=0).astype(int) if np.any(square_patch) else None
            return averageColor, stds_colors



        image = self.actualQImage ## RealImage with actual size
        overlay_size, click_pos = info ## Overlay size and click position on the overlay
        realSize_image = image.size() ## Real image size

        scaled_image = image.scaled(overlay_size) ## image scaled in the size of the overlay to work easily
        import qimage2ndarray
        scaled_image_np = qimage2ndarray.rgb_view(scaled_image).copy()
        scaled_image_np = np.swapaxes(scaled_image_np, 0, 1)
        x, y = click_pos.x(), click_pos.y()
        print(scaled_image_np.shape, x, y)


        '''
            Get radius, average color, standard deviation
            
        '''
        radius = self.toolbar.magicWand.magicWandRadius
        averageColor, stds_colors = findAverageColorInRoundArea(scaled_image_np, (x, y), radius)
        self.toolbar.magicWand.setViewedColor(averageColor)
        '''
            Create the mask from the pixel clicked.
            Parameters:
            - Scaled image: to speed up the mask finding
            - (x,y) coordinates of the click point on the scaled image
            - 
    
        '''
        image_masked, countours, self.temp_mask = self.toolbar.magicWand.createMask(scaled_image_np, (x, y), averageColor, stds_colors, self.temp_mask )
        image_masked = np.swapaxes(image_masked, 1, 0)
        print("oook", image_masked, countours, self.temp_mask)
        q_im = qimage2ndarray.array2qimage(image_masked)
        self.imageOverlay.setPixmap(QPixmap(q_im))

    def setWandCursor(self):
        # 1. Set the cursor map
        cursor_pix = QPixmap("./resources/circle-icon.png")
        # 2. Scale textures
        cursor_scaled_pix = cursor_pix.scaled(QSize(self.toolbar.magicWand.magicWandRadius, self.toolbar.magicWand.magicWandRadius), Qt.KeepAspectRatio)

        # 3. Set cursor style and cursor focus position
        current_cursor = QCursor(cursor_scaled_pix, -1, -1)
        self.imageOverlay.setCursor(current_cursor)

    def activateWand(self, event):
        if self.fileList is not None:
            if self.imageOverlay.mousePressCallback == self.createMask:
                self.imageOverlay.setMouseReleaseFunctionCallback(None)
                self.imageOverlay.setCursor(QCursor(Qt.ArrowCursor))
                self.toolbar.magicWand.button.setChecked(False)
            else:
                self.imageOverlay.setMouseReleaseFunctionCallback(self.createMask)
                self.setWandCursor()
                self.toolbar.magicWand.button.setChecked(True)
        else:
            self.toolbar.magicWand.button.setChecked(False)


    def updateMagicWandSize(self, value):
        self.toolbar.magicWand.magicWandRadius = value
        self.setWandCursor() if self.fileList is not None else None


    def setupToolbar(self):


        self.toolbar.magicWand.button.setClickCallback(self.activateWand)
        self.toolbar.magicWand.slider.setValueChangedCallback(self.updateMagicWandSize)

        self.toolbar.imageSelector.nextImageButton.clicked.connect(lambda: self.showImage(increment=True))
        self.toolbar.imageSelector.previuousImageButton.clicked.connect(lambda: self.showImage(increment=False))


    def setupImageViewer(self):

        imageViewerLayout = QGridLayout()
        self.imageViewer.setLayout(imageViewerLayout)

        self.imageOverlay = CustomImageView()
        self.imageOverlay.setMouseReleaseFunctionCallback(self.openFile)

        guide = QLabel()
        guide.setFixedHeight(35)
        guide.setText("KEEP PRESSED 'SHIT'/'CTRL' KEY TO ADD/REMOVE AREAS TO THE MASK")

        self.keyPressed = QLabel()
        self.keyPressed.setStyleSheet("color: red; padding: 0px 0px 0px 20px ;")
        #keyPressed.setText("TEST")
        guide.setFixedHeight(35)

        imageViewerLayout.addWidget(self.imageOverlay, 0, 0, 1, 2)
        imageViewerLayout.addWidget(guide, 1, 0)
        imageViewerLayout.addWidget(self.keyPressed, 1, 1)

        self.toolbar.magicWand.variableHook = self.keyPressed


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
        dialog = QFileDialog()
        actualDir = "/home/gabriele/Desktop/Barilla/Datasets/wheat-leaf-kaggle/archive/wheat_leaf/" #os.getcwd()

        foo_dir = dialog.getExistingDirectory(self, 'Select Images Directory', directory=actualDir, options=QFileDialog.DontUseNativeDialog)
        if foo_dir:
            self.actualDirectory = foo_dir
            self.fileList = os.listdir(self.actualDirectory)
            self.fileList = [filename for filename in self.fileList if pathlib.Path(filename).suffix in [".jpeg", ".jpg", ".png", ".gif", ".JPG", ".JPEG"]]
            if len(self.fileList) <= 0:
                QMessageBox.information(self, "Image Viewer", "The selected directory has no valid images.")
                return
            self.indexImage = 0
            self.showImage(firstCall=True)

            self.imageOverlay.setMouseReleaseFunctionCallback(None)  ## Removed if already called
        else:
            QMessageBox.information(self, "Image Viewer", "Empty Directory")



    def showImage(self, increment=True, firstCall=False):
        if self.fileList:
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

            self.actualQImage = image
            self.imageOverlay.setPixmap(QPixmap.fromImage(image).scaled(self.imageOverlay.size(), Qt.KeepAspectRatio))
            self.toolbar.imageSelector.imageCounter.setText(str(self.indexImage + 1) + "/" + str(len(self.fileList)))


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg):

    app = QApplication(sys.argv)
    win = Window(cfg.window.width, cfg.window.height)
    screenGeometry = app.desktop().screenGeometry()
    x = int((screenGeometry.width() - win.width())/ 2)
    y = int((screenGeometry.height() -win.height()) / 2)
    win.move(x, y)


    win.show()
    sys.exit(app.exec_())



if __name__ == "__main__":
    main()