from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QHBoxLayout, QWidget, QMessageBox


class MaskTable(QWidget):


    def __init__(self):
        super().__init__()


        self.masks = {}
        self.actualImage = None
        self.setup()



    def setActualImage(self, actualImageID):
        self.actualImage = actualImageID
    def insertMask(self):
        selectedLabel = self.parent().labelhandler.getCheckedLabel()
        if selectedLabel is None:
            QMessageBox.information(self, "Label not Selected", "Select a label to save the mask.")
            return
        selectedMask = self.parent().magicWand.getMask()
        if selectedMask:
            pass

        self.table.insertRow(self.table.rowCount())
        self.table.setItem(self.table.rowCount() - 1, 0, QTableWidgetItem(selectedLabel))

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
        self.table.setHorizontalHeaderLabels(["Masks' Labels"])
        self.table.setColumnWidth(0, 350)
        self.table.setColumnCount(1)

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
