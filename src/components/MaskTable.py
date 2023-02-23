from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class MaskTable(QTableWidget):


    def __init__(self):
        super().__init__()

        self.setup()
    def insertMask(self):

        newItem = QTableWidgetItem
        self.setItem()
    def setup(self):
        self.setRowCount(10)
        self.setColumnCount(3)