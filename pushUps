import cv2
import mediapipe as mp
import winsound

class PushupCounter:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.count = 0
        self.is_down = False  # Change to is_down for push-up logic

    def count_pushups(self, landmarks):
        # Use shoulders and elbows to determine push-up motion
        left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW.value].y
        left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y

        right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW.value].y
        right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER.value].y

        # Checking if elbows are below shoulders (push-up down position)
        if left_elbow > left_shoulder and right_elbow > right_shoulder:
            self.is_down = True
        # Checking if elbows are above shoulders and push-up was previously in the down position
        elif left_elbow < left_shoulder and right_elbow < right_shoulder and self.is_down:
            self.count += 1
            self.is_down = False
            # Play beep sound
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

                # Change text to "Pushups"
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

                mp.solutions.drawing_utils.draw_landmarks(
                    image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS
                )

            cv2.namedWindow("Push-up Counter", cv2.WINDOW_NORMAL)  # Change window name to "Push-up Counter"
            cv2.imshow("Push-up Counter", image)  # Change window name here as well

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    pushup_counter = PushupCounter()
    pushup_counter.run()
