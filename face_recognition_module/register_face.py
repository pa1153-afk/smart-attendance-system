import cv2
import os
import time

print("🔥 register_face.py is running 🔥")


def register_face(student_id, student_name, num_images=15, dataset_path="dataset"):
    save_dir = os.path.join(dataset_path, student_id)
    os.makedirs(save_dir, exist_ok=True)
    print(f"\n[INFO] Saving images to: {save_dir}")

    # Load face detector
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_cascade = cv2.CascadeClassifier(cascade_path)

    if face_cascade.empty():
        print("[ERROR] Could not load face cascade classifier.")
        return False

    # Try webcam 0, fallback to 1
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[WARNING] Camera 0 failed, trying camera 1...")
        cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("[ERROR] Could not access webcam.")
        return False

    print(f"\n[INFO] Starting registration for: {student_name} ({student_id})")

    count = 0
    last_capture = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            print("[ERROR] Failed to read frame.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(80, 80))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            current_time = time.time()
            if current_time - last_capture >= 0.3 and count < num_images:
                face_img = gray[y:y+h, x:x+w]
                face_img = cv2.resize(face_img, (200, 200))

                img_path = os.path.join(save_dir, f"{student_id}_{count+1}.jpg")
                cv2.imwrite(img_path, face_img)

                count += 1
                last_capture = current_time
                print(f"[✓] Captured {count}/{num_images}")

        cv2.putText(frame, f"{count}/{num_images}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        cv2.imshow("Face Registration", frame)

        if count >= num_images:
            print("\n[SUCCESS] Done capturing images")
            break

        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("\n[INFO] Quit pressed")
            break

    cap.release()
    cv2.destroyAllWindows()

    return count > 0


# ===== MAIN RUN =====
if __name__ == "__main__":
    print("=== Face Registration Started ===")

    student_id = input("Enter Student ID: ").strip()
    student_name = input("Enter Student Name: ").strip()

    if not student_id or not student_name:
        print("[ERROR] Empty input")
    else:
        success = register_face(student_id, student_name)
        if success:
            print("[DONE] Registration complete")
        else:
            print("[FAILED] No images captured")