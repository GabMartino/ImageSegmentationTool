from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel


class ImageSelector(QWidget):


    def __init__(self):
        super().__init__()

        self.setup()

        self.indexImage = 0
        self.size = None

    def setup(self):


        buttonsLayout = QHBoxLayout()
        self.setLayout(buttonsLayout)


        self.nextImageButton = QPushButton()
        self.nextImageButton.setText("Next")
        self.nextImageButton.clicked.connect(self.goNext)


        self.imageCounter = QLabel()
        self.imageCounter.setAlignment(Qt.AlignCenter)


        self.previuousImageButton = QPushButton()
        self.previuousImageButton.setText("Previous")
        self.previuousImageButton.clicked.connect(self.goPrevious)

        buttonsLayout.addWidget(self.previuousImageButton)
        buttonsLayout.addWidget(self.imageCounter)
        buttonsLayout.addWidget(self.nextImageButton)



    def getActualImageID(self):
        return self.indexImage


    def setSize(self, size):
        self.size = size
        self.imageCounter.setText(str(self.indexImage + 1) + "/" + str(self.size))


    def setCallbackForGoNext(self, method):
        self.goNextCallback = method

    def setCallbackForGoPrevious(self, method):
        self.goPreviousCallback = method

    def goNext(self):
        if self.size:
            self.indexImage = (self.indexImage + 1) % self.size
            self.imageCounter.setText(str(self.indexImage + 1) + "/" + str(self.size))
            self.goNextCallback(self.indexImage)

    def goPrevious(self):
        if self.size:
            self.indexImage = (self.indexImage - 1) % self.size

            self.imageCounter.setText(str(self.indexImage + 1) + "/" + str(self.size))
            self.goPreviousCallback(self.indexImage)
