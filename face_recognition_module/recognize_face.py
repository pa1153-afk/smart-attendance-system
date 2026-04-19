import sys
import os

# 🔥 FIX: add project root BEFORE imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import face_recognition
import cv2
import numpy as np
from database.db import mark_attendance

print("🔥 recognize_face.py STARTED 🔥", flush=True)


# ===============================
# LOAD DATASET
# ===============================
def load_known_faces(dataset_path="dataset"):
    known_encodings = []
    known_ids = []

    print("[INFO] Loading dataset...", flush=True)

    if not os.path.exists(dataset_path):
        print("[ERROR] dataset folder not found", flush=True)
        return [], []

    for student_id in os.listdir(dataset_path):
        student_dir = os.path.join(dataset_path, student_id)

        if not os.path.isdir(student_dir):
            continue

        print(f"[INFO] Processing {student_id}", flush=True)

        for file in os.listdir(student_dir):
            if file.lower().endswith(".jpg"):
                path = os.path.join(student_dir, file)

                image = face_recognition.load_image_file(path)
                encodings = face_recognition.face_encodings(image)

                if encodings:
                    known_encodings.append(encodings[0])
                    known_ids.append(student_id)

    print(f"[INFO] Loaded {len(known_encodings)} encodings", flush=True)
    return known_encodings, known_ids


# ===============================
# RECOGNITION
# ===============================
def run_recognition(known_encodings, known_ids):
    print("[INFO] Starting camera...", flush=True)

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[WARNING] Camera 0 failed, trying camera 1...", flush=True)
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("[ERROR] Camera not opening", flush=True)
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Frame read failed", flush=True)
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb)
        face_encodings = face_recognition.face_encodings(rgb, face_locations)

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):

            name = "Unknown"

            if len(known_encodings) > 0:
                face_distances = face_recognition.face_distance(known_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)

                # 🔥 Better accuracy threshold
                if face_distances[best_match_index] < 0.45:
                    name = known_ids[best_match_index]
                    print(f"[MATCH] {name} ({face_distances[best_match_index]:.3f})", flush=True)

                    # 🔥 mark attendance only when valid match
                    if mark_attendance(name):
                         print("[INFO] Attendance marked, stopping camera...", flush=True)
                         cap.release()
                         cv2.destroyAllWindows()
                         return
                else:
                    print(f"[UNKNOWN] ({min(face_distances):.3f})", flush=True)

            cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)
            cv2.putText(frame, name, (left, top-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)

        cv2.imshow("Face Recognition", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] Stopping...", flush=True)
            break

    cap.release()
    cv2.destroyAllWindows()


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    print("=== FACE RECOGNITION START ===", flush=True)

    encodings, ids = load_known_faces()

    if not encodings:
        print("[ERROR] No data found", flush=True)
    else:
        run_recognition(encodings, ids)