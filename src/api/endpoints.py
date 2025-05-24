import os
from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
from pathlib import Path
import json

# For the OpenCV scanner
from src.core.services.barcode_scanner_service import BarcodeScannerService
from src.core.utils.sound_player import SoundPlayer
from src.core.logging.logger import Logger
from src.core.config.config import Config
from src.core.repository.file_repository import FileRepository
from src.core.utils.file_utils import FileUtils

# Thermal printer service
from src.core.services.thermal_printer_service import ThermalPrinterService
from escpos.printer import Serial


# For the Yolo scanner
from src.core.services.yolo_service import YOLOService

# For the scanner
from src.core.repository.code_repository import CodeRepository


yolo_model_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "yolo", "my_model.pt")
)

config = Config()
logger = Logger(config)
logger_instance = logger.get_logger()

sound_path = os.path.join(os.path.dirname(
    __file__), "..", "..", "sound", "beep.wav")

db_path = os.path.join(
    os.path.dirname(__file__), "..", "core", "database", "allCodes.db"
)
db_path = os.path.abspath(db_path)

sound_path = os.path.abspath(sound_path)

code_repository = CodeRepository(db_path, logger)


sound_player = SoundPlayer(sound_file=sound_path, logger=logger_instance)

printer = Serial(devfile='/dev/ttyUSB0', baudrate=9600, timeout=1)


thermal_printer_service = ThermalPrinterService(
    printer=printer,
    logger=logger_instance,
    code_repository=code_repository
)


file_utils = FileUtils()
file_repository = FileRepository(logger=logger_instance, file_utils=file_utils)

barcode_service = BarcodeScannerService(
    sound_player, logger, image_output="output.jpg", code_repository=code_repository, file_repository=file_repository,  thermal_printer_service=thermal_printer_service
)
yolo_service = YOLOService(model_path=yolo_model_path, logger=logger_instance)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")


app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

camera = None
camera_thread = None

# Cargar traducciones
p = Path(".")
with open(p / "src/core/config/translations.json", "r", encoding="utf-8") as f:
    translations = json.load(f)


def camera_frames(mode="opencv"):
    global camera
    camera = cv2.VideoCapture(0)

    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            break

        if mode == "yolo":
            frame = yolo_service.start_scanning(frame)
        elif mode == "opencv":
            frame = barcode_service.start_scanning(frame)

            if not barcode_service.hardware.scanning:
                summary = barcode_service.summarize_discounts()
                logger_instance.debug(f"Summary creado: {summary}")

                break
        elif mode == "raw":
            pass  # No se modifica la imagen

        ret, jpeg = cv2.imencode(".jpg", frame)
        frame = jpeg.tobytes()

        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/")
def index():
    return render_template(
        "camera.html", hora="12:00", cameraBool=True, lang=translations["es"]
    )


@app.route("/en")
def index_en():
    return render_template(
        "camera.html", hora="12:00", cameraBool=True, lang=translations["en"]
    )


@app.route("/summary/<summary_id>", methods=["GET", "POST"])
def resumen(summary_id):

    if request.method == "GET":
        summary_data = barcode_service.last_summary
        print(f"Requested summary ID")

        if not summary_data or summary_data["id"] != summary_id:
            return "Resumen no encontrado", 404

        return render_template("summary.html", summary=summary_data["summary"], id=summary_id)

    elif request.method == "POST":
        summary_data = barcode_service.last_summary

        if not summary_data or summary_data["id"] != summary_id:
            return "Resumen no encontrado", 404

        # Mark the codes as used
        for code in summary_data["codes"]:
            barcode_service.code_repository.mark_as_used(code)

        return render_template("summary.html", summary=summary_data["summary"], id=summary_id, usado=True)


@app.route("/video/<mode>")
def video_feed(mode):
    if mode not in ["yolo", "opencv"]:
        return "Modo no soportado", 400
    return Response(
        camera_frames(mode=mode), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/restart-camera", methods=["POST"])
def restart_camera():
    return jsonify({"status": "Camera restarted"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
