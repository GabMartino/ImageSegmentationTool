from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QIcon, QPalette, QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider


class MagicWandButton(QPushButton):

    def __init__(self, ico_path):
        super().__init__()
        self.ico_path = ico_path
        self.setup()
        self.show()
    def setup(self):
        qico = QPixmap(self.ico_path)
        ico = QIcon(qico)
        self.setIcon(ico)

        self.setFixedSize(QSize(40, 40))
        self.setIconSize(QSize(20, 20))
        self.setCheckable(True)

    def setClickCallback(self, method):
        self.clicked.connect(method)

class ColorPreview(QLabel):

    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.setFixedSize(40, 40)
        self.setStyleSheet("border: 2px solid black")


class ColorLabel(QLabel):

    def __init__(self):
        super().__init__()
        self.setup()
    def setup(self):
        self.setFixedSize(QSize(100, 30))


class MagicWandSlider(QWidget):

    def __init__(self):
        super().__init__()

        self.setup()

    def setup(self):

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.slider = QSlider(Qt.Horizontal)

        self.slider.setMinimum(1)
        self.slider.setMaximum(150)
        self.slider.setTickPosition(10)
        self.slider.setFixedSize(200, 20)

        labels = QWidget()

        slider_hbox = QHBoxLayout()
        labels.setLayout(slider_hbox)
        slider_hbox.setContentsMargins(0, 0, 0, 0)

        label_minimum = QLabel(alignment=Qt.AlignLeft)
        label_minimum.setText(str(self.slider.minimum()))
        label_maximum = QLabel(alignment=Qt.AlignRight)
        label_maximum.setText(str(self.slider.maximum()))

        slider_hbox.addWidget(label_minimum, Qt.AlignLeft)
        slider_hbox.addWidget(label_maximum, Qt.AlignRight)

        layout.addWidget(self.slider)
        layout.addWidget(labels)

    def setValueChangedCallback(self, method):
        self.slider.valueChanged.connect(method)


class MagicWand(QWidget):

    def __init__(self):
        super().__init__()
        self.magicWandRadius = 10

        self.setup()
        self.show()
    def setup(self):
        mainLayout = QVBoxLayout()
        self.setLayout(mainLayout)

        self.wandSet = QWidget()

        lineLayout = QHBoxLayout()
        self.wandSet.setLayout(lineLayout)

        self.button = MagicWandButton("resources/magic-wand.png")
        self.colorSelected = ColorPreview()
        self.colorLabel = ColorLabel()

        lineLayout.addWidget(self.button)
        lineLayout.addWidget(self.colorSelected)
        lineLayout.addWidget(self.colorLabel)

        self.slider = MagicWandSlider()



        mainLayout.addWidget(self.wandSet)
        mainLayout.addWidget(self.slider)

    def setViewedColor(self, color):
        r, g, b = color
        palette = QPalette()
        palette.setColor(self.colorSelected.backgroundRole(), QColor(r, g, b))
        self.colorSelected.setAutoFillBackground(True)
        self.colorSelected.setPalette(palette)

        def rgb_to_hex(r, g, b):
            return '#{:02x}{:02x}{:02x}'.format(r, g, b)

        colorText = "(" + str(r) + ", " + str(g) + ", " + str(b) + ")\n"
        colorText += rgb_to_hex(r, g, b)
        self.colorLabel.setText(colorText)