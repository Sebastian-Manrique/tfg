import cv2
import numpy as np
from ultralytics import YOLO
from src.core.logging.logger import Logger

class YOLOService:
    def __init__(self, model_path, logger: Logger):
        self.model = YOLO(model_path)
        self.labels = self.model.names
        self.logger = logger
        self.bbox_colors = [
            (164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
            (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)
        ]

    def process_frame(self, frame):
        results = self.model(frame, verbose=False)
        detections = results[0].boxes

        for i in range(len(detections)):
            xyxy = detections[i].xyxy.cpu().numpy().squeeze().astype(int)
            xmin, ymin, xmax, ymax = xyxy

            classidx = int(detections[i].cls.item())
            classname = self.labels[classidx]
            conf = detections[i].conf.item()

            if conf > 0.5:
                color = self.bbox_colors[classidx % 10]
                cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), color, 2)

                label = f'{classname}: {int(conf * 100)}%'
                label_size, base_line = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
                label_ymin = max(ymin, label_size[1] + 10)

                cv2.rectangle(frame, (xmin, label_ymin - label_size[1] - 10),
                              (xmin + label_size[0], label_ymin + base_line - 10),
                              color, cv2.FILLED)
                cv2.putText(frame, label, (xmin, label_ymin - 7),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

                if self.logger:
                    self.logger.info(f"YOLO → {classname}: {int(conf*100)}%")

        return frame
