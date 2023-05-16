import cv2
import mediapipe as mp
import math
import time
import numpy as np

# Create a MediaPipe Pose instance
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Create a MediaPipe Drawing instance
mp_drawing = mp.solutions.drawing_utils

# Create a MediaPipe Hands instance
hands = mp.solutions.hands.Hands()

count = -1
hand_seconds = 0
hand_start_time = 0
squat_seconds = 0
squat_start_time = 0
state = "wtever"
prev_state = "wtever"

def calculate_angle(a, b, c):
    # Calculate the angle between three joints
    radians = math.atan2(c.y - b.y, c.x - b.x) - math.atan2(a.y - b.y, a.x - b.x)
    angle = abs(radians * 180.0 / math.pi)

    if angle > 180:
        angle = 360 - angle

    return angle  

def calculate_normal(hand_landmarks):
    # Check if there are at least 3 points
    if len(hand_landmarks) < 3:
        return None
    
    # Calculate the normal vector of the palm surface
    if len(hand_landmarks) == 3:
        a = np.array([hand_landmarks[1].x, hand_landmarks[1].y, 0]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, 0])
        b = np.array([hand_landmarks[2].x, hand_landmarks[2].y, 0]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, 0])
        normal = np.cross(a, b)
    elif len(hand_landmarks) == 4:
        normal = np.cross(np.array([hand_landmarks[1].x, hand_landmarks[1].y, hand_landmarks[1].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z]),
                           np.array([hand_landmarks[2].x, hand_landmarks[2].y, hand_landmarks[2].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z]))
    elif len(hand_landmarks) == 5:
        normal = np.cross(np.array([hand_landmarks[1].x, hand_landmarks[1].y, hand_landmarks[1].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z]),
                           np.array([hand_landmarks[2].x, hand_landmarks[2].y, hand_landmarks[2].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z])) \
                 + np.cross(np.array([hand_landmarks[2].x, hand_landmarks[2].y, hand_landmarks[2].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z]),
                            np.array([hand_landmarks[3].x, hand_landmarks[3].y, hand_landmarks[3].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z])) \
                 + np.cross(np.array([hand_landmarks[3].x, hand_landmarks[3].y, hand_landmarks[3].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z]),
                            np.array([hand_landmarks[1].x, hand_landmarks[1].y, hand_landmarks[1].z]) - np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z]))
    else:
        return None
    
    # Normalize the normal vector
    normal /= np.linalg.norm(normal)
    
    return normal

def should_start(results_hands, img):
    global count, start_time, hand_seconds
    if count < 0 and hand_seconds < 3:
        if results_hands is not None and results_hands.multi_hand_landmarks:
            hand_landmarks = results_hands.multi_hand_landmarks[0].landmark
            
            # Define the wrist, index finger tip, and middle finger tip
            wrist = np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z])
            index_tip = np.array([hand_landmarks[8].x, hand_landmarks[8].y, hand_landmarks[8].z])
            middle_tip = np.array([hand_landmarks[12].x, hand_landmarks[12].y, hand_landmarks[12].z])

            # Calculate the vectors from the wrist to the index and middle fingers' tips
            index_vector = index_tip - wrist
            middle_vector = middle_tip - wrist

            # Calculate the cross product of the two vectors
            palm_normal = np.cross(index_vector, middle_vector)
            print ("Palm normal: ",palm_normal)

            # Check if the hand is facing the camera
            if palm_normal[2] <= 0:
                # Palms are facing towards you
                print("Palms are facing towards you")
                if hand_seconds == 0:
                    start_time = time.time()
                    print("start_time: ", start_time)
                hand_seconds = time.time() - start_time
                print ("time.time: ", time.time())
                print("start_time: ", start_time)
                print ("seconds: ",hand_seconds)
            else:
                hand_seconds = 0
                # Palms are facing away from you
                print("Palms are facing away from you")

            if hand_seconds == 3:
                count = 0
                return_value = True
            else:
                return_value = False
        else:
            return_value = False
    else:
        return_value = True
    return return_value

