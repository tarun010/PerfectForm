import cv2
import mediapipe as mp
import math
        
"""     
        # Extract the hand landmarks
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
        left_pinky = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_PINKY]
        right_pinky = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_PINKY]
        left_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_INDEX]
        right_index = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_INDEX]
        left_thumb = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_THUMB]
        right_thumb = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_THUMB]

        print ("left wrist: ", left_wrist)
        print ("right wrist: ", right_wrist)
        print ("left pinky: ", left_pinky)
        print ("right pinky: ", right_pinky)
        print ("left index: ", left_index)
        print ("right index: ", right_index)
        print ("left thumb: ", left_thumb)
        print ("right thumb: ", right_thumb)

        # Calculate the orientation of the hands
        left_hand_orientation = np.array([left_pinky.x, left_pinky.y, left_pinky.z]) - np.array([left_thumb.x, left_thumb.y, left_thumb.z])
        right_hand_orientation = np.array([right_pinky.x, right_pinky.y, right_pinky.z]) - np.array([right_thumb.x, right_thumb.y, right_thumb.z])

        # Check if the palms are facing towards or away from you
        if left_hand_orientation[2] > 0 or right_hand_orientation[2] > 0:
            # Palms are facing towards you
            print("Palms are facing towards you")
            if(seconds == 0):
                start_time = time.time()
            seconds = time.time() - start_time

        else:
            seconds = 0
            # Palms are facing away from you
            print("Palms are facing away from you")
            
        if seconds == 3: 
            count = 0
            return True
        else:
            return False 
    return True
"""


"""
def check_arm_angle(results):
    # Define the threshold for the angle between the shoulder, elbow, and wrist
    arm_angle_threshold = 90 # in degrees

    # Get the pose keypoints for the shoulder, elbow, and wrist of the right arm
    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
    right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

    # Get the pose keypoints for the shoulder, elbow, and wrist of the left arm
    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]

    # Calculate the angle between the shoulder, elbow, and wrist
    right_arm_angle = math.degrees(calculate_angle(right_shoulder, right_elbow, right_wrist))
    left_arm_angle = math.degrees(calculate_angle(left_shoulder, left_elbow, left_wrist))


    # Check if the right arm angle meets the threshold for a raised arm
    if right_arm_angle >= arm_angle_threshold and left_arm_angle >= arm_angle_threshold:
        status = True
    else:
        status = False

    return status
"""


def calculate_angle(a, b, c):
    # Calculate the angle between three joints
    radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
    angle = abs(radians * 180.0 / math.pi)

    if angle > 180:
        angle = 360 - angle

    return angle

# Create a MediaPipe Pose instance
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Create a MediaPipe Drawing instance
mp_drawing = mp.solutions.drawing_utils

# Initialize the webcam capture
cap = cv2.VideoCapture(0)

# Start the main loop to capture and process each frame
while cap.isOpened():
    # Read a frame from the camera
    ret, frame = cap.read()

    # Flip the frame horizontally for a more intuitive mirror-view display
    frame = cv2.flip(frame, 1)

    # Convert the frame from BGR to RGB for MediaPipe
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the image with MediaPipe
    results = pose.process(image)

    # Draw the detected keypoints on the frame
    if results.pose_landmarks is not None:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]

        left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
        left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]

        right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
        right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]

        # Ensure that camera is placed properly
        right_shoulder_hip_angle = calculate_angle(right_shoulder, right_hip, left_shoulder)
        left_shoulder_hip_angle = calculate_angle(right_shoulder, left_hip, left_shoulder)

        if (right_shoulder_hip_angle < 45 or left_shoulder_hip_angle < 45):    
            status = "Please stand sideways"

        # Calculate the angles of the legs
        left_leg_angle = calculate_angle(left_hip, left_knee, left_ankle)
        right_leg_angle = calculate_angle(right_hip, right_knee, right_ankle)

        # Determine the squat status based on the leg angles
        if left_leg_angle > 160 and right_leg_angle > 160:
            status = "Good posture"
        elif left_leg_angle <= 160 and right_leg_angle <= 160:
            status = "Too low"
        else:
            status = "Uneven posture"

        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)        

    # Display the frame
    cv2.imshow('MediaPipe Pose', frame)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the webcam capture and destroy all windows
cap.release()
cv2.destroyAllWindows()
