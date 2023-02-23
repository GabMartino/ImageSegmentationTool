from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QInputDialog, QLineEdit, QMessageBox, \
    QGridLayout


class LabelButtonList(QWidget):

    def __init__(self):
        super().__init__()

        self.buttonList = []
        self.labels = []
        self.checkedLabel = None

        self.setup()
    def setup(self):

        self.layout = QGridLayout()
        self.setLayout(self.layout)

    def checkLabel(self, checked):
        if checked:
            for b in self.children()[1:]: ## jump the layout
                if b.text() != self.sender().text():
                    b.setChecked(False)

            self.checkedLabel = self.sender().text()
        else:
            self.checkedLabel = None
    def genRandomColor(self):
        import random
        r = lambda: random.randint(0, 255)
        return '#{:02x}{:02x}{:02x}'.format(r(), r(), r())
    def insertLabelButton(self, labelName):
        try:
            index = self.labels.index(labelName)
            return False
        except:
            button = QPushButton(labelName)
            button.setCheckable(True)
            button.clicked.connect(self.checkLabel)
            button.setStyleSheet("background-color:"+self.genRandomColor()+";")
            self.labels.append(labelName)
            self.layout.addWidget(button)
            return True

    def removeLabelButton(self, labelName):
        try:
            index = self.labels.index(labelName)
            print(index)
            w = self.layout.itemAt(index).widget()
            print(w)
            self.layout.removeWidget(w)
            w.deleteLater()
            self.labels.remove(labelName)
            return True
        except:
            return False

    def getCheckedLabel(self):
        return self.checkedLabel

class LabelsHandler(QWidget):

    def __init__(self):
        super().__init__()

        self.setup()
    def addLabel(self):
        text, ok = QInputDialog().getText(self, "Insert new Label Name", "Label Name:", QLineEdit.Normal)
        if ok and text:
            check = self.labelButtonList.insertLabelButton(text)
            if not check:
                QMessageBox.information(self, "Label already Present", "The label name inserted is already present. Type another label name.")
    def removeLabel(self):
        text, ok = QInputDialog().getText(self, "Insert a Label Name to Remove", "Label Name:", QLineEdit.Normal)
        if ok and text:
            check = self.labelButtonList.removeLabelButton(text)
            if not check:
                QMessageBox.information(self, "Label not Present", "The label name inserted does not exist.")


    def getCheckedLabel(self):
        return self.labelButtonList.getCheckedLabel()
    def setup(self):

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        buttons = QWidget()
        buttonsLayout = QHBoxLayout()
        buttons.setLayout(buttonsLayout)

        AddLabelButton = QPushButton()
        AddLabelButton.setText("Add Label")
        AddLabelButton.clicked.connect(self.addLabel)

        RemoveLabelButton = QPushButton()
        RemoveLabelButton.setText("Remove Label")
        RemoveLabelButton.clicked.connect(self.removeLabel)

        buttonsLayout.addWidget(AddLabelButton)
        buttonsLayout.addWidget(RemoveLabelButton)

        self.labelButtonList = LabelButtonList()






        mainLayout.addWidget(buttons)
        mainLayout.addWidget(self.labelButtonList)