from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLabel


class ImageSelector(QWidget):


    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):


        buttonsLayout = QHBoxLayout()
        self.setLayout(buttonsLayout)


        self.nextImageButton = QPushButton()
        self.nextImageButton.setText("Next")

        self.imageCounter = QLabel()


        self.previuousImageButton = QPushButton()
        self.previuousImageButton.setText("Previous")


        buttonsLayout.addWidget(self.previuousImageButton, Qt.AlignLeft)
        buttonsLayout.addWidget(self.imageCounter, Qt.AlignCenter)
        buttonsLayout.addWidget(self.nextImageButton, Qt.AlignRight)