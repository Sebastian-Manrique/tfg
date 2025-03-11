import cv2
from pyzbar import pyzbar
import os

# Iniciar la captura de video desde la webcam (cambia 0 si tienes varias cámaras)
cap = cv2.VideoCapture(0)

# Verificar si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara")
    exit()

# Capturar un solo fotograma
ret, frame = cap.read()

if ret:

    # Buscar el siguiente número disponible, para guardar la imagen
    contador = 1
    while os.path.exists(os.path.join("img", f"foto{contador}.jpg")):
        contador += 1

    # Nombre final de la nueva imagen
    nuevo_nombre = os.path.join("img", f"foto{contador}.jpg")

    # Guardar la imagen
    cv2.imwrite("img/foto.jpg", frame)
    os.rename("img/foto.jpg", nuevo_nombre)
    print(f"Foto guardada como {nuevo_nombre}")

    # Leer el código QR
    img = cv2.imread(nuevo_nombre)

    barcodes = pyzbar.decode(img)

    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 4)
        bdata = barcode.data.decode("utf-8")
        btype = barcode.type
        text = f"{bdata}, {btype}"
        cv2.putText(img, text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    cv2.imshow("foto", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

else:
    print("Error: No se pudo capturar la imagen")

# Liberar la cámara
cap.release()
cv2.destroyAllWindows()
