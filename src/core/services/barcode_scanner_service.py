from datetime import datetime
import cv2
import hashlib
import numpy as np
from datetime import datetime, timedelta
import time
import json
from pathlib import Path
from pyzbar.pyzbar import decode
from src.core.utils.hardware_controller import HardwareController
from src.core.utils.sound_player import SoundPlayer
from src.core.exceptions.exceptions import BusinessException
from src.core.logging.logger import Logger
from src.core.repository.code_repository import CodeRepository
from src.core.repository.file_repository import FileRepository

# For the discont price
from src.core.config.config import Config


class BarcodeScannerService:
    def __init__(
        self,
        sound_player: SoundPlayer,
        logger: Logger,
        image_output: str,
        code_repository: CodeRepository,
        file_repository: FileRepository,
        thermal_printer_service=None,
    ):
        self.sound_player = sound_player
        self.logger = logger.get_logger()
        self.image_output = image_output
        self.code_repository = code_repository
        self.file_repository = file_repository
        self.last_summary = None
        self.thermal_printer_service = thermal_printer_service
        self.hardware = HardwareController(on_button_press=self._on_button_pressed)
        self.last_scanned = {"code": None, "time": 0}
        self.codes_scanned = []
        self.material_codes = self._load_material_codes()

    def _on_button_pressed(self):
        if not self.codes_scanned:
            self.logger.info("Button pressed, but no codes. Ignoring.")
            return  # Do nothing

        self.logger.info("Button pressed: generating summary.")
        self.hardware.scanning = False

    def _load_material_codes(self):
        try:
            path = "src/core/config/material_codes.json"
            content = self.file_repository.get_content_file(path)
            return json.loads(content)
        except Exception as e:
            self.logger.error(f"Error cargando material_codes.json: {e}")
            return {"plastic_bottles": [], "aluminum_cans": []}

    def start_scanning(self, frame):
        frame = cv2.flip(frame, 1)

        detected_barcodes = decode(frame)
        if detected_barcodes:
            for barcode in detected_barcodes:
                if barcode.data:
                    data_str = barcode.data.decode("utf-8")
                    btype = barcode.type
                    now = time.time()

                    if (
                        self.last_scanned["code"] == data_str
                        and (now - self.last_scanned["time"]) < 3
                    ):
                        self.logger.info(f"Duplicate barcode ignored: {data_str}")
                        continue

                    self.last_scanned = {"code": data_str, "time": now}
                    self.logger.info(f"Barcode detected: {data_str}")

                    self.sound_player.play_sound()
                    self.hardware.blink_camera()
                    self.hardware.scan_success()
                    self.code_repository.save_code(data_str, btype)
                    self.codes_scanned.append(data_str)

                    # Dibuja rectángulo
                    pts = barcode.polygon
                    pts = [(pt.x, pt.y) for pt in pts]
                    pts = np.array(pts, np.int32).reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

                    # Texto
                    cv2.putText(
                        frame,
                        f"{btype}: {data_str}",
                        (pts[0][0][0], pts[0][0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

        return frame

    def summarize_discounts(self):
        plastic_codes = self.material_codes["plastic_bottles"]
        aluminum_codes = self.material_codes["aluminum_cans"]

        plastic_count = 0
        aluminum_count = 0

        for code in self.codes_scanned:
            if code in plastic_codes:
                plastic_count += 1
            elif code in aluminum_codes:
                aluminum_count += 1

        discount_per_plastic = Config.DISCOUNT_PLASTIC
        discount_per_aluminum = Config.DISCOUNT_ALUMINUM

        total_discount_centimos = (
            plastic_count * discount_per_plastic
            + aluminum_count * discount_per_aluminum
        )

        # Generate summary_id unique
        joined_codes = "".join(self.codes_scanned)
        now_str = datetime.now().isoformat()

        hash_input = f"{joined_codes}{now_str}"
        summary_id = hashlib.sha256(hash_input.encode()).hexdigest()[:8]

        summary = {
            "plastics_bottles": plastic_count,
            "aluminum_cans": aluminum_count,
            "descuento_total_centimos": total_discount_centimos,
            "descuento_total_euros": round(total_discount_centimos / 100, 2),
        }

        print("\n🧾 Resumen del escaneo:")
        print(json.dumps(summary, indent=2, ensure_ascii=False))

        if self.thermal_printer_service:
            self.thermal_printer_service.print_summary_coupon(summary_id, summary)

        hora_actual = (datetime.now() + timedelta(hours=1)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # Save the summary if requested via web
        self.last_summary = {
            "id": summary_id,
            "codes": list(self.codes_scanned),
            "summary": summary,
            "hora": hora_actual,
            "used": False,
        }
        
        self.hardware.camera_off()

        return summary
