from flask import Flask, request, render_template_string, send_from_directory
import base64, os, time
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
        th, td { border: 1px solid #ccc; padding: 0.5rem; }
        img { max-height: 100px; border-radius: 6px; }
    </style>
    <meta http-equiv="refresh" content="2">
</head>
<body>
<h1>📥 Incoming Uploads</h1>
<table>
<tr><th>Time</th><th>Weight</th><th>Image</th></tr>
{% for u in uploads %}
<tr>
    <td>{{ u.time }}</td>
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
    form_data = dict(request.form)
    file = request.files.get("image")

    image_b64 = None
    if file:
        image_b64 = base64.b64encode(file.read()).decode("utf-8")

    uploads.append({
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "weight": form_data.get("weight"),
        "image": image_b64
    })

    print(f"✅ Received upload at {time.strftime('%Y-%m-%d %H:%M:%S')}: {form_data}")
    return "OK", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
