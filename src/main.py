import os
import sys
import time
from dataclasses import dataclass

import gpiozero
import requests
import logging
from enum import Enum
from datetime import datetime, timezone
from dotenv import load_dotenv
from google.oauth2 import service_account
from google.auth.transport.requests import Request

from src.components.scale import Scale
from src.components.camera import Camera
from src.config import load_config

class Mode(Enum):
    DEV = "dev"
    PROD = "prod"

    @classmethod
    def from_string(cls, mode_str):
        if mode_str.lower() == "dev":
            return cls.DEV
        elif mode_str.lower() == "prod":
            return cls.PROD
        # Handles cases where the string isn't "dev" or "prod"
        raise ValueError(f"Invalid mode specified: '{mode_str}'")

@dataclass
class Data:
    image_bytes: bytes
    weight: float
    device_id: str


logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


current_mode = Mode.PROD
try:
    if len(sys.argv) > 1:
        user_input = sys.argv[1]
        current_mode = Mode.from_string(user_input)
except Exception as e:
    logging.error(f"Warning: {e}. Defaulting to {current_mode.name} mode.")

logger.info(f"Running in {current_mode}")
logger.info("Loading environment variables...")
load_dotenv()
GCP_KEY = os.getenv("GCP_KEY")
BACKEND_URL = os.getenv("BACKEND_URL")
CONFIG_PATH = os.getenv("CONFIG_PATH")
if current_mode is Mode.DEV: BACKEND_URL = os.getenv("DEV_BACKEND_URL")
logger.info("✓ Loaded environment variables!")

def main():
    logger.info("Loading config file...")
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
    logger.info("✓ Loaded config file!")

    logger.info("Starting main loop...")
    failures = 0
    while True:
        try:
            logger.info("Awaiting next order...")
            button.wait_for_active()
            button.wait_for_inactive()
            logger.info("Order received!")
            logger.info("Taking reading...")
            red.on()
            weight = scale.median_weight()
            image_bytes = camera.capture()
            red.off()
            green.on()
            logger.info("✓ Reading taken!")
            failures = 0
            logger.info("Uploading reading...")
            send_reading(image_bytes, weight, config.device.serial)
            logger.info("✓ Reading uploaded!")
        except KeyboardInterrupt:
            logging.info("KeyboardInterrupt received. Cleaning up...")
            break
        except Exception as e:
            failures += 1
            if failures > 2: break;
            logging.error("Error taking reading: e")
            logging.error("Retrying...")
            continue

        time.sleep(1)
        green.off()

    green.off()
    red.off()
    camera.release()
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

    params = { "key": GCP_KEY }

    headers = {}
    # token = get_auth_token()
    # if token:
    #     headers['Authorization'] = f'Bearer {token}'

    # Make the POST request
    response = requests.post(
        BACKEND_URL,
        data=data,
        files=files,
        headers=headers,
        params=params
    )

    # Check response
    if response.status_code == 201:
        logging.info("✓ Reading uploaded successfully!")
        return response.json()
    else:
        logging.error(f"✗ Error: {response.status_code}\n{response.text}")
        return dict(response.json())

# def get_auth_token():
#     """Get an identity token for authenticating with Cloud Functions."""
#     if not GCP_KEY_PATH:
#         return None
#
#     credentials = service_account.IDTokenCredentials.from_service_account_file(
#         GCP_KEY_PATH,
#         target_audience=BACKEND_URL
#     )
#
#     credentials.refresh(Request())
#     return credentials.token

if __name__ == "__main__":
    main()