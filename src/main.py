import threading
import signal
import sys
import time
import json
from pathlib import Path
from flask import Flask, jsonify, send_file, make_response
from dotenv import load_dotenv

from components.camera import Camera
from components.scale import Phidget
from components.llm import OpenAiConvo


# Shared data structure
latest_data = {
    "weight": None,
    "image_path": Path(__file__).parent.parent / ".images" / "test.jpg",
    "timestamp": None,
    "items": None
}
data_lock = threading.Lock()

# Flask app
app = Flask(__name__)

load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

@app.route('/')
def index():
    html_path = Path(__file__).parent / 'api' / 'client.html'
    return send_file(html_path)

@app.route('/data')
def get_data():
    with data_lock:
        metadata = {
            "weight": latest_data.get("weight"),
            "timestamp": latest_data.get("timestamp")
        }
        return jsonify(metadata)

@app.route('/order')
def get_order():
    return "Order #263"

@app.route('/image')
def get_image():
    with data_lock:
        img_path = latest_data.get("image_path")
        if img_path and Path(img_path).exists():
            return send_file(img_path, mimetype="image/jpeg")
        else:
            return make_response("No image available", 404)

@app.route('/items')
def get_items():
    with data_lock:
        items_str = latest_data.get("items")
        if items_str is not None:
            try:
                items = json.loads(items_str)
                return jsonify(items)
            except json.JSONDecodeError:
                return make_response("Invalid JSON response", 500)
        else:
            return make_response("No items available", 404)

@app.route('/weight')
def get_weight():
    with data_lock:
        weight = latest_data.get("weight")
        theoretical_weight = latest_data.get("theoretical_weight")
        tolerance = latest_data.get("tolerance")
        if weight is not None:
            return jsonify({"weight": weight, "theoretical_weight": theoretical_weight, "tolerance": tolerance})
        else:
            return make_response("No weight available", 404)


def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

def main():
    scale = Phidget.new(9775979.599626426, 0.0001310482621192932)
    camera = Camera()

    image_path = Path(__file__).parent.parent / ".images" / "test.jpg"
    open_ai_convo = OpenAiConvo(image_path=image_path)

    def cleanup_and_exit(sig=None, frame=None):
        print("\nShutting down gracefully...")
        camera.release()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup_and_exit)

    # Start Flask in background thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("Flask server running on http://localhost:5000")
    print("View dashboard at: http://localhost:5000/")
    print("API endpoints:")
    print("  /data  → weight and timestamp")
    print("  /image → actual image")
    print("  /items → detected items with ingredients")

    print("\nStarting seefood...")
    while True:
        input("Press enter when ready for next reading...")

        start_time = time.time()

        # Capture weight
        weight = None
        def capture_weight():
            nonlocal weight
            weight = round(scale.weigh_median(8, 250))
            print(f"Weight: {weight}g")

        # Capture OpenAI response (returns JSON string)
        items_json = None
        def capture_items():
            nonlocal items_json
            items_json = open_ai_convo.prompt()
            print("--- Detected Items: ---")
            try:
                items = json.loads(items_json)
                print(json.dumps(items, indent=2))
            except json.JSONDecodeError:
                print(items_json)
            print("----------------------")

        # Image path for this run
        image_path = Path(__file__).parent.parent / ".images" / "test.jpg"

        # Start threads
        scale_thread = threading.Thread(target=capture_weight)
        camera_thread = threading.Thread(target=camera.capture, args=(image_path,))
        llm_thread = threading.Thread(target=capture_items)

        scale_thread.start()
        camera_thread.start()
        camera_thread.join()  # Wait for image before LLM
        llm_thread.start()

        scale_thread.join()
        llm_thread.join()

        end_time = time.time()
        print(f"--- Run Time: {end_time - start_time:.2f}s ---")

        # Update shared data
        with data_lock:
            latest_data["weight"] = weight
            latest_data["theoretical_weight"] = 250
            latest_data["tolerance"] = 5

            latest_data["image_path"] = str(image_path)
            latest_data["timestamp"] = time.time()
            latest_data["items"] = items_json

if __name__ == "__main__":
    main()