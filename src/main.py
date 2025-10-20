import os
import sys
import time
import gpiozero
import requests
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from src.components.scale import Scale
from src.components.camera import Camera
from src.config import load_config

load_dotenv()
GCP_KEY_PATH = os.getenv("GCP_KEY")
BACKEND_URL = os.getenv("BACKEND_URL")
CONFIG_PATH = os.getenv("CONFIG_PATH")

def main():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        config = load_config(CONFIG_PATH)
        scale = Scale.new(config.scale)
        camera = Camera(config.camera)
        button = gpiozero.Button(config.button.pin)
        red = gpiozero.LED(config.red_led.pin)
        green = gpiozero.LED(config.green_led.pin)
    except Exception as e:
        logger.error("Error running setup: {}".format(e))
        sys.exit(1)

    failures = 0
    while True:
        try:
            button.wait_for_active()
            button.wait_for_inactive()
            red.on()
            weight = scale.live_weigh()
            image_bytes = camera.capture()
            red.off()
            green.on()
            failures = 0
        except KeyboardInterrupt:
            print("\nKeyboardInterrupt received. Cleaning up...")
            camera.release()
            red.off()
            green.off()
            sys.exit(0)
        except Exception as e:

            failures += 1
            if failures > 2: break;
            print("Error taking reading: \n", e, "\nRetrying...")
            continue


        send_reading(image_bytes, weight, config.device.serial)
        time.sleep(1)
        green.off()

    logging.error("Unrecoverable error. Restarting system...")
    sys.exit(1)


def send_reading(image_bytes: bytes, weight: float, device_id: str, filename: str ="image.jpg") -> dict:
    """
    Send a reading to the backend.

    Args:
        image_bytes: Image data as bytes
        weight: Weight measurement in grams (float)
        device_id: Unique identifier for the device
        filename: Optional filename for the image (default: "image.jpg")

    Returns:
        dict: Response from the server
    """
    # Prepare the timestamp in ISO 8601 format with UTC timezone
    timestamp = datetime.now(timezone.utc).isoformat()
    data = {
        'weight': str(weight),
        'device_id': device_id,
        'timestamp': timestamp
    }

    # Prepare the file from bytes
    files = {
        'image': (
            filename,  # filename
            image_bytes,  # bytes data
            'image/jpeg'  # MIME type
        )
    }

    headers = {}
    token = get_auth_token()
    if token:
        headers['Authorization'] = f'Bearer {token}'

    # Make the POST request
    response = requests.post(
        BACKEND_URL,
        data=data,
        files=files,
        headers=headers
    )

    # Check response
    if response.status_code == 201:
        print("✓ Reading uploaded successfully!")
        return response.json()
    else:
        print(f"✗ Error: {response.status_code}")
        print(response.json())
        return dict(response.json())

def get_auth_token():
    """Get an identity token for authenticating with Cloud Functions."""
    if not GCP_KEY_PATH:
        return None

    credentials = service_account.IDTokenCredentials.from_service_account_file(
        GCP_KEY_PATH,
        target_audience=BACKEND_URL
    )

    credentials.refresh(Request())
    return credentials.token

if __name__ == "__main__":
    main()