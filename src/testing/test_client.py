import requests
import time
import sys
from ..components.scale import Scale
from ..config import Scale as ScaleConfig
from ..components.camera import Camera

class TestClient:
    def __init__(self, server_url):
        """
        Initialize the client with the backend URL.
        Example: TestClient("http://localhost:8080/upload")
        """
        self.server_url = server_url

    def send(self, fields: dict, image_path: str = None, image_bytes: bytes = None, filename: str = None):
        """
        Send data and optional image to the server.

        Args:
            fields: dict of form fields, e.g. {"name": "Riley", "comment": "Test upload"}
            image_path: optional, path to image file to upload
            image_bytes: optional, raw bytes of image
            filename: filename to use when uploading bytes
        """
        files = {}
        if image_path:
            files["file"] = (image_path.split("/")[-1], open(image_path, "rb"), "application/octet-stream")
        elif image_bytes:
            files["file"] = (filename, image_bytes, "application/octet-stream")

        print(f"→ Sending POST to {self.server_url}")
        response = requests.post(self.server_url, data=fields, files=files if files else None)

        # If file opened, close it
        if image_path:
            files["file"][1].close()

        print(f"← Status: {response.status_code}")
        return response

if __name__ == "__main__":
    if len(sys.argv) > 1:
        ip = sys.argv[1]
    else:
        ip = "192.168.37.255"
        print("Using default host ip: ", ip)

    host = f"http://{ip}:8080/upload"
    client = TestClient(host)

    config = ScaleConfig(0.0013512, 100)
    scale = Scale.new(config)

    camera = Camera()

    while True:
        try:
            weight = scale.live_weigh()
            image_bytes = camera.capture()
            print("Weight: ", weight)
            client.send(
                fields={"weight": weight},
                image_bytes=image_bytes,
                filename="capture.jpg"
            )
            time.sleep(0.25)
        except Exception as e:
            camera.release()
            print("Critical error: \n", e)
            sys.exit(1)