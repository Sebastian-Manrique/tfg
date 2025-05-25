import os
from flask import Flask, render_template, Response, jsonify, request
import cv2
import threading
import hashlib
import time
from datetime import datetime
from pathlib import Path
import json
from datetime import datetime, timedelta

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
from src.core.utils import shared_flags

# For the scanner
from src.core.repository.code_repository import CodeRepository


yolo_model_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "yolo", "my_model.pt")
)

config = Config()
logger = Logger(config)
logger_instance = logger.get_logger()

sound_path = os.path.join(os.path.dirname(__file__), "..", "..", "sound", "beep.wav")

db_path = os.path.join(
    os.path.dirname(__file__), "..", "core", "database", "allCodes.db"
)
db_path = os.path.abspath(db_path)

sound_path = os.path.abspath(sound_path)

code_repository = CodeRepository(db_path, logger)


sound_player = SoundPlayer(sound_file=sound_path, logger=logger_instance)

printer = Serial(devfile="/dev/ttyUSB0", baudrate=9600, timeout=1)


thermal_printer_service = ThermalPrinterService(
    printer=printer, logger=logger_instance, code_repository=code_repository
)


file_utils = FileUtils()
file_repository = FileRepository(logger=logger_instance, file_utils=file_utils)

barcode_service = BarcodeScannerService(
    sound_player,
    logger,
    image_output="output.jpg",
    code_repository=code_repository,
    file_repository=file_repository,
    thermal_printer_service=thermal_printer_service,
)
yolo_service = YOLOService(
    model_path=yolo_model_path,
    logger=logger_instance,
    sound_player=sound_player,
    hardware_controller=barcode_service.hardware,
)


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(os.path.dirname(__file__), "templates")
static_dir = os.path.join(os.path.dirname(__file__), "static")


app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

camera = None
camera_thread = None

# Load translations
try:
    content = file_repository.get_content_file("src/core/config/translations.json")
    translations = json.loads(content)
except Exception as e:
    logger_instance.error(f"No se pudo cargar el archivo de traducciones: {e}")
    translations = {"es": {}, "en": {}}  # Fallback vacío para evitar errores


def camera_frames(mode="opencv"):
    global camera
    camera = cv2.VideoCapture(0)

    barcode_service.hardware.camera_on()

    # Setup for each mode
    if mode == "yolo":
        barcode_service.hardware.camera_on()

        _init_yolo_session()
    elif mode == "opencv":
        barcode_service.hardware.scanning = True

    while camera.isOpened():
        ret, frame = camera.read()
        if not ret:
            break

        if mode == "yolo":
            frame = yolo_service.process_frame(frame)

            if (
                yolo_service.has_valid_detection
                and shared_flags.button_pressed_after_detection
            ):
                _finalize_yolo_detection()
                barcode_service.hardware.camera_off()
                break

        elif mode == "opencv":
            frame = barcode_service.start_scanning(frame)

            if not barcode_service.hardware.scanning:
                _finalize_barcode_detection()
                break

        elif mode == "raw":
            pass  # no cambios a la imagen

        # Codificar y enviar el frame
        ret, jpeg = cv2.imencode(".jpg", frame)
        frame = jpeg.tobytes()
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


# For the Yolo and the OpenCV logic
def _init_yolo_session():
    yolo_service.detected_counts = {"Plastics": 0, "Aluminium cans": 0}
    yolo_service.last_detection_time = {"Plastics": 0, "Aluminium cans": 0}
    yolo_service.has_valid_detection = False
    shared_flags.button_pressed_after_detection = False


def _finalize_yolo_detection():
    summary = yolo_service.summarize_detections()
    summary_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:8]

    thermal_printer_service.print_summary_coupon(summary_id, summary)
    logger_instance.info(f"🧾 Cupón generado con YOLO: {summary_id}")
    hora_actual = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")

    barcode_service.last_summary = {
        "id": summary_id,
        "codes": "Yolo detection",
        "summary": summary,
        "used": False,
        "hora": hora_actual,
    }

    shared_flags.button_pressed_after_detection = False


def _finalize_barcode_detection():
    summary = barcode_service.summarize_discounts()
    logger_instance.debug(f"Summary creado: {summary}")


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
    summary_data = barcode_service.last_summary

    if request.method == "GET":
        if not summary_data or summary_data["id"] != summary_id:
            return "Resumen no encontrado", 404

        lang_code = request.args.get("lang", "es")
        lang = translations.get(lang_code, translations["es"])
        hora = summary_data.get(
            "hora", summary_data["summary"].get("hora", "Desconocida")
        )

        return render_template(
            "summary.html",
            summary=summary_data["summary"],
            id=summary_id,
            usado=summary_data.get("used", False),
            lang=lang,
            hora=hora,
        )

    elif request.method == "POST":
        if not summary_data["codes"]:
            logger_instance.warning("Intento de canje sin códigos escaneados.")
            return jsonify({"error": "No hay códigos para canjear"}), 400

        for code in summary_data["codes"]:
            barcode_service.code_repository.mark_as_used(code)

            barcode_service.last_summary["used"] = True

        return jsonify({"success": True})


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