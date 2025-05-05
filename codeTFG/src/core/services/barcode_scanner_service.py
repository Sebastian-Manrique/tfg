import cv2
from pyzbar.pyzbar import decode
from src.core.utils.sound_player import SoundPlayer
from src.core.exceptions.exceptions import BusinessException
from src.core.logging.logger import Logger
from src.core.utils.add_to_bdd import addBarcode


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
                            addBarcode(data_str, btype)
                            self.sound_player.play_sound()

                if cv2.waitKey(1) == ord('q'):
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()
