import sys
import cv2
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, pyqtSlot
import PyQt5.QtGui as QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QComboBox, QLabel
import main
import numpy as np

index = 0
availableCameras = []
while True:
    cap = cv2.VideoCapture(index)
    if not cap.read()[0]:
        break
    else:
        availableCameras.append(str(index))
    cap.release()
    index += 1

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PerfectForm")
        self.setFixedSize(QSize(1024, 768))

        ### Buttons
        self.startButton = QPushButton("Start camera")
        self.startButton.clicked.connect(self.startButtonClicked)

        self.stopButton = QPushButton("Stop camera") 
        self.stopButton.clicked.connect(self.stopButtonClicked)
        self.stopButton.setEnabled(False)
        ###

        ### Dropdowns
        self.modeBox = QComboBox()
        self.modeBox.setToolTip('Choose Exercise Mode')
        self.modeBox.addItems(['Squat'])
        self.modeBox.currentTextChanged.connect(self.modeSelected)

        self.cameraBox = QComboBox()
        self.cameraBox.setToolTip('Choose Camera (by index)')
        self.cameraBox.addItems(availableCameras)
        self.cameraBox.currentIndexChanged.connect(self.cameraSelected)
        ### 

        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(1024, 768)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.image_label)
        self.layout.addWidget(self.startButton)
        self.layout.addWidget(self.stopButton)
        self.layout.addWidget(self.cameraBox)
        self.layout.addWidget(self.modeBox)

        self.container = QWidget()
        self.container.setLayout(self.layout)

        # Set the central widget of the Window.
        self.setCentralWidget(self.container)

        # create the video capture thread
        #self.thread = main.VideoThread()

        # connect its signal to the update_image slot
        #self.thread.change_pixmap_signal.connect(self.update_image)
        
        # start the thread
        #self.thread.start()

    def closeEvent(self, event):
        self.thread.stopCam()
        event.accept()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(1024, 768, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    def startButtonClicked(self):
        self.startButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.cameraBox.setEnabled(False)

        # create the video capture thread
        self.thread = main.VideoThread(self.cameraBox.currentIndex())
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    def stopButtonClicked(self):
        self.stopButton.setEnabled(False)
        self.startButton.setEnabled(True)
        self.cameraBox.setEnabled(True)
        self.thread.stopCam()

    def modeSelected(self, s):
        print(s)
        self.thread.setMode(s)

    def cameraSelected(self, i):
        print(i)
        #self.thread.setCamera(i)

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()