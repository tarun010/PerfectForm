import cv2
import mediapipe as mp
import formchecker
from enum import Enum
import numpy as np
from PyQt5.QtCore import QSize, Qt, QThread, pyqtSignal, pyqtSlot

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self, camIdx):
        super().__init__()
        self.running = True
        self.MODES = {'SQUAT', 'CURL'}
        self.mode = 'SQUAT'
        self.camera = camIdx

    def run(self):
        # Set up the video capture
        cap = cv2.VideoCapture(self.camera)

        # Create a MediaPipe Pose instance
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

        # Create a MediaPipe Hands instance
        hands = mp.solutions.hands.Hands()

        # Create a MediaPipe Drawing instance
        mp_drawing = mp.solutions.drawing_utils

        while self.running:
            # Read the frame from the camera
            ret, frame = cap.read()

            # Convert the image color to RGB
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Process the image and get the pose and hands landmarks
            results = pose.process(image)
            results_hands = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

            # Draw the pose landmarks on the image
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            # Check for proper form during squats
            if results.pose_landmarks is not None:
                status = formchecker.squats(results, results_hands, image)
                cv2.putText(image, status, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                cv2.putText(image, self.mode, (50, 700), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # Show the image
            self.change_pixmap_signal.emit(cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
            #cv2.imshow('Fitness Form Checker', cv2.cvtColor(image, cv2.COLOR_RGB2BGR))

        # Release the resources
        cap.release()
        #cv2.destroyAllWindows()

    def stopCam(self):
        self.running = False
        self.wait()

    def setMode(self, newMode):
        if (newMode.upper() not in self.MODES): return 0
        self.mode = newMode.upper()
        return 1

    def setCamera(self, i):
        self.camera = i

    def isRunning(self):
        return self.running