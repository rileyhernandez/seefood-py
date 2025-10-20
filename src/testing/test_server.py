from flask import Flask, request, render_template_string, jsonify
import base64
from datetime import datetime

app = Flask(__name__)

uploads = []

PAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Incoming Uploads</title>
    <style>
        body { font-family: sans-serif; padding: 1rem; background: #fafafa; }
        h1 { margin-bottom: 1rem; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ccc; padding: 0.5rem; text-align: left; }
        img { max-height: 100px; border-radius: 6px; }
        .device-id { font-family: monospace; font-size: 0.9em; color: #666; }
    </style>
    <meta http-equiv="refresh" content="2">
</head>
<body>
<h1>📥 Incoming Uploads</h1>
<table>
<tr><th>Time</th><th>Device ID</th><th>Weight (g)</th><th>Image</th></tr>
{% for u in uploads %}
<tr>
    <td>{{ u.time }}</td>
    <td class="device-id">{{ u.device_id }}</td>
    <td>{{ u.weight }}</td>
    <td>
    {% if u.image %}
        <img src="data:image/jpeg;base64,{{ u.image }}" />
    {% else %}
        <i>No image</i>
    {% endif %}
    </td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(PAGE_TEMPLATE, uploads=reversed(uploads))


@app.route("/upload", methods=["POST"])
def upload():
    # Extract form data
    weight = request.form.get("weight")
    device_id = request.form.get("device_id")
    timestamp = request.form.get("timestamp")

    # Extract image file
    file = request.files.get("image")

    image_b64 = None
    if file:
        image_b64 = base64.b64encode(file.read()).decode("utf-8")

    # Parse timestamp or use current time
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    else:
        time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store the upload
    uploads.append({
        "time": time_str,
        "device_id": device_id or "unknown",
        "weight": weight or "N/A",
        "image": image_b64
    })

    # Check for Authorization header (optional validation)
    auth_header = request.headers.get("Authorization")
    if auth_header:
        print(f"🔑 Auth header received: {auth_header[:20]}...")

    print(f"✅ Received upload from device {device_id}: weight={weight}g at {time_str}")

    # Return 201 status with JSON response (matching what client expects)
    return jsonify({
        "status": "success",
        "message": "Reading uploaded successfully",
        "data": {
            "weight": weight,
            "device_id": device_id,
            "timestamp": time_str
        }
    }), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)