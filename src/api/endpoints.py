import os
from flask import Flask, render_template, Response, jsonify
from src.core.utils.yolo_service import detect_objects
from src.core.services.barcode_scanner_service import BarcodeScannerService
from src.core.utils.sound_player import SoundPlayer
from src.core.logging.logger import Logger
from src.core.config.config import Config

config = Config()
logger = Logger(config)
sound_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sound', 'beep.wav')
sound_path = os.path.abspath(sound_path)

sound_player = SoundPlayer(sound_file=sound_path, logger=logger)

barcode_service = BarcodeScannerService(sound_player, logger, image_output="output.jpg")

import cv2
import threading
from pathlib import Path
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")


app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

camera = None
camera_thread = None

# Cargar traducciones
p = Path('.')
with open(p / 'src/core/config/translations.json', 'r', encoding='utf-8') as f:
    translations = json.load(f)


def camera_frames(mode='opencv'):
    global camera
    camera = cv2.VideoCapture(0)

    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            break

        if mode == 'yolo':
            frame = detect_objects(frame)
        elif mode == 'opencv':
            frame = barcode_service.process_frame(frame)
        elif mode == 'raw':
            pass  # No se modifica la imagen

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



@app.route('/')
def index():
    return render_template("camera.html", hora="12:00", cameraBool=True, lang=translations['es'])


@app.route('/video/<mode>')
def video_feed(mode):
    if mode not in ['yolo', 'opencv']:
        return "Modo no soportado", 400
    return Response(camera_frames(mode=mode), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/restart-camera', methods=['POST'])
def restart_camera():
    return jsonify({"status": "Camera restarted"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
