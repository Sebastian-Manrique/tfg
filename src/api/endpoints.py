from pathlib import Path
from flask import Flask, render_template, Response, jsonify, after_this_request
import cv2
import json
import threading


app = Flask(__name__)

# This is for the restart thread button
camera = None
camera_thread = None


p = Path('.')

with open(p / 'src/core/config/translations.json', 'r',  encoding='utf-8') as f:
    translations = json.load(f)


def camera_frames():
    global camera
    camera = cv2.VideoCapture(0)  # Open the default camera (0)

    while camera.isOpened():
        isEnable, frame = camera.read()
        if not isEnable:
            print("Failed to capture image")
            break
        else:
            # Encode the frame as JPG
            response, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    hour_fun_flask = "12:79"
    camera_fun_flask = True
    return render_template("camera.html", hora=hour_fun_flask, cameraBool=camera_fun_flask, lang=translations['es'])


@app.route('/en')
def index_en():
    hour_fun_flask = "12:79"
    camera_fun_flask = True
    return render_template("camera.html", hora=hour_fun_flask, cameraBool=camera_fun_flask, lang=translations['en'])


@app.route('/manual-scan', methods=['POST'])
def manual_scan():
    return jsonify({"status": "El escaneo ya está en curso."})


@app.route('/video')
def camera_stream():
    return Response(camera_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/restart-camera', methods=['POST'])
def restart():
    global camera, camera_thread

    # Stops the actual loop
    if camera:
        camera.release()

    # Wait for the previous thread to end (optional)
    if camera_thread and camera_thread.is_alive():
        camera_thread.join(timeout=2)

    # Reboot on a new thread (does not lock Flask)
    camera_thread = threading.Thread(target=camera_frames, daemon=True)
    camera_thread.start()

    return jsonify({"status": "Camera restarted"})


app.run(host="0.0.0.0", port=5001, debug=True)
