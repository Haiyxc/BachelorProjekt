import cv2
import mediapipe as mp
import math
import winsound  # Für den Ton unter Windows
import time

# MediaPipe Initialisierung
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# Webcam Initialisierung
cap = cv2.VideoCapture(0)

# Zählervariable für die erfolgreichen Übungen
exercise_count = 0

# Zeitstempel für die letzte erfolgreiche Übung
last_exercise_time = time.time()

# Mindestabstand zwischen zwei erfolgreichen Übungen in Sekunden
exercise_interval = 3

# Startzeit des Programms
start_time = time.time()

# Statusvariable, um den aktuellen Status der Übung zu verfolgen
# 0: Arme hängen seitlich herunter, 1: Arme werden angehoben, 2: Arme werden heruntergelassen
exercise_status = 0

# Funktion zur Berechnung des Winkels zwischen drei Punkten
def calculate_angle(a, b, c):
    radians = abs(a - b - c)
    angle = radians * (180.0 / 3.14)
    return angle

# Funktion zum Signalisieren einer erfolgreichen Übung mit Zählererhöhung und Piepton
def signal_success():
    global exercise_count, last_exercise_time
    exercise_count += 1
    last_exercise_time = time.time()
    print("Erfolgreiche Übung! Anzahl:", exercise_count)
    winsound.Beep(1000, 200)  # Anpassen der Tonfrequenz und Dauer nach Bedarf

# Funktion zur Überprüfung der Seitheben-Bewegung
def check_side_raise(left_shoulder, left_elbow, left_wrist, right_shoulder, right_elbow, right_wrist):
    global exercise_status
    # Überprüfen Sie den aktuellen Status der Übung
    if exercise_status == 0:
        # Überprüfen Sie, ob die Arme seitlich herunterhängen
        if left_shoulder < left_elbow and right_shoulder < right_elbow:
            exercise_status = 1
        else:
            print("Warnung: Arme nicht seitlich herunterhängend. Bitte stellen Sie sicher, dass Ihre Arme locker an Ihren Seiten hängen.")
    elif exercise_status == 1:
        # Überprüfen Sie, ob die Arme in einem 80-Grad-Winkel angehoben werden
        if left_shoulder > left_elbow and right_shoulder > right_elbow:
            exercise_status = 2
        else:
            print("Warnung: Arme nicht im 80-Grad-Winkel angehoben. Versuchen Sie, Ihre Arme höher zur Seite zu heben.")
    elif exercise_status == 2:
        # Überprüfen Sie, ob die Arme wieder heruntergelassen werden
        if left_shoulder < left_elbow and right_shoulder < right_elbow:
            return True
        else:
            print("Warnung: Arme nicht wieder heruntergelassen. Senken Sie Ihre Arme wieder zur Seite.")
    return False

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Kein Bild von der Webcam.")
        break

    # Umwandlung des Bildes in RGB (MediaPipe erwartet RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Erkennung der Pose
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        # Zeichne die Landmarken
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Extrahiere die Positionen der relevanten Landmarken
        left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y
        left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y
        left_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y

        right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
        right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].y
        right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y

        # Überprüfen Sie die Seitheben-Bewegung
        if check_side_raise(left_shoulder, left_elbow, left_wrist, right_shoulder, right_elbow, right_wrist):
            # Überprüfen Sie, ob genügend Zeit seit der letzten Übung vergangen ist
            if time.time() - last_exercise_time > exercise_interval:
                signal_success()  # Erfolgreiche Übung signalisieren
            # Setzen Sie den Status der Übung zurück, um die nächste Übung zu erfassen
            exercise_status = 0

    # Text für den Counter
    counter_text = "Übungen: {}".format(exercise_count)

    # Text für die Stoppuhr
    elapsed_time = time.time() - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    stopwatch_text = "Stoppuhr: {:02}:{:02}:{:02}".format(int(hours), int(minutes), int(seconds))

    # Texte auf dem Bild anzeigen
    cv2.putText(image, counter_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(image, stopwatch_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow('Seitheben-Erkennung', image)

    if cv2.waitKey(5) & 0xFF == 27:  # Escape-Taste zum Beenden
        break

# Aufräumen
cap.release()
cv2.destroyAllWindows()
