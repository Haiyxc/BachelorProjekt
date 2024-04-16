import cv2
import mediapipe as mp
import winsound
import time
import numpy as np



class PushupCounter:
    def __init__(self):
        self.running = True  # Add a flag to control the running state
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.count = 0
        self.is_down = False
        self.feedback_depth = ""  # Feedback zur Tiefe
        self.feedback_alignment = ""  # Feedback zur Ausrichtung
        self.current_position = None
        self.previous_position = None
        self.horizontal_tolerance = 50  # degrees within horizontal considered "valid"

    def calculate_angle(self, landmark1, landmark2, landmark3):
        vector1 = np.array([landmark1.x - landmark2.x, landmark1.y - landmark2.y])
        vector2 = np.array([landmark3.x - landmark2.x, landmark3.y - landmark2.y])
        unit_vector1 = vector1 / np.linalg.norm(vector1)
        unit_vector2 = vector2 / np.linalg.norm(vector2)
        dot_product = np.dot(unit_vector1, unit_vector2)
        angle = np.arccos(dot_product) * (180.0 / np.pi)
        return angle

    def calculate_angle_with_horizontal(self, point1, point2):
        # Calculate the angle between the vector from point1 to point2 and the horizontal axis
        vector = np.array([point2.x - point1.x, point2.y - point1.y])
        horizontal = np.array([1, 0])  # Horizontal vector
        unit_vector1 = vector / np.linalg.norm(vector)
        dot_product = np.dot(unit_vector1, horizontal)
        angle = np.arccos(dot_product) * (180.0 / np.pi)
        return angle

    def process_and_display_angles(self, image, landmarks, threshold=15):
       if landmarks:
        # Define a visibility threshold for landmarks
        visibility_threshold = 0.1

        # Landmarks to check for visibility
        landmark_ids = [
            mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value,
            mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value,
            mp.solutions.pose.PoseLandmark.LEFT_WRIST.value,
            mp.solutions.pose.PoseLandmark.LEFT_HIP.value,
            mp.solutions.pose.PoseLandmark.LEFT_KNEE.value,
            mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value,
            mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value,
            mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value,
            mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value,
            mp.solutions.pose.PoseLandmark.RIGHT_HIP.value,
            mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value,
            mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value
        ]

        # Check if all required landmarks are visible
        all_landmarks_visible = all(landmarks[i].visibility > visibility_threshold for i in landmark_ids)

        #if not all_landmarks_visible:
        #    cv2.putText(image, "Get in position or adjust frame", ((image.shape[1] - cv2.getTextSize("Get in position or adjust frame", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2, (image.shape[0] + cv2.getTextSize("Get in position or adjust frame", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][1]) // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
        #    return image

        acceptable_ranges = {
            'up': {'elbow': 176, 'shoulder': 55, 'hip': 0, 'knee': 160},
            'down': {'elbow': 80, 'shoulder': 15, 'hip': 0, 'knee': 160}
        }
        # Extract landmarks
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
        left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value]
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
        right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value]
        right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
        left_knee = landmarks[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value]
        right_knee = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_KNEE.value]
        left_ankle = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value]
        right_ankle = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ANKLE.value]

        # Calculate angles for each joint
        left_elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_elbow_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)
        left_shoulder_angle = self.calculate_angle(left_elbow, left_shoulder, left_hip)
        right_shoulder_angle = self.calculate_angle(right_elbow, right_shoulder, right_hip)
        left_hip_angle = self.calculate_angle(left_hip, left_knee, left_shoulder)
        right_hip_angle = self.calculate_angle(right_hip, right_knee, right_shoulder)
        left_knee_angle = self.calculate_angle(left_hip, left_knee, left_ankle)
        right_knee_angle = self.calculate_angle(right_hip, right_knee, right_ankle)

        # Calculate average angles
        average_hip_angle = (left_hip_angle + right_hip_angle) / 2
        average_elbow_angle = (left_elbow_angle + right_elbow_angle) / 2
        average_shoulder_angle = (left_shoulder_angle + right_shoulder_angle) / 2
        average_knee_angle = (left_knee_angle + right_knee_angle) / 2

        # Display angles on the image
        cv2.putText(image, f"LEA: {int(left_elbow_angle)}", (int(left_elbow.x * image.shape[1]), int(left_elbow.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(image, f"REA: {int(right_elbow_angle)}", (int(right_elbow.x * image.shape[1]), int(right_elbow.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        cv2.putText(image, f"LSA: {int(left_shoulder_angle)}", (int(left_shoulder.x * image.shape[1]), int(left_shoulder.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        cv2.putText(image, f"RSA: {int(right_shoulder_angle)}", (int(right_shoulder.x * image.shape[1]), int(right_shoulder.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
        cv2.putText(image, f"LHA: {int(left_hip_angle)}", (int(left_hip.x * image.shape[1]), int(left_hip.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)
        cv2.putText(image, f"RHA: {int(right_hip_angle)}", (int(right_hip.x * image.shape[1]), int(right_hip.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
        cv2.putText(image, f"LKA: {int(left_knee_angle)}", (int(left_knee.x * image.shape[1]), int(left_knee.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(image, f"RKA: {int(right_knee_angle)}", (int(right_knee.x * image.shape[1]), int(right_knee.y * image.shape[0])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Calculate the angle with the horizontal
        angle_with_horizontal = self.calculate_angle_with_horizontal(left_hip, left_shoulder)

        # Determine if the current position is within the horizontal tolerance
        if angle_with_horizontal <= self.horizontal_tolerance and average_hip_angle<15 and average_knee_angle>120:  
          
            current_horizontal_position = 'valid'  # Set position status to invalid when landmarks are not clearly visible
            
        else:
            cv2.putText(image, "Get in position or adjust frame", ((image.shape[1] - cv2.getTextSize("Get in position or adjust frame", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2, (image.shape[0] + cv2.getTextSize("Get in position or adjust frame", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][1]) // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            current_horizontal_position = 'invalid'  # Set position status to invalid when landmarks are not clearly visible
            return image  # Return the image with the warning text

        # Assume initial position based on elbow angle (simplified heuristic)
        if average_elbow_angle > (acceptable_ranges['up']['elbow'] + acceptable_ranges['down']['elbow']) / 2:
            self.current_position = 'up'
        else:
            self.current_position = 'down'

        # Function to determine color based on angle validation
        def get_color_and_feedback(angle, joint):
            target = acceptable_ranges[self.current_position][joint]
            if angle > target + threshold:
                if joint == 'elbow':
                    return (255, 0, 255), "Bend your arms"
                elif joint == 'knee':
                    return (255, 0, 255), "Straighten your legs"
                elif joint == 'shoulder':
                    return (255, 0, 255), "Bring body front, so that the arm is straight"
                elif joint == 'hip':
                    return (255, 0, 255), "Bring hip down"
            elif angle < target - threshold:
                if joint == 'elbow':
                    return (0, 0, 255), "Straighten your arms"
                elif joint == 'knee':
                    return (0, 0, 255), "Straighten your legs"
                elif joint == 'shoulder':
                    return (0, 0, 255), "Bring body back, so that the arm is straight"
                elif joint == 'hip':
                    return (0, 0, 255), "Bring hip up"
            return (0, 255, 0), "Good position"

        # Validate and display each angle
        angles = {
            'Elbow Avg': average_elbow_angle,
            'Shoulder Avg': average_shoulder_angle,
            'Hip Avg': average_hip_angle,
            'Knee Avg': average_knee_angle
        }
        y_pos = 100
        for key, angle in angles.items():
            joint = key.lower().split()[0]
            color, feedback = get_color_and_feedback(angle, joint)
            cv2.putText(image, f"{key}: {int(angle)} - {feedback}", (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2, cv2.LINE_AA)
            y_pos += 40

        # Display Up/Down
        position_text = f"Position: {self.current_position.capitalize()}"
        position_text_width = cv2.getTextSize(position_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]
        cv2.putText(image, position_text, (image.shape[1] - position_text_width - 10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # Display Horizontal
        horizontal_text = f"Ho: {current_horizontal_position.capitalize()}"
        horizontal_text_width = cv2.getTextSize(horizontal_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]
        cv2.putText(image, horizontal_text, (image.shape[1] - horizontal_text_width - 10, y_pos + 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

        # Display Horizontal Angle
        horizontal_angle_text = f"HoA: {round(angle_with_horizontal)}"
        horizontal_angle_text_width = cv2.getTextSize(horizontal_angle_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]
        cv2.putText(image, horizontal_angle_text, (image.shape[1] - horizontal_angle_text_width - 10, y_pos + 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2, cv2.LINE_AA)

       
        # Count 
        if current_horizontal_position == 'valid':
            if self.current_position == 'down' and self.previous_position == 'up':
                self.is_down = True
            elif self.current_position == 'up' and self.previous_position == 'down' and self.is_down:
                self.count += 1
                self.is_down = False  # Reset for the next cycle
                winsound.Beep(1000, 200)  # Beep to signal a completed pushup
            self.previous_position = self.current_position


  


    def run(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened() and self.running:
            success, image = cap.read()
            if not success or not self.running:
                break

            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)

            if results.pose_landmarks:
                self.process_and_display_angles(image, results.pose_landmarks.landmark)
                mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

                cv2.putText(image, f"Pushups: {self.count}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
                if self.feedback_depth:
                    cv2.putText(image, self.feedback_depth, (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 255), 2, cv2.LINE_AA)
                if self.feedback_alignment:
                    cv2.putText(image, self.feedback_alignment, (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (100, 255, 255), 2, cv2.LINE_AA)

            cv2.namedWindow("Push-up Counter", cv2.WINDOW_NORMAL)
            cv2.imshow("Push-up Counter", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


        cap.release()
        cv2.destroyAllWindows()
       
    def stop(self):
        self.running = False  # Method to stop the running counter    


if __name__ == "__main__":
    pushup_counter = PushupCounter()
    pushup_counter.run()