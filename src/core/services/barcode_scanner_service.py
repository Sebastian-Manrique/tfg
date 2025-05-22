import cv2
import numpy as np
from pyzbar.pyzbar import decode
from src.core.utils.sound_player import SoundPlayer
from src.core.exceptions.exceptions import BusinessException
from src.core.logging.logger import Logger


class BarcodeScannerService:
    def __init__(self, sound_player: SoundPlayer, logger: Logger, image_output: str):
        self.sound_player = sound_player
        self.logger = logger.get_logger()
        self.image_output = image_output

    def start_scanning(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            self.logger.error("Webcam not accessible.")
            raise BusinessException(500, "Cannot access webcam.")

        try:
            while cap.isOpened():
                success, frame = cap.read()
                frame = cv2.flip(frame, 1)

                detected_barcodes = decode(frame)
                if not detected_barcodes:
                    self.logger.info("No barcode detected.")
                else:
                    for barcode in detected_barcodes:
                        if barcode.data:
                            data_str = barcode.data.decode('utf-8')
                            btype = barcode.type
                            self.logger.info(f"Barcode detected: {data_str}")
                            self.sound_player.play_sound()

                if cv2.waitKey(1) == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
    
    def process_frame(self, frame):
        frame = cv2.flip(frame, 1)

        detected_barcodes = decode(frame)
        if not detected_barcodes:
            self.logger.info("No barcode detected.")
        else:
            for barcode in detected_barcodes:
                if barcode.data:
                    data_str = barcode.data.decode('utf-8')
                    btype = barcode.type
                    self.logger.info(f"Barcode detected: {data_str}")
                    self.sound_player.play_sound()

                    # Dibuja el rectángulo alrededor del código
                    pts = barcode.polygon
                    pts = [(pt.x, pt.y) for pt in pts]
                    pts = np.array(pts, np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 2)

                    # Escribe el tipo y contenido del código
                    cv2.putText(frame, f"{btype}: {data_str}", (pts[0][0][0], pts[0][0][1] - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return frame

