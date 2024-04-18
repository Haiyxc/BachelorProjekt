import cv2
import mediapipe as mp
import numpy as np

class LateralRaiseCounter:
    def __init__(self):
        self.running = True
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.count = 0
        self.is_up = False
        self.horizontal_tolerance = 50

    def calculate_angle(self, landmark1, landmark2, landmark3):
        # Funktion zur Berechnung des Winkels zwischen drei Landmarken
        vector1 = np.array([landmark1.x - landmark2.x, landmark1.y - landmark2.y])
        vector2 = np.array([landmark3.x - landmark2.x, landmark3.y - landmark2.y])
        unit_vector1 = vector1 / np.linalg.norm(vector1)
        unit_vector2 = vector2 / np.linalg.norm(vector2)
        dot_product = np.dot(unit_vector1, unit_vector2)
        angle = np.arccos(dot_product) * (180.0 / np.pi)
        return angle

    def process_and_display_angles(self, image, landmarks):
        if landmarks:
            # Schwellenwert für die Sichtbarkeit der Landmarken festlegen
            visibility_threshold = 0.1

            # IDs der Landmarken, die überprüft werden sollen
            landmark_ids = [
                mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value,
                mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value,
                mp.solutions.pose.PoseLandmark.LEFT_WRIST.value,
                mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value,
                mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value,
                mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value
            ]

            # Überprüfen, ob alle erforderlichen Landmarken sichtbar sind
            all_landmarks_visible = all(landmarks[i].visibility > visibility_threshold for i in landmark_ids)

            if not all_landmarks_visible:
                # Wenn nicht alle Landmarken sichtbar sind, eine Warnung anzeigen
                cv2.putText(image, "Get in position or adjust frame", ((image.shape[1] - cv2.getTextSize("Get in position or adjust frame", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][0]) // 2, (image.shape[0] + cv2.getTextSize("Get in position or adjust frame", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0][1]) // 2), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
                return image

            # Landmarken extrahieren
            right_hip = landmarks [mp.solutions.pose.PoseLandmark.RIGHT_HIP.value]
            left_hip = landmarks [mp.solutions.pose.PoseLandmark.LEFT_HIP.value]      
            left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value]
            left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value]
            left_wrist = landmarks[mp.solutions.pose.PoseLandmark.LEFT_WRIST.value]
            right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value]
            right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value]
            right_wrist = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_WRIST.value]

            # Winkel für jedes Gelenk berechnen
            left_arm_angle = self.calculate_angle(left_hip, left_shoulder, left_elbow)
            right_arm_angle = self.calculate_angle(right_hip, right_shoulder, right_elbow)
            left_elbow_angle = self.calculate_angle(left_shoulder, left_elbow, left_wrist)
            right_elbow_angle = self.calculate_angle(right_shoulder, right_elbow, right_wrist)

            # Überprüfen, ob die aktuelle Position innerhalb der horizontalen Toleranz liegt
            angle_with_horizontal_left = self.calculate_angle_with_horizontal(left_shoulder, left_elbow)
            angle_with_horizontal_right = self.calculate_angle_with_horizontal(right_shoulder, right_elbow)
            current_horizontal_position = 'invalid' if angle_with_horizontal_left <= self.horizontal_tolerance and angle_with_horizontal_right <= self.horizontal_tolerance else 'valid'

            # Position und Zählen validieren
            if current_horizontal_position == 'valid':
                if (left_arm_angle >= 75 and right_arm_angle >= 75) and (left_elbow_angle >= 150 and right_elbow_angle >= 150):
                    self.is_up = True
                elif (left_elbow_angle >= 150 and right_elbow_angle >= 150) and (self.is_up and left_arm_angle <= 25 and right_arm_angle <= 25) and self.is_up:
                    self.count += 1
                    self.is_up = False

            # Winkel auf dem Bild anzeigen
            cv2.putText(image, f"Right Arm Angle: {int(left_arm_angle)}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Left Arm Angle: {int(right_arm_angle)}", (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Right Elbow Angle: {int(left_elbow_angle)}", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Left Elbow Angle: {int(right_elbow_angle)}", (10, 200), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Count: {self.count}", (10, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f"Horizontal Position: {current_horizontal_position}", (10, 300), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2, cv2.LINE_AA)

        return image

    def calculate_angle_with_horizontal(self, point1, point2):
        # Winkel zwischen dem Vektor von Punkt1 zu Punkt2 und der horizontalen Achse berechnen
        vector = np.array([point2.x - point1.x, point2.y - point1.y])
        horizontal = np.array([1, 0])  # Horizontale Vektor
        unit_vector1 = vector / np.linalg.norm(vector)
        dot_product = np.dot(unit_vector1, horizontal)
        angle = np.arccos(dot_product) * (180.0 / np.pi)
        return angle

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
                image = self.process_and_display_angles(image, results.pose_landmarks.landmark)
                mp.solutions.drawing_utils.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            cv2.namedWindow("Lateral Raise Counter", cv2.WINDOW_NORMAL)
            cv2.imshow("Lateral Raise Counter", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def stop(self):
        self.running = False

if __name__ == "__main__":
    lateral_raise_counter = LateralRaiseCounter()
    lateral_raise_counter.run()
