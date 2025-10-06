import threading
import signal
import sys

from components.camera import Camera
from components.scale import Phidget


def main():
    scale = Phidget.new(9775979.599626426, 0.0001310482621192932)
    camera = Camera()

    def cleanup_and_exit(sig=None, frame=None):
        print("\nShutting down gracefully...")
        camera.release()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)

    print("Starting seefood...")
    while True:
        input("Press enter when ready for next reading...")

        scale_thread = threading.Thread(
            target=camera.capture, args=(".images/test.jpg",)
        )
        camera_thread = threading.Thread(
            target=lambda: print("Weight: ", scale.weigh_median(8, 250))
        )

        scale_thread.start()
        camera_thread.start()

        scale_thread.join()
        camera_thread.join()


if __name__ == "__main__":
    main()
