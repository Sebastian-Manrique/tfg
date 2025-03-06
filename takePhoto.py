import cv2

# Iniciar la captura de video desde la webcam (cambia 0 si tienes varias cámaras)
cap = cv2.VideoCapture(0)

# Verificar si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error: No se pudo acceder a la cámara")
    exit()

# Capturar un solo fotograma
ret, frame = cap.read()

if ret:
    # Guardar la imagen
    cv2.imwrite("img/foto.jpg", frame)
    print("Foto guardada como 'foto.jpg'")
else:
    print("Error: No se pudo capturar la imagen")

# Liberar la cámara
cap.release()
cv2.destroyAllWindows()
