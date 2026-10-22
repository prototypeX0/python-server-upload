
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from pathlib import Path

app = Flask(__name__)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Maximum upload size: 100 MB
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024


@app.route("/", methods=["GET"])
def home():
    return {
        "server": "Kali File Upload Server",
        "endpoint": "/upload",
        "method": "POST"
    }


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    if not file.filename:
        return jsonify({"error": "No filename provided"}), 400

    filename = secure_filename(file.filename)

    if not filename:
        return jsonify({"error": "Invalid filename"}), 400

    # Avoid overwriting an existing file
    destination = UPLOAD_DIR / filename
    counter = 1

    while destination.exists():
        destination = UPLOAD_DIR / f"{counter}_{filename}"
        counter += 1

    file.save(destination)

    return jsonify({
        "status": "success",
        "filename": destination.name,
        "saved_to": str(destination.resolve()),
        "size_bytes": destination.stat().st_size
    }), 201


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({"error": "File exceeds 100 MB limit"}), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
