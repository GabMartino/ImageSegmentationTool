from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QMessageBox

from SegmentationLabeling.src.utils.utils import drawMaskOnImage


class MaskTable(QWidget):


    def __init__(self):
        super().__init__()

        self.masks = {}
        self.actualImageID = None
        self.setupUI()
        self.overlayHook = None

    '''
        Set the ID of the actual image, for saving purpose
    '''
    def setActualImage(self, actualImageID):
        self.actualImageID = actualImageID
        self.cleanTable()
        self.updateTable() if self.actualImageID is not None else None

    def setOverlayCursorHook(self, hook):
        self.overlayHook = hook

    def insertMask(self):
        if self.actualImageID is None:
            QMessageBox.information(self, "Images folder not selected", "Select an image folder before adding a mask")
            return
        '''
            Get label checked
        '''
        selectedLabel = self.parent().labelhandler.getCheckedLabel()
        if selectedLabel is None:
            QMessageBox.information(self, "Label not Selected", "Select a label to save the mask.")
            return

        '''
            Get mask from magic wand
        '''
        selectedMask = self.parent().magicWand.getMask()
        print("print selected mask", selectedMask)
        if selectedMask is not None:
            '''
                Insert the mask in the list of the masks of the image of the label selected
            '''
            labelledMask = {
                'label': selectedLabel,
                'mask': selectedMask.tolist()
            }

            if self.actualImageID in self.masks:
                self.masks[self.actualImageID].append(labelledMask)
            else:
                self.masks[self.actualImageID] = [labelledMask]

            self.table.insertRow(self.table.rowCount())
            item = QTableWidgetItem(selectedLabel)
            item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(self.table.rowCount() - 1, 0, item)
        else:
            QMessageBox.information(self, "No mask created", "Still no masks have been created.")

    def removeMask(self):
        select = self.table.selectionModel()
        selectedRows = select.selectedRows()
        if len(selectedRows) > 0:
            row = selectedRows[0].row()
            self.table.removeRow(row)
            del self.masks[self.actualImageID][row]
        else:
            QMessageBox.information(self, "No row selected to be removed.", "No row selected to be removed.")
    def setupUI(self):

        masktableLayout = QVBoxLayout()
        self.setLayout(masktableLayout)

        buttonsW = QWidget()
        buttonsLayout = QHBoxLayout()
        buttonsW.setLayout(buttonsLayout)

        self.table = QTableWidget()
        #self.table.setHorizontalHeaderLabels(["Masks' Labels"])
        self.table.setColumnWidth(0, 350)
        self.table.setColumnCount(1)
        self.table.clicked.connect(self.handleMasksClicking)

        addMaskButton = QPushButton()
        addMaskButton.setText("Add Mask")
        addMaskButton.clicked.connect(self.insertMask)

        removeMaskButton = QPushButton()
        removeMaskButton.setText("Remove Mask")
        removeMaskButton.clicked.connect(self.removeMask)

        buttonsLayout.addWidget(addMaskButton)
        buttonsLayout.addWidget(removeMaskButton)

        masktableLayout.addWidget(self.table)
        masktableLayout.addWidget(buttonsW)


    def updateTable(self):
        if self.actualImageID in self.masks:
            for maskDict in self.masks[self.actualImageID]:
                label = maskDict['label']
                self.table.insertRow(self.table.rowCount())
                item = QTableWidgetItem(label)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(self.table.rowCount() - 1, 0, item)

    def cleanTable(self):
        self.table.clearContents()
        self.table.clear()
        for row in range(self.table.rowCount()):
            self.table.removeRow(row)
    '''
        When some rows are clicked the mask selected should be shown
    '''
    def handleMasksClicking(self):
        select = self.table.selectionModel()
        selectedRows = select.selectedRows()
        masks = []
        for row in selectedRows:
            masks.append(self.masks[self.actualImageID][row.row()]['mask'])


        '''
        print(masks)
        for mask in masks:
            img, _, _ = drawMaskOnImage(img, mask)
        '''
        self.overlayHook.drawMultipleMasksOnActualImage(masks)


    ## TODO: set smoothing factors
    ## TODO: set tolerance of the channel in vertical slider
    ## TODO: implement exportation in COCO