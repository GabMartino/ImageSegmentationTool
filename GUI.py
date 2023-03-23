import os
import pathlib
import sys

import hydra
import numpy as np
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QImage, QCursor
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenuBar, QMenu, QAction, QGridLayout, \
    QHBoxLayout, QFileDialog, QWidget, QMessageBox

from SegmentationLabeling.src.components.ImagePreview.ImageViewer import CustomImageView, ImageOverlay
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
        self.imageViewer = ImageOverlay()
        self.toolbar = Toolbar()

        layout.addWidget(self.imageViewer, int(self.width() * 0.75))
        layout.addWidget(self.toolbar, int(self.width() * 0.25))

        self.mainWidget.setLayout(layout)
        self.setCentralWidget(self.mainWidget)

        # self.setupImageViewer()
        #self.setupToolbar()
        self.setupAllEventHandlers()

        self.masks = {}

    ###########################################################################à

    #                           SETUP MENU FUNCTIONS
    #
    ###########################################################################

    def setupMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.menuBar().addMenu(self.fileMenu)

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.openImageFolder)

    ###########################################################################################
    '''
    
    def createMask(self, info):

        def findAverageColorInRoundArea(image, center, radius):
            x, y = center
            square_patch = image[x - radius:x + radius, y - radius: y + radius]
            ## TODO: implement round patch
            square_patch = square_patch.reshape((square_patch.shape[0] * square_patch.shape[1], square_patch.shape[2]))
            averageColor = np.mean(square_patch, axis=0).astype(int) if np.any(square_patch) else None
            stds_colors = np.std(square_patch, axis=0).astype(int) if np.any(square_patch) else None
            return averageColor, stds_colors

        image = self.actualQImage  ## RealImage with actual size
        overlay_size, click_pos = info  ## Overlay size and click position on the overlay
        realSize_image = image.size()  ## Real image size

        scaled_image = image.scaled(overlay_size)  ## image scaled in the size of the overlay to work easily
        import qimage2ndarray
        scaled_image_np = qimage2ndarray.rgb_view(scaled_image).copy()
        scaled_image_np = np.swapaxes(scaled_image_np, 0, 1)
        x, y = click_pos.x(), click_pos.y()
        print(scaled_image_np.shape, x, y)

        radius = self.toolbar.magicWand.magicWandRadius
        averageColor, stds_colors = findAverageColorInRoundArea(scaled_image_np, (x, y), radius)
        self.toolbar.magicWand.setViewedColor(averageColor)
        
            Create the mask from the pixel clicked.
            Parameters:
            - Scaled image: to speed up the mask finding
            - (x,y) coordinates of the click point on the scaled image
            - 
    
        image_masked, countours, self.temp_mask = self.toolbar.magicWand.createMask(scaled_image_np, (x, y),
                                                                                    averageColor, stds_colors,
                                                                                    self.temp_mask)
        image_masked = np.swapaxes(image_masked, 1, 0)
        print("oook", image_masked, countours, self.temp_mask)
        q_im = qimage2ndarray.array2qimage(image_masked)
        self.imageOverlay.setPixmap(QPixmap(q_im))
        
    
    '''

    def setupAllEventHandlers(self):
        '''
            At the startup of the application the first trigger clicking the interface is to open a folder
        '''
        self.imageViewer.setMouseReleaseFunctionCallback(self.openImageFolder)
        self.toolbar.magicWand.setOverlayCursorHook(self.imageViewer.imageOverlay) ##set which overlay should affect the changing of the cursor of the magic wand
        self.toolbar.masktable.setOverlayCursorHook(self.imageViewer.imageOverlay)
        self.toolbar.imageSelector.setMaskTableHook(self.toolbar.masktable)
    #######################################################################################
    ##
    ##                 SCROLLER AND VISUALIZERS METHODS
    ##
    ######################################################################################àà

    ''''
        This method allow the selection of the folder with the images that have to be masked.
    '''

    def openImageFolder(self, info):
        # Logic for opening an existing file goes here...
        dialog = QFileDialog()
        actualDir = "/home/gabriele/Desktop/Barilla/Datasets/wheat-leaf-kaggle/archive/wheat_leaf/"  # TO BE REMOVED AFTER TESTING PHASE

        foo_dir = dialog.getExistingDirectory(self, 'Select Images Directory', directory=actualDir,
                                              options=QFileDialog.DontUseNativeDialog)
        if foo_dir:
            self.actualDirectory = foo_dir  ## set the actual directory

            '''
                Get the file list of the folder
            '''
            self.fileList = os.listdir(self.actualDirectory)
            self.fileList = [filename for filename in self.fileList if
                             pathlib.Path(filename).suffix in [".jpeg", ".jpg", ".png", ".gif", ".JPG", ".JPEG"]]

            if len(self.fileList) <= 0:
                QMessageBox.information(self, "Image Viewer", "The selected directory has no valid images.")
                return

            '''
                Set the first index of the first image
            '''
            self.showImage(0)
            self.toolbar.masktable.setActualImage(0)
            '''
                IF a folder has been open remove this method on click
                because the overlay would eventually been clicked by the magic wand
            '''
            self.imageViewer.setMouseReleaseFunctionCallback(None)
            self.toolbar.imageSelector.setSize(len(self.fileList))  ## This will activate the counter
            self.toolbar.imageSelector.setCallbackForGoNext(self.showImage)
            self.toolbar.imageSelector.setCallbackForGoPrevious(self.showImage)
            self.toolbar.magicWand.activateWand()
        else:
            QMessageBox.information(self, "Image Viewer", "Empty Directory")

    '''
        This method is called whenever the next/previous button is pressed.
        This is used as callaback function
    
    '''

    def showImage(self, imageIndex):

        if self.fileList:  ## if the file list is not empty

            filename = self.actualDirectory + "/" + self.fileList[imageIndex]
            image = QImage(filename)
            if image.isNull():
                QMessageBox.information(self, "Image Viewer", "Cannot load %s." % filename)
                return

            self.actualQImage = image
            self.imageViewer.updateImage(image)


@hydra.main(version_base=None, config_path="config", config_name="config")
def main(cfg):
    app = QApplication(sys.argv)
    win = Window(cfg.window.width, cfg.window.height)
    screenGeometry = app.desktop().screenGeometry()
    x = int((screenGeometry.width() - win.width()) / 2)
    y = int((screenGeometry.height() - win.height()) / 2)
    win.move(x, y)

    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
