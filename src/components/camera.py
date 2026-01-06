import subprocess
import cv2
import time
import logging
from ..config import Camera as CameraConfig

# Set up logging for verbose warnings
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_set_v4l2(device: str, setting_type: str, params: dict):
    """
    Applies v4l2 settings one by one. 
    If a setting fails, prints a warning and continues.
    """
    for key, value in params.items():
        # Construct the command based on whether it's a 'ctrl' or a 'parm/fmt'
        if setting_type == "--set-ctrl":
            cmd = ["v4l2-ctl", "-d", device, "--set-ctrl", f"{key}={value}"]
        elif setting_type == "--set-fmt-video":
            # Formatting usually needs to be grouped, but we'll wrap the whole call
            cmd = ["v4l2-ctl", "-d", device, "--set-fmt-video", f"{key}={value}"]
        elif setting_type == "--set-parm":
            cmd = ["v4l2-ctl", "-d", device, "--set-parm", str(value)]
        else:
            continue

        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            logger.warning(f"[V4L2] Failed to set {key} to {value} on {device}. "
                           f"Error: {result.stderr.strip()}")

def apply_v4l2_settings_initial(config: CameraConfig):
    """Apply all v4l2-ctl settings before opening the stream."""
    device = f"/dev/video{config.device_index}"

    # 1. Format and FPS (Often critical for the stream to start)
    safe_set_v4l2(device, "--set-parm", {"fps": config.fps})
    # Width, height, and pix_fmt are usually best set together
    subprocess.run([
        "v4l2-ctl", "-d", device,
        "--set-fmt-video", f"width={config.width},height={config.height},pixelformat={config.pix_fmt}"
    ], capture_output=True)

    # 2. Individual Controls (Often hardware dependent)
    controls = {
        "brightness": config.brightness,
        "contrast": config.contrast,
        "saturation": config.saturation,
        "gain": config.gain,
        "sharpness": config.sharpness,
        "white_balance_automatic": config.white_balance_auto,
        "white_balance_temperature": config.white_balance_temp,
        "auto_exposure": config.auto_exposure,
        "exposure_time_absolute": config.exposure_time,
        "focus_automatic_continuous": config.focus_auto_continuous,
        "focus_absolute": config.focus_absolute
    }
    safe_set_v4l2(device, "--set-ctrl", controls)


def apply_critical_settings(config: CameraConfig):
    """Reapply critical settings that tend to reset after stream opens."""
    device = f"/dev/video{config.device_index}"
    controls = {
        "auto_exposure": config.auto_exposure,
        "exposure_time_absolute": config.exposure_time,
        "focus_automatic_continuous": config.focus_auto_continuous,
        "focus_absolute": config.focus_absolute
    }
    safe_set_v4l2(device, "--set-ctrl", controls)


class Camera:
    def __init__(self, config: CameraConfig):
        self.config = config
        # Apply all settings before opening the stream
        apply_v4l2_settings_initial(config)
        time.sleep(0.5)

        # Open the stream
        self.cap = cv2.VideoCapture(config.device_index, cv2.CAP_V4L2)
        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open camera at /dev/video{config.device_index}")

        # Set OpenCV properties (Syncing OpenCV state with V4L2 state)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.height)
        self.cap.set(cv2.CAP_PROP_FPS, config.fps)

        # Let the stream stabilize
        time.sleep(0.5)

        # Reapply critical settings
        apply_critical_settings(config)
        time.sleep(0.5)

    def capture(self, image_format: str = ".jpg") -> bytes:
        """
        Capture a frame from the camera.
        Returns as bytes.
        """
        frame = None  
        # Flush stale frames from the internal buffer
        for i in range(5):
            ret, current_frame = self.cap.read()
            if ret:
                frame = current_frame
            else:
                # If we can't even get one frame, fail early
                raise RuntimeError(f"Failed to grab frame from camera at iteration {i}")
        if frame is None:
            raise RuntimeError("Camera read returned success, but frame remained None.")
        success, buffer = cv2.imencode(image_format, frame)
        if not success:
            raise RuntimeError("Failed to encode frame to bytes")
            
        return buffer.tobytes()

    def release(self):
        """Release the camera stream."""
        if self.cap.isOpened():
            self.cap.release()