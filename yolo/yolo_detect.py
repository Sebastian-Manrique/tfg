import cv2
import numpy as np
from ultralytics import YOLO


def detect_objects(image, model_path, conf_threshold=0.5):
    """
    Detecta objetos en una imagen utilizando un modelo YOLO y devuelve resultados y la imagen anotada.

    :param image: Imagen (np.array) en formato BGR (OpenCV)
    :param model_path: Ruta al modelo YOLO (.pt, torchscript, etc.)
    :param conf_threshold: Umbral mínimo de confianza (default: 0.5)
    :return: Tuple con:
        - detecciones: lista de tuplas (etiqueta, confianza)
        - annotated_image: imagen con los resultados dibujados (np.array)
    """
    model = YOLO(model_path)
    results = model(image, verbose=False)
    detections = results[0].boxes
    labels = model.names

    annotated_image = image.copy()
    result_list = []

    bbox_colors = [
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

    for i, det in enumerate(detections):
        conf = det.conf.item()
        if conf >= conf_threshold:
            class_idx = int(det.cls.item())
            class_name = labels[class_idx]
            result_list.append((class_name, conf))

            # Dibujar en la imagen
            color = bbox_colors[class_idx % len(bbox_colors)]
            x1, y1, x2, y2 = map(int, det.xyxy[0].tolist())

            cv2.rectangle(annotated_image, (x1, y1), (x2, y2), color, 2)
            label = f"{class_name} ({int(conf * 100)}%)"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(annotated_image, (x1, y1 - 20), (x1 + w, y1), color, -1)
            cv2.putText(
                annotated_image,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                1,
            )

    return result_list, annotated_image
