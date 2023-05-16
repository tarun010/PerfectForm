import mediapipe as mp
import cv2

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# Initialize pose estimation model
pose = mp_pose.Pose()

cap = cv2.VideoCapture(0)

while True:
    success, image = cap.read()
    if not success:
        break

    # Convert image to RGB format
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Run pose estimation model on the image
    results = pose.process(image)

    if results.pose_landmarks:
        # Get landmarks for shoulders, hips, and spine
        left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
        left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
        right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
        mid_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.HIP_]
        spine = results.pose_landmarks.landmark[mp_pose.PoseLandmark.SPINE_MID]

        # Calculate angles between shoulders, hips, and spine
        angle_shoulders = angle_between_points(left_shoulder, right_shoulder, mid_hip)
        angle_hips = angle_between_points(left_hip, right_hip, spine)

        # Determine if person is standing sideways
        if angle_shoulders < 60 and angle_hips > 120:
            cv2.putText(image, "Sideways", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2, cv2.LINE_AA)
        else:
            cv2.putText(image, "Not sideways", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2, cv2.LINE_AA)

    # Convert image back to BGR format for displaying
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    # Display image
    cv2.imshow("Image", image)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

def angle_between_points(p1, p2, p3):
    # Calculate angle between three points using cosine rule
    a = (p2.x - p1.x)**2 + (p2.y - p1.y)**2
    b = (p2.x - p3.x)**2 + (p2.y - p3.y)**2
    c = (p3.x - p1.x)**2 + (p3.y - p1.y)**2
    angle = math.degrees(math.acos((a + b - c) / math.sqrt(4 * a * b)))
    return angle
