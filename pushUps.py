import cv2
import mediapipe as mp
import winsound
import time

class PushupCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.count = 0
        self.is_down = False
        self.feedback_depth = ""  # Feedback zur Tiefe
        self.feedback_alignment = ""  # Feedback zur Ausrichtung
        self.previous_left_elbow = None
        self.previous_right_elbow = None
        self.bewegung = False
        self.letzte_bewegung_zeit = None

    def update_feedback(self, landmarks):

        aktuelle_zeit = time.time()

        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value].y
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y
        right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value].y
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y
        nose = landmarks[mp.solutions.pose.PoseLandmark.NOSE.value].y
        left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y
        right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP.value].y

        # Feedback zur Tiefe
        if left_elbow > left_shoulder and right_elbow > right_shoulder:
            self.feedback_depth = "Weiter runtergehen mit dem Körper"
        else:
            self.feedback_depth = "Gute Tiefe!"

        # Feedback zur Ausrichtung
        if nose > ((left_hip + right_hip) / 2):
            self.feedback_alignment = "Oberkörper und Beine in einer Linie halten"
        else:
            self.feedback_alignment = "Gute Ausrichtung!"

        # Prüfen, ob die Bewegung seit dem letzten Frame signifikant war
        if self.previous_left_elbow is not None and self.previous_right_elbow is not None:
            left_movement = abs(left_elbow - self.previous_left_elbow)
            right_movement = abs(right_elbow - self.previous_right_elbow)
            
            if left_movement < 0.09 and right_movement < 0.09 and not self.bewegung:
                self.feedback_depth = "Bitte starten Sie die Bewegung."
                self.feedback_alignment = ""
                # Wenn keine Bewegung erkannt wird, setzen Sie die letzte Bewegungszeit zurück
                self.letzte_bewegung_zeit = aktuelle_zeit
            else:
                if self.letzte_bewegung_zeit is None or aktuelle_zeit - self.letzte_bewegung_zeit >= 3:
                    self.bewegung = True


        self.previous_left_elbow = left_elbow
        self.previous_right_elbow = right_elbow

    def count_pushups(self, landmarks):
        self.update_feedback(landmarks)
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value].y
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y
        right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value].y
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y

        if left_elbow > left_shoulder and right_elbow > right_shoulder:
            self.is_down = True
        elif left_elbow < left_shoulder and right_elbow < right_shoulder and self.is_down:
            self.count += 1
            self.is_down = False
            winsound.Beep(1000, 200)  # Frequency: 1000 Hz, Duration: 200 ms

    def run(self):
        cap = cv2.VideoCapture(0)
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                continue

            image = cv2.flip(image, 1)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.pose.process(image_rgb)

            if results.pose_landmarks:
                self.count_pushups(results.pose_landmarks.landmark)

                cv2.putText(
                    image,
                    f"Pushups: {self.count}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 0),
                    2,
                    cv2.LINE_AA,
                )

                # Tiefe-Feedback anzeigen
                if self.feedback_depth:
                    cv2.putText(
                        image,
                        self.feedback_depth,
                        (10, 100),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (100, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                # Ausrichtungs-Feedback anzeigen
                if self.feedback_alignment:
                    cv2.putText(
                        image,
                        self.feedback_alignment,
                        (10, 130),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (100, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                mp.solutions.drawing_utils.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )

            cv2.namedWindow("Push-up Counter", cv2.WINDOW_NORMAL)
            cv2.imshow("Push-up Counter", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    pushup_counter = PushupCounter()
    pushup_counter.run()
