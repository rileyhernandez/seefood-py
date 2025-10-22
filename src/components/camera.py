import subprocess
import cv2
import time
from ..config import Camera as CameraConfig

def apply_v4l2_settings_initial(config: CameraConfig):
    """Apply all v4l2-ctl settings before opening the stream."""
    device = f"/dev/video{config.device_index}"
    subprocess.run([
        "v4l2-ctl", "-d", device,
        "--set-parm", str(config.fps),
        "--set-fmt-video", f"width={config.width},height={config.height},pixelformat={config.pix_fmt}",
    ], check=True)

    subprocess.run([
        "v4l2-ctl", "-d", device,
        "--set-ctrl", f"brightness={config.brightness}",
        "--set-ctrl", f"contrast={config.contrast}",
        "--set-ctrl", f"saturation={config.saturation}",
        "--set-ctrl", f"gain={config.gain}",
        "--set-ctrl", f"sharpness={config.sharpness}",
        "--set-ctrl", f"white_balance_automatic={config.white_balance_auto}",
        "--set-ctrl", f"white_balance_temperature={config.white_balance_temp}",
        "--set-ctrl", f"auto_exposure={config.auto_exposure}",
        "--set-ctrl", f"exposure_time_absolute={config.exposure_time}",
        "--set-ctrl", f"focus_automatic_continuous={config.focus_auto_continuous}",
        "--set-ctrl", f"focus_absolute={config.focus_absolute}"
    ], check=True)


def apply_critical_settings(config: CameraConfig):
    """Reapply critical settings that tend to reset after stream opens."""
    device = f"/dev/video{config.device_index}"
    subprocess.run([
        "v4l2-ctl", "-d", device,
        "--set-ctrl", f"auto_exposure={config.auto_exposure}",
        "--set-ctrl", f"exposure_time_absolute={config.exposure_time}",
        "--set-ctrl", f"focus_automatic_continuous={config.focus_auto_continuous}",
        "--set-ctrl", f"focus_absolute={config.focus_absolute}"
    ], check=True)


class Camera:
    def __init__(self, config: CameraConfig):
        # Apply all settings before opening the stream
        apply_v4l2_settings_initial(config)
        time.sleep(0.5)

        # Open the stream
        self.cap = cv2.VideoCapture(f"/dev/video{config.device_index}")
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at /dev/video{config.device_index}")

        # Set OpenCV properties
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
        self.cap.set(cv2.CAP_PROP_FPS, config.fps)

        # Let the stream stabilize
        time.sleep(0.5)

        # Reapply critical settings that may have reset
        apply_critical_settings(config)

        # Allow settings to take effect
        time.sleep(0.5)

    def capture(self, image_format: str = ".jpg") -> bytes:
        """
        Capture a frame from the camera.
        Returns as bytes
        """
        frame = None
        for _ in range(5):  # flush stale frames
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError("Failed to grab frame from camera")

        # Encode the image in memory
        success, buffer = cv2.imencode(image_format, frame)
        if not success:
            raise RuntimeError("Failed to encode frame to bytes")
        return buffer.tobytes()

    def release(self):
        """Release the camera stream."""
        self.cap.release()