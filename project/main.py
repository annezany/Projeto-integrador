"""Move the mouse pointer from left-eye movement captured by a webcam."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from urllib.request import urlretrieve

import cv2
import mediapipe as mp
import pyautogui
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


LEFT_IRIS = (474, 475, 476, 477)
LEFT_EYE = (362, 263, 386, 374, 385, 380, 390, 373)
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
MODEL_PATH = Path(__file__).with_name("models") / "face_landmarker.task"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="Webcam device index")
    parser.add_argument("--smoothing", type=float, default=0.22, help="Cursor smoothing from 0.05 to 1.0")
    parser.add_argument("--width", type=int, default=960, help="Preview width")
    return parser.parse_args()


def point(landmarks: object, index: int, width: int, height: int) -> tuple[int, int]:
    landmark = landmarks[index]
    return int(landmark.x * width), int(landmark.y * height)


def normalized_eye_position(landmarks: object, width: int, height: int) -> tuple[float, float]:
    iris = [point(landmarks, index, width, height) for index in LEFT_IRIS]
    eye = [point(landmarks, index, width, height) for index in LEFT_EYE]
    iris_x = sum(x for x, _ in iris) / len(iris)
    iris_y = sum(y for _, y in iris) / len(iris)
    min_x, max_x = min(x for x, _ in eye), max(x for x, _ in eye)
    min_y, max_y = min(y for _, y in eye), max(y for _, y in eye)
    horizontal = (iris_x - min_x) / max(max_x - min_x, 1)
    vertical = (iris_y - min_y) / max(max_y - min_y, 1)
    return max(0.0, min(1.0, horizontal)), max(0.0, min(1.0, vertical))


def draw_status(frame: object, paused: bool, fps: float) -> None:
    status = "PAUSED (press P to resume)" if paused else "TRACKING"
    cv2.putText(frame, f"{status} | FPS {fps:.0f} | Q quits", (18, 32), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (40, 230, 180), 2)


def ensure_model() -> Path:
    if not MODEL_PATH.exists():
        MODEL_PATH.parent.mkdir(exist_ok=True)
        print("Downloading the MediaPipe face model (about 3 MB)...")
        urlretrieve(MODEL_URL, MODEL_PATH)
    return MODEL_PATH


def run() -> int:
    args = parse_args()
    if not 0.05 <= args.smoothing <= 1.0:
        raise ValueError("--smoothing must be between 0.05 and 1.0")

    screen_width, screen_height = pyautogui.size()
    pyautogui.PAUSE = 0
    pyautogui.FAILSAFE = True
    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        print(f"Could not open webcam {args.camera}. Try --camera 1.", file=sys.stderr)
        return 1

    landmarker = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path=str(ensure_model())),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
        min_face_detection_confidence=0.6,
        min_face_presence_confidence=0.6,
        min_tracking_confidence=0.6,
        output_face_blendshapes=False,
        output_facial_transformation_matrixes=False,
    ))
    paused = False
    cursor_x, cursor_y = screen_width / 2, screen_height / 2
    previous_time = time.perf_counter()
    timestamp_ms = 0

    try:
        while True:
            success, frame = camera.read()
            if not success:
                continue
            frame = cv2.flip(frame, 1)
            height, width = frame.shape[:2]
            timestamp_ms += 33
            image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            result = landmarker.detect_for_video(image, timestamp_ms)

            if result.face_landmarks:
                landmarks = result.face_landmarks[0]
                x_ratio, y_ratio = normalized_eye_position(landmarks, width, height)
                if not paused:
                    target_x = x_ratio * screen_width
                    target_y = y_ratio * screen_height
                    cursor_x += (target_x - cursor_x) * args.smoothing
                    cursor_y += (target_y - cursor_y) * args.smoothing
                    pyautogui.moveTo(round(cursor_x), round(cursor_y), _pause=False)

                for index in LEFT_IRIS:
                    cv2.circle(frame, point(landmarks, index, width, height), 2, (0, 255, 255), -1)

            now = time.perf_counter()
            fps = 1 / max(now - previous_time, 0.001)
            previous_time = now
            draw_status(frame, paused, fps)
            cv2.imshow("Left Eye Mouse", cv2.resize(frame, (args.width, int(height * args.width / width))))
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q") or key == 27:
                break
            if key == ord("p"):
                paused = not paused
    finally:
        camera.release()
        landmarker.close()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(run())
    except pyautogui.FailSafeException:
        print("PyAutoGUI fail-safe triggered; exiting.", file=sys.stderr)
        raise SystemExit(1)
