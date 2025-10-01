import cv2
import base64
from dataclasses import dataclass
from pathlib import Path

@dataclass
class Camera:
    device_index: int = 0
    max_dim: int = 1024
    warmup_frames: int = 10
    burst_size: int = 5  # how many frames to test for sharpness

    def __post_init__(self):
        # Open the camera once
        self.cap = cv2.VideoCapture(self.device_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open /dev/video{self.device_index}")

    def _sharpest_frame(self):
        """Capture multiple frames and return the sharpest one."""
        best_score, best_frame = -1, None
        for _ in range(self.burst_size):
            ret, frame = self.cap.read()
            if not ret:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            score = cv2.Laplacian(gray, cv2.CV_64F).var()  # variance = focus measure
            if score > best_score:
                best_score, best_frame = score, frame
        if best_frame is None:
            raise RuntimeError("Failed to capture any frames")
        return best_frame

    def capture(self, save_path=None):
        """
        Captures the sharpest image from the camera and returns it as a base64 encoded data URI.
        Optionally saves the original captured image to save_path.
        """
        # Warm up (throw away a few frames)
        for _ in range(self.warmup_frames):
            ret, _ = self.cap.read()
            if not ret:
                raise RuntimeError("Camera did not return frame during warmup")

        # Get the sharpest frame out of a burst
        frame = self._sharpest_frame()

        # Save original frame if requested
        if save_path:
            p = Path(save_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            if not cv2.imwrite(str(p), frame):
                raise RuntimeError(f"Failed to save image to {save_path}")
            print(f"Image successfully saved to: {p.resolve()}")

        # Resize for base64 output
        h, w = frame.shape[:2]
        if max(h, w) > self.max_dim:
            scale = self.max_dim / max(h, w)
            new_w, new_h = int(w * scale), int(h * scale)
            frame = cv2.resize(frame, (new_w, new_h))

        # Encode as JPEG → base64
        success, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not success:
            raise RuntimeError("Failed to encode image")

        img_bytes = buf.tobytes()
        img_b64 = base64.b64encode(img_bytes).decode("utf-8")
        return f"data:image/jpeg;base64,{img_b64}"

    def release(self):
        """Release the camera when done"""
        self.cap.release()


if __name__ == "__main__":
    cam = Camera(device_index=4, max_dim=1024, warmup_frames=10, burst_size=20)
    try:
        print("Attempting to capture and save...")
        data_uri = cam.capture(save_path=".images/test.jpg")
        print("Capture and save process completed.")
    finally:
        cam.release()
