import cv2
import os

def extract_frames(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_interval = fps  # 1 frame per second

    frame_id = 0
    video_name = os.path.basename(video_path).split('.')[0]

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_number = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
        if frame_number % frame_interval == 0:
            timestamp = int(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000)
            frame_filename = f"{video_name}_frame{frame_id}_t{timestamp}.jpg"
            frame_path = os.path.join(output_dir, frame_filename)
            cv2.imwrite(frame_path, frame)
            print(f"Saved: {frame_path}")
            frame_id += 1

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    extract_frames("input_videos/interview.mp4", "static/frames")
