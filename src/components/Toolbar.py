from PyQt5.QtWidgets import QWidget, QVBoxLayout

from SegmentationLabeling.src.components.LabelsHandler import LabelsHandler
from SegmentationLabeling.src.components.MaskTable import MaskTable
from SegmentationLabeling.src.components.imageSelector.ImageSelector import ImageSelector
from SegmentationLabeling.src.components.magicwandComponents.magicWand import MagicWand


class Toolbar(QWidget):



    def __init__(self):
        super().__init__()

        self.setup()
        self.show()
    '''
        The toolbar is made of 
        1) magiWandButton, colorPreview, colorLabel
                slider
        2) Add Label, Remove Label
        3) Mask list with check box for visualizing
        4) Preview, 1/N, Next
    
    '''
    def setup(self):

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.magicWand = MagicWand()
        self.labelhandler = LabelsHandler()
        self.masktable = MaskTable()
        self.imageSelector = ImageSelector()


        layout.addWidget(self.magicWand)
        layout.addWidget(self.labelhandler)
        layout.addWidget(self.masktable)
        layout.addWidget(self.imageSelector)


