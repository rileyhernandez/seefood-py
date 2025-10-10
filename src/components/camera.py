import subprocess
import cv2
import time

DEVICE = "/dev/video4"
WIDTH = 1280
HEIGHT = 720
PIX_FMT = "MJPG"
FPS = 10

BRIGHTNESS = 0
CONTRAST = 22
SATURATION = 120
GAIN = 0
WHITE_BALANCE_TEMP = 4624
SHARPNESS = 3
AUTO_EXPOSURE = 1
EXPOSURE_TIME = 250
FOCUS_ABSOLUTE = 280
FOCUS_AUTO_CONTINUOUS = 0
WHITE_BALANCE_AUTO = 0


def apply_v4l2_settings_initial():
    """Apply all v4l2-ctl settings before opening the stream."""
    subprocess.run([
        "v4l2-ctl", "-d", DEVICE,
        "--set-parm", str(FPS),
        "--set-fmt-video", f"width={WIDTH},height={HEIGHT},pixelformat={PIX_FMT}",
    ], check=True)

    subprocess.run([
        "v4l2-ctl", "-d", DEVICE,
        "--set-ctrl", f"brightness={BRIGHTNESS}",
        "--set-ctrl", f"contrast={CONTRAST}",
        "--set-ctrl", f"saturation={SATURATION}",
        "--set-ctrl", f"gain={GAIN}",
        "--set-ctrl", f"sharpness={SHARPNESS}",
        "--set-ctrl", f"white_balance_automatic={WHITE_BALANCE_AUTO}",
        "--set-ctrl", f"white_balance_temperature={WHITE_BALANCE_TEMP}",
        "--set-ctrl", f"auto_exposure={AUTO_EXPOSURE}",
        "--set-ctrl", f"exposure_time_absolute={EXPOSURE_TIME}",
        "--set-ctrl", f"focus_automatic_continuous={FOCUS_AUTO_CONTINUOUS}",
        "--set-ctrl", f"focus_absolute={FOCUS_ABSOLUTE}"
    ], check=True)


def apply_critical_settings():
    """Reapply critical settings that tend to reset after stream opens."""
    subprocess.run([
        "v4l2-ctl", "-d", DEVICE,
        "--set-ctrl", f"auto_exposure={AUTO_EXPOSURE}",
        "--set-ctrl", f"exposure_time_absolute={EXPOSURE_TIME}",
        "--set-ctrl", f"focus_automatic_continuous={FOCUS_AUTO_CONTINUOUS}",
        "--set-ctrl", f"focus_absolute={FOCUS_ABSOLUTE}"
    ], check=True)


class Camera:
    def __init__(self, device=DEVICE):
        # Apply all settings before opening the stream
        apply_v4l2_settings_initial()
        time.sleep(0.5)

        # Open the stream
        self.cap = cv2.VideoCapture(device)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at {device}")

        # Set OpenCV properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, FPS)

        # Let the stream stabilize
        time.sleep(0.5)

        # Reapply critical settings that may have reset
        apply_critical_settings()

        # Allow settings to take effect
        time.sleep(0.5)

    def capture(self, filename: str):
        """Grab a fresh frame and save it to a file."""
        frame = None
        # Flush 5 frames to avoid stale buffers
        for _ in range(5):
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed to grab frame from camera")
        cv2.imwrite(filename, frame)

    def release(self):
        """Release the camera stream."""
        self.cap.release()