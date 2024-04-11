import cv2
import mediapipe as mp
import winsound

class BicepCurlCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.count = 0
        self.is_down = False

    def count_bicep_curls(self, landmarks):
        # Berechne die vertikale Position der mittleren Rückenlandmarken
        spine_landmarks_y = [landmarks[i].y for i in range(12, 24)]  # Landmarken-IDs zwischen Schulter und Hüfte
        avg_y = sum(spine_landmarks_y) / len(spine_landmarks_y)

        # Überprüfe die Rückenhaltung (obere und untere Landmarken)
        upper_spine_y = landmarks[12].y
        lower_spine_y = landmarks[23].y

        # Überprüfe, ob der Rücken gerade ist (obere und untere Landmarken über oder unter dem Durchschnitt)
        if (upper_spine_y > avg_y and lower_spine_y > avg_y) or (upper_spine_y < avg_y and lower_spine_y < avg_y):
            self.is_down = True
        elif self.is_down and ((upper_spine_y < avg_y and lower_spine_y > avg_y) or (upper_spine_y > avg_y and lower_spine_y < avg_y)):
            self.count += 1
            self.is_down = False
            winsound.Beep(1000, 200)

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
                self.count_bicep_curls(results.pose_landmarks.landmark)

                cv2.putText(
                    image,
                    f"Bicep Curls: {self.count}",
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 0, 0),
                    2,
                    cv2.LINE_AA,
                )

                mp.solutions.drawing_utils.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )

            cv2.namedWindow("Bicep Curl Counter", cv2.WINDOW_NORMAL)
            cv2.imshow("Bicep Curl Counter", image)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    bicep_curl_counter = BicepCurlCounter()
    bicep_curl_counter.run()
