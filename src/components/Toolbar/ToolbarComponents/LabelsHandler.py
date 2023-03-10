from PyQt5.QtWidgets import QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QInputDialog, QLineEdit, QMessageBox, \
    QGridLayout

'''
    This class represent the list of buttons linked to the labels
'''

class LabelButtonList(QWidget):

    def __init__(self):
        super().__init__()

        self.buttonList = []
        self.labels = []
        self.checkedLabel = None
        self.lastFilledRow = 0
        self.lastFilledColumn = 0
        self.maximumColumnPerRow = 3
        self.setupUI()

    def setupUI(self):

        self.layout = QGridLayout()
        self.setLayout(self.layout)





    def genRandomColor(self):
        import random
        r = lambda: random.randint(0, 255)
        return '#{:02x}{:02x}{:02x}'.format(r(), r(), r())

    '''
        Insert a new button.
        We set a layout where only 3 buttons can be present on the same row
    '''
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
            self.layout.addWidget(button,self.lastFilledRow, self.lastFilledColumn, 1, 1)
            self.lastFilledColumn = (self.lastFilledColumn + 1) % self.maximumColumnPerRow
            self.lastFilledRow = int(len(self.labels)/ self.maximumColumnPerRow)
            return True

    def removeLabelButton(self, labelName):

        try:
            index = self.labels.index(labelName)
            w = self.layout.itemAt(index).widget()
            self.layout.removeWidget(w)
            w.deleteLater()
            self.labels.remove(labelName)
            #updateGrid(row, column, index + 1)

            self.lastFilledColumn = (self.lastFilledColumn - 1) % self.maximumColumnPerRow
            self.lastFilledRow = self.lastFilledColumn - 1 if self.lastFilledColumn == 2 else self.lastFilledRow

            return True
        except:
            return False


    '''
        Return the label text of the label checked.
        
        :return None if no label is checked otherwise the string of the label
    '''
    def getCheckedLabel(self):
        return self.checkedLabel

    '''
        Event handler if one of the labels button created is clicked.
        The button could be checked/unchecked.
        If it is checked -> uncheck all the others buttons
        If it is unchecked -> (It's the only one that was checked) so update the state variable
    '''
    def checkLabel(self, checked):
        if checked:
            for b in self.children()[1:]:  ## jump the layout
                if b.text() != self.sender().text():
                    b.setChecked(False)

            self.checkedLabel = self.sender().text() ## Update the state variable
        else:
            self.checkedLabel = None ## Update the state variable



'''
    This Class handles the creating or deleting of the labels that has to be
    assigned to the different masks.

'''
class LabelsHandler(QWidget):

    def __init__(self):
        super().__init__()
        self.setupUI()


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


    def setupUI(self):

        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)
        '''
            Create ADD/REMOVE BUTTONS
        '''
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


        '''
            CREATE LABELS BUTTONS LISTS
        '''
        self.labelButtonList = LabelButtonList()

        mainLayout.addWidget(buttons)
        mainLayout.addWidget(self.labelButtonList)