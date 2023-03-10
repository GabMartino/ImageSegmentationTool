from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QMessageBox


class MaskTable(QWidget):


    def __init__(self):
        super().__init__()

        self.masks = {}
        self.actualImageID = None
        self.setup()


    def setActualImage(self, actualImageID):
        self.actualImageID = actualImageID


    def insertMask(self):
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
        print(selectedMask)
        if selectedMask is not None:
            '''
                Insert the mask in the list of the masks of the image of the label selected
            '''
            labelledMask = {
                'label': selectedLabel,
                'mask': selectedMask
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
        else:
            QMessageBox.information(self, "No row selected to be removed.", "No row selected to be removed.")
    def setup(self):

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


    def showActualImageMasks(self):
        labelledMask = self.masks[self.actualImageID]

        for mask in labelledMask:
            self.table.insertRow(self.table.rowCount())
            self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(mask['label']))

    def cleanTable(self):
        self.table.clearContents()
    '''
        When some rows are clicked the mask selected should be shown
    '''
    def handleMasksClicking(self):
        select = self.table.selectionModel()
        selectedRows = select.selectedRows()
        print(selectedRows)
        for row in selectedRows:
            mask = self.masks[self.actualImageID][row.row()]['mask']




    ## TODO: clear table when switching images and report the saved mask when turning back to the image
    ## TODO: set smoothing factors
    ## TODO: set labels in GRID Layouts
    ## TODO: show selected mask when clicked on table
    ## TODO: set tolerance of the channel in vertical slider
    ## TODO: implement exportation in COCO