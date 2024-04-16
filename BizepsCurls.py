import cv2
import mediapipe as mp
import winsound
import math

# Funktion zur Berechnung des Winkels zwischen drei Punkten
def calculate_angle(a, b, c):
    ang = abs(math.degrees(math.atan2(c[1] - b[1], c[0] - b[0]) - math.atan2(a[1] - b[1], a[0] - b[0])))
    return ang if ang <= 180 else 360 - ang

# Initialisierung von MediaPipe
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

# MediaPipe Pose Modell laden
pose = mp_pose.Pose()

# Video-Capture starten
cap = cv2.VideoCapture(0)

# Variablen initialisieren
counter = 0
angle_high = 0
angle_low = 0
is_counted = False


# Schwellenwinkel für die "hoch"- und "runter"-Position
threshold_high = 60  # Winkel für die "hoch"-Position
threshold_low = 150   # Winkel für die "runter"-Position

while cap.isOpened():
    ret, frame = cap.read()

    # Umkehren des Bildes (horizontal)
    frame = cv2.flip(frame, 1)

    # Bild zu MediaPipe Pose umwandeln
    img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(img_rgb)

    # Zeichnen der Pose-Schicht
    if results.pose_landmarks:
        mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # Punkte für den Winkel zwischen Schulter, Ellenbogen und Handgelenk
        left_shoulder = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * frame.shape[1]),
                         int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * frame.shape[0])]
        left_elbow = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].x * frame.shape[1]),
                      int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y * frame.shape[0])]
        left_wrist = [int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].x * frame.shape[1]),
                      int(results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_WRIST].y * frame.shape[0])]

        # Winkel berechnen
        angle_high = calculate_angle(left_shoulder, left_elbow, left_wrist)
        
        # Winkel an der Ellenbogen-Landmark anezige
        cv2.putText(frame, f'Elbow Angle: {int(angle_high)}', (left_elbow[0], left_elbow[1] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        # Text für den Winkelbereich "higher" und "lower" basierend auf den Schwellenwerten
        if angle_high < 90:
            text_higher = "Higher"
        elif angle_high < 150:
            text_higher = "Lower"
        else:
            text_higher = ""

        # Text für den Winkelbereich "lower"
        if angle_high < 90:
            text_lower = ""
        elif angle_high < 150:
            text_lower = "Lower"
        else:
            text_lower = "Higher"
    
        # Text für den Winkelbereich "hoch genug" und "tief genug" basierend auf den Schwellenwerten
        if angle_high <= threshold_high:
            text_high_enough = "Hoch genug"
        else:
            text_high_enough = ""

        if angle_low >= threshold_low:
            text_low_enough = "Tief genug"
        else:
            text_low_enough = ""

        # Text für "hoch genug" und "tief genug" anzeigen
        cv2.putText(frame, f'{text_high_enough}', (20, frame.shape[0] - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        cv2.putText(frame, f'{text_low_enough}', (20, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Winkelbereich "higher" anzeigen unten links
        cv2.putText(frame, f'{text_higher}', (20, frame.shape[0] - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Winkelbereich "lower" anzeigen direkt unter "higher"
        cv2.putText(frame, f'{text_lower}', (20, frame.shape[0] - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        # Zähler auf dem Bildschirm anzeigen
        cv2.putText(frame, f'Curls: {counter}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Bizeps Curl Bedingungen prüfen
        if not is_counted and angle_high < threshold_high:
            is_counted = True
        elif is_counted and angle_high > threshold_low:
            angle_low = calculate_angle(left_shoulder, left_elbow, left_wrist)
            if angle_low > threshold_low:
                counter += 1
                winsound.Beep(1000, 200)  # Piepton für erfolgreiche Curl
                is_counted = False  # Zurücksetzen des Zählers für die nächste Wiederholung



    # Winkel auf dem Bildschirm anzeigen
    cv2.putText(frame, f'Angle High: {int(angle_high)}', (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(frame, f'Angle Low: {int(angle_low)}', (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Zähler auf dem Bildschirm anzeigen
    cv2.putText(frame, f'Curls: {counter}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Bizeps Curls Counter', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break  # Beende die Schleife, wenn 'q' gedrückt wird

cap.release()
cv2.destroyAllWindows()
