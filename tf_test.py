import cv2
import numpy as np
import tensorflow as tf

# Load OpenPose model
model = tf.keras.models.load_model("path/to/your/pose/model")

# Set reference angles for good form
reference_angles = {
    "shoulder-elbow-wrist": 90,
    "hip-knee-ankle": 180
}

# Define a function to calculate the angle between three joints
def calculate_angle(joint1, joint2, joint3):
    v1 = np.array([joint1[0] - joint2[0], joint1[1] - joint2[1]])
    v2 = np.array([joint3[0] - joint2[0], joint3[1] - joint2[1]])
    angle = np.degrees(np.arccos(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)))
    return angle

# Define a function to extract joints and angles from each frame in a video
def extract_pose_from_video(video_path):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Preprocess the frame
        input_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        input_image = cv2.resize(input_image, (656, 368))
        input_image = input_image.astype(np.float32) / 255.0
        input_image = np.expand_dims(input_image, axis=0)
        
        # Predict the poses
        heatmaps, pafs = model.predict(input_image)
        heatmaps = np.squeeze(heatmaps)
        pafs = np.squeeze(pafs)
        
        # Extract joint coordinates and calculate angles
        joint_coords = []
        if heatmaps.ndim == 3 and pafs.ndim == 3:
            # Iterate over each keypoint and find the corresponding peak
            for i in range(heatmaps.shape[-1]):
                heatmap = heatmaps[..., i]
                heatmap = cv2.resize(heatmap, (frame.shape[1], frame.shape[0]))
                joint_coord = np.unravel_index(np.argmax(heatmap), heatmap.shape)
                joint_coords.append(joint_coord)
            
            if len(joint_coords) > 0:
                # Calculate shoulder-elbow-wrist angle
                shoulder = joint_coords[5]  # index 5 corresponds to the left shoulder
                elbow = joint_coords[6]  # index 6 corresponds to the left elbow
                wrist = joint_coords[7]  # index 7 corresponds to the left wrist
                angle1 = calculate_angle(shoulder, elbow, wrist)
                
                # Calculate hip-knee-ankle angle
                hip = joint_coords[11]  # index 11 corresponds to the left hip
                knee = joint_coords[12]  # index 12 corresponds to the left knee
                ankle = joint_coords[13]  # index 13 corresponds to the left ankle
                angle2 = calculate_angle(hip, knee, ankle)
                
                # Compare angles to reference angles
                good_form = (abs(angle1 - reference_angles["shoulder-elbow-wrist"]) <= 10)
