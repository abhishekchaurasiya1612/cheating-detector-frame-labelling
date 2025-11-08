import cv2
import os
import json

def auto_label_frames(frame_dir, output_json="predicted_labels.json"):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    results = []

    for frame_file in sorted(os.listdir(frame_dir)):
        if not frame_file.endswith(".jpg"):
            continue

        frame_path = os.path.join(frame_dir, frame_file)
        frame = cv2.imread(frame_path)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        h, w = frame.shape[:2]
        label = "Not Cheating"

        for (x, y, fw, fh) in faces:
            cx, cy = x + fw // 2, y + fh // 2
            left, right = w // 3, 2 * w // 3
            top_half = h // 2

            if cy > top_half or cx < left or cx > right:
                label = "Cheating"

            color = (0, 255, 0) if label == "Not Cheating" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + fw, y + fh), color, 2)
            cv2.putText(frame, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        cv2.imwrite(frame_path, frame)

        results.append({
            "frame_name": frame_file,
            "predicted_label": label
        })

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"✅ Auto-labeled frames saved to {output_json}")

if __name__ == "__main__":
    auto_label_frames("static/frames")