def if_standing_sideways(results):
    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
    left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
    right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
    right_foot = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
    left_foot = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
    left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST]
    right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
    right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
    left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]
    
    shoulder_angle = calculate_angle(right_shoulder, left_shoulder, left_shoulder)
    hip_angle = calculate_angle(right_hip, left_hip, left_hip)
    foot_angle = calculate_angle(right_foot, left_foot, left_foot)

    if ((right_wrist.x < right_elbow.x < right_shoulder.x and
        right_wrist.y < right_elbow.y < right_shoulder.y) or 
        (left_wrist.x < left_elbow.x < left_shoulder.x and
        left_wrist.y < left_elbow.y < left_shoulder.y)) :
        if shoulder_angle > 170 or hip_angle > 150 or foot_angle > 150:
            status = False
        else:
            status = True
    else:
        if shoulder_angle > 190 or hip_angle > 190 or foot_angle > 150:
            status =  False
        else:
            status =  True

    return status

def squats(results, results_hands, img):
        
    global count, state, prev_state, squat_start_time, squat_seconds

    # Define the thresholds for each pose keypoint
    foot_angle_threshold = 60  # in degrees
    knee_angle_start_threshold = 160  # in degrees
    knee_angle_bottom_threshold = 100  # in degrees
    hip_angle_bottom_threshold = 80  # in degrees

    # Check if the person is standing sideways
    is_sideways = if_standing_sideways(results)

    if should_start(results_hands, img):  
        print ("should start: ",should_start(results_hands, img)) 
        if is_sideways:
            # Get the pose keypoints for the feet, knees, hips, shoulders, and back
            left_foot = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
            right_foot = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]
            left_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE]
            right_knee = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE]
            left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
            right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
            left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            left_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE]
            right_ankle = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE]
    
            # Calculate the distances and angles between the pose keypoints
            foot_distance = abs(left_foot.x - right_foot.x)
            shoulder_distance = abs(left_shoulder.x - right_shoulder.x)       #Foot distance threshold
            if left_foot.visibility > 0.5 and right_foot.visibility > 0.5:
                foot_angle = abs(math.atan2(left_foot.y - right_foot.y, left_foot.x - right_foot.x) * 180 / math.pi)
            else:
                foot_angle = 90
            left_knee_angle = calculate_angle (left_hip, left_knee, left_ankle)
            right_knee_angle = calculate_angle (right_hip, right_knee, right_ankle)
            left_hip_angle = calculate_angle (left_shoulder, left_hip, left_knee)
            right_hip_angle = calculate_angle (right_shoulder, right_hip, right_knee)
        

            knee_angle = (left_knee_angle + right_knee_angle) / 2
            hip_angle = (left_hip_angle + right_hip_angle) / 2
            
            # Calculate the midpoint between the left and right hip landmarks
            mid_hip_x = (left_hip.x + right_hip.x) / 2
            mid_hip_y = (left_hip.y + right_hip.y) / 2

            # Calculate the midpoint between the left and right shoulder landmarks
            mid_shoulder_x = (left_shoulder.x + right_shoulder.x) / 2
            mid_shoulder_y = (left_shoulder.y + right_shoulder.y) / 2

            # Calculate the angle between the line connecting the left and right shoulder landmarks, and
            # the line connecting the midpoint between the left and right hip landmarks and the midpoint
            # between the left and right shoulder landmarks
            back_angle = abs(abs(math.atan2(mid_shoulder_y - mid_hip_y, mid_shoulder_x - mid_hip_x) * 180 / math.pi))

            text = str(count)

            # Set the font and font scale
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1

            # Set the thickness of the text
            thickness = 2

            # Get the size of the text
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)

            # Define the position of22e                         C:\Users\dmura\OneDrive\Desktop\MUN\Term 8\Computer Vision\Project\computer_vision_project the text
            position = (10, img.shape[0]-10)

            # Draw the text on the image
            cv2.putText(img, text, position, font, font_scale, (255, 255, 255), thickness)


            # set the state of the squat
            if knee_angle > knee_angle_start_threshold:
                state = "starting"
                status = "".join("starting")
                if(prev_state == "bottom"):
                    count += 1
                    prev_state = "starting"
            elif (state == "starting" or state == "descending") and knee_angle < knee_angle_start_threshold and knee_angle > knee_angle_bottom_threshold:
                state = "descending"
                status = "".join("descending")        
            elif state == "descending" and knee_angle <= knee_angle_bottom_threshold:
                state = "bottom"
                status = "".join("bottom")
            elif (state == "bottom" or state == "ascending" or state == "idk") and knee_angle > knee_angle_bottom_threshold and knee_angle < knee_angle_start_threshold:
                state = "ascending"
                status = "".join("ascending")
            else:
                state = "idk"
                status = "".join("idk")


            #Depending on the state, check if the person is in a good squat position
            if state == "starting":
                print("state: ", state)
                if (knee_angle > knee_angle_start_threshold and
                    (foot_distance - shoulder_distance) == 0.1 and
                    foot_angle > foot_angle_threshold):
                    print("knee angle: ", knee_angle)
                    print("good starting position")
                    status = "".join("Good starting position")
                    squat_seconds = 0; 
                else:
                    improper_form = []
                    if ((foot_distance - shoulder_distance) == 0.1):
                        print("foot distance: ", foot_distance)
                        print ("Feet are too far apart.")
                        improper_form.append("Feet are too far apart.")
                    if foot_angle <= foot_angle_threshold:
                        print("foot angle: ", foot_angle)
                        print("Feet are not parallel.")
                        improper_form.append("Feet are not parallel.")
                    if knee_angle <= knee_angle_start_threshold:
                        print("knee angle: ", knee_angle)
                        print("knees should be straighter in starting position")
                        status = "".join("Knees should be straighter in starting position")
                    status = "".join(improper_form)    
                    

            elif state == "descending" or state == "ascending":
                print("state: ", state)
                if ((foot_distance - shoulder_distance) == 0.1 and
                        foot_angle > foot_angle_threshold):
                    print("foot distance: ", foot_distance)
                    print("foot angle: ", foot_angle)
                    status = "".join("Good posture during descent/ascent")
                else:
                    improper_form = []
                    if ((foot_distance - shoulder_distance) == 0.1):
                        print("foot distance: ", foot_distance)
                        print ("Feet are too far apart.")
                        improper_form.append("Feet are too far apart.")
                    if foot_angle <= foot_angle_threshold:
                        print("foot angle: ", foot_angle)
                        print("Feet are not parallel.")
                        improper_form.append("Feet are not parallel.")
                    status = "".join(improper_form)

            elif state == "bottom":
                print("state: ", state)
                if ((foot_distance - shoulder_distance) == 0.1 and
                        foot_angle > foot_angle_threshold and
                        knee_angle <= knee_angle_bottom_threshold and
                        hip_angle >= hip_angle_bottom_threshold):
                    print("foot distance: ", foot_distance)
                    print("foot angle: ", foot_angle)
                    print("knee_angle: ", knee_angle)
                    status = "".join("Good posture at the bottom")
                    if squat_seconds == 0:
                        squat_start_time = time.time()
                    squat_seconds = time.time() - squat_start_time
                    if squat_seconds >= 2:
                      prev_state = "bottom"  
                else:
                    squat_seconds = 0
                    improper_form = []
                    if (foot_distance - shoulder_distance) == 0.1:
                        print("foot distance: ", foot_distance)
                        print ("Feet are too far apart.")
                        improper_form.append("Feet are too far apart.")
                    if foot_angle <= foot_angle_threshold:
                        print("foot angle: ", foot_angle)
                        print("feet are not parallel")
                        improper_form.append("Feet are not parallel.")
                    if knee_angle >= knee_angle_bottom_threshold:
                        print("knee_angle: ", knee_angle)
                        print("knees are not bent enough")
                        improper_form.append("Knees are not bent enough.")
                    if hip_angle <= hip_angle_bottom_threshold:
                        print("hip angle: ", hip_angle)
                        print("hips are not low enough")
                        improper_form.append("Hips are not low enough.")
                    status = "".join(improper_form)
            else:
                status = "".join("Invalid squat state")
        else:
            status = "".join("Please stand sideways")
    else:
        status = "".join("Show palm towards screen for 3 secs. to begin...")

    return status
