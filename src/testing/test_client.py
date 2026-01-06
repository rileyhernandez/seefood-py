import requests
import time
import sys
from ..components.scale import Scale
from ..config import Scale as ScaleConfig, Config, load_config
from ..components.camera import Camera
import gpiozero
from dotenv import load_dotenv
import os

class TestClient:
    def __init__(self, server_url):
        """
        Initialize the client with the backend URL.
        Example: TestClient("http://localhost:8080/upload")
        """
        self.server_url = server_url

    def send(self, fields: dict, image_path: str | None = None, image_bytes: bytes | None = None, filename: str | None = None):
        files = {}
        
        # Logic for raw bytes (no closing needed)
        if image_bytes:
            files["image"] = (filename, image_bytes, "application/octet-stream")
            return self._post_request(fields, files)
    
        # Logic for file paths (using context manager)
        if image_path:
            with open(image_path, "rb") as f:
                files["image"] = (os.path.basename(image_path), f, "application/octet-stream")
                return self._post_request(fields, files)
    
        # Fallback for no image
        return self._post_request(fields, None)
    
    def _post_request(self, fields, files):
        print(f"→ Sending POST to {self.server_url}")
        response = requests.post(self.server_url, data=fields, files=files)
        print(f"← Status: {response.status_code}")
        return response

if __name__ == "__main__":
	load_dotenv()
	GCP_KEY = os.getenv("GCP_KEY")
	BACKEND_URL = os.getenv("DEV_BACKEND_URL")
	CONFIG_PATH = os.getenv("CONFIG_PATH")
	config = load_config(CONFIG_PATH)
	client = TestClient(BACKEND_URL)
	scale = Scale.new(config.scale)

	camera = Camera(config.camera)
	button = gpiozero.Button(config.button.pin)
	red = gpiozero.LED(config.red_led.pin)
	green = gpiozero.LED(config.green_led.pin)
	
	match sys.argv[1:]:
		case []:
			try:
				while True:
					button.wait_for_active()
					button.wait_for_inactive()
					red.on()
					weight = scale.median_weight()
					image_bytes = camera.capture()
					red.off()
					green.on()
					print("Weight: ", weight)
					client.send(
                        fields={"weight": weight},
                        image_bytes=image_bytes,
                        filename="capture.jpg"
					)
					time.sleep(1)
					green.off()
			except KeyboardInterrupt:
				print("\nKeyboardInterrupt received. Cleaning up...")
			except Exception as e:
				print("Critical error: \n", e)
			finally:
				# Always run cleanup
				camera.release()
				red.off()
				green.off()
				print("Resources released, exiting.")
				sys.exit(0)
		case ['led']:
			print("Running LED test...")
			while True:
				red.on()
				time.sleep(1)
				red.off()
				green.on()
				time.sleep(1)
				green.off()
		case ['button']:
			print("Running Button test...")
			while True:
				button.wait_for_active()
				print("Button pressed!")
				button.wait_for_inactive()
				print("Button released!")

		case ['led-button']:
			print("Running LED and Button test...")
			while True:
				button.wait_for_active()
				red.off()
				green.on()
				print("Button pressed!")
				button.wait_for_inactive()
				green.off()
				red.on()
				print("Button released!")