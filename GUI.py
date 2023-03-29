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
        self.fileMenu.addAction(self.exportAct)
        self.fileMenu.addAction(self.importAct)
        self.menuBar().addMenu(self.fileMenu)

    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O", triggered=self.openImageFolder)
        self.exportAct = QAction("&Export", self, shortcut="Ctrl+S", triggered=self.exportAnnotations)
        self.importAct = QAction("&Import", self, shortcut="Ctrl+I", triggered=self.importAnnotations)
    ###########################################################################################

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
    def exportAnnotations(self):
        if self.fileList:

            dialog = QFileDialog()
            actualDir = "/home/gabriele/Desktop/"  # TO BE REMOVED AFTER TESTING PHASE

            filename, extension = dialog.getSaveFileName(self, "Save Annotations", actualDir, ".json", options=QFileDialog.DontUseNativeDialog)

            import json
            masks = self.toolbar.masktable.masks

            annotations = []
            for imageID in masks:
                annotations.append({'id': imageID,
                                    'filename': self.fileList[imageID],
                                    'annotation': masks[imageID]})


            with open(filename + extension, "w") as outfile:
                json.dump(annotations, outfile)
        else:
            QMessageBox.information(self, "No Image folder selected", "No annotation has been found.")

    def importAnnotations(self):
        pass

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
