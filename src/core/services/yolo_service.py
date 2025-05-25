import cv2
import time
import numpy as np
from ultralytics import YOLO
from src.core.logging.logger import Logger
from src.core.config.config import Config


class YOLOService:
    def __init__(
        self, model_path, logger: Logger, sound_player=None, hardware_controller=None
    ):
        self.model = YOLO(model_path)
        self.labels = self.model.names
        self.logger = logger
        self.has_valid_detection = False
        self.sound_player = sound_player
        self.hardware_controller = hardware_controller
        self.detected_counts = {"Plastics": 0, "Aluminium cans": 0}
        self.last_detection_time = {"Plastics": 0, "Aluminium cans": 0}
        self.cooldown_seconds = 2

        self.bbox_colors = [
            (164, 120, 87),
            (68, 148, 228),
            (93, 97, 209),
            (178, 182, 133),
            (88, 159, 106),
            (96, 202, 231),
            (159, 124, 168),
            (169, 162, 241),
            (98, 118, 150),
            (172, 176, 184),
        ]

    def process_frame(self, frame):
        self.detected_classes = []
        results = self.model(frame, verbose=False)
        detections = results[0].boxes

        for i in range(len(detections)):
            xyxy = detections[i].xyxy.cpu().numpy().squeeze().astype(int)
            xmin, ymin, xmax, ymax = xyxy

            classidx = int(detections[i].cls.item())
            classname = self.labels[classidx]
            conf = detections[i].conf.item()

            if conf > 0.5:
                classname = self.labels[classidx]
                now = time.time()

                if classname in self.detected_counts:
                    # To do not duplicate discounts with the object classes
                    last_time = self.last_detection_time[classname]
                    if now - last_time >= self.cooldown_seconds:
                        self.detected_counts[classname] += 1
                        if self.sound_player:
                            self.sound_player.play_sound()
                        if self.hardware_controller:
                            self.hardware_controller.scan_success()
                        self.last_detection_time[classname] = now

                self.detected_classes.append(classname)
                color = self.bbox_colors[classidx % 10]
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                label = f"{classname}: {int(conf * 100)}%"
                label_size, base_line = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                label_ymin = max(ymin, label_size[1] + 10)

                cv2.rectangle(
                    frame,
                    (xmin, label_ymin - label_size[1] - 10),
                    (xmin + label_size[0], label_ymin + base_line - 10),
                    color,
                    cv2.FILLED,
                )
                cv2.putText(
                    frame,
                    label,
                    (xmin, label_ymin - 7),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 0, 0),
                    1,
                )

                if self.logger:
                    self.logger.info(f"YOLO → {classname}: {int(conf * 100)}%")

        self.has_valid_detection = (
            self.detected_counts["Plastics"] > 0
            or self.detected_counts["Aluminium cans"] > 0
        )

        return frame

    def summarize_detections(self):
        plastic_count = self.detected_counts["Plastics"]
        aluminum_count = self.detected_counts["Aluminium cans"]

        discount_per_plastic = Config.DISCOUNT_PLASTIC
        discount_per_aluminum = Config.DISCOUNT_ALUMINUM

        total_discount_centimos = (
            plastic_count * discount_per_plastic
            + aluminum_count * discount_per_aluminum
        )

        return {
            "plastics_bottles": plastic_count,
            "aluminum_cans": aluminum_count,
            "descuento_total_centimos": total_discount_centimos,
            "descuento_total_euros": round(total_discount_centimos / 100, 2),
        }
