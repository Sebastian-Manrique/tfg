import cv2
from pyzbar import pyzbar
import sqlite3
import os

# Launch the camera
cap = cv2.VideoCapture(0)

# Verify if the camera was opened correctly
if not cap.isOpened():
    print("Error: Unable to access the camera")
    exit()

# Cature a single frame
ret, frame = cap.read()

if ret:
    # Create the subfolder if it doesn't exist
    os.makedirs("img/read", exist_ok=True)

    # Search for the next available number, to save the image
    counter = 1
    while os.path.exists(os.path.join("img", f"photo{counter}.jpg")):
        counter += 1

    # Final name of the new image
    new_name = os.path.join("img", f"photo{counter}.jpg")

    # Save the image
    cv2.imwrite("img/photo.jpg", frame)
    os.rename("img/photo.jpg", new_name)
    print(f"Photo save as photo{counter}.jpg")

    # SQLite was used because it is simpler and nothing needs to be installed.
    # A table called “codigos” was created with the fields “id” and “codigo”.

    # Read the QR code
    img = cv2.imread(new_name)

    barcodes = pyzbar.decode(img)

    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(img, (x, y), (x+w, y+h), (0, 0, 255), 4)
        bdata = barcode.data.decode("utf-8")
        btype = barcode.type
        text = f"{bdata}, {btype}"
        cv2.putText(img, text, (x, y-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    name_read = os.path.join("img/read", os.path.basename(new_name))
    cv2.imwrite(name_read, img)
    cv2.imshow("foto", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    with sqlite3.connect("allCodes.db") as conn:
        cursor = conn.cursor()
        # Insert the code into the database
        cursor.execute(
            'INSERT INTO codes(code, type) VALUES(?, ?)', (bdata, btype))
        conn.commit()


else:
    print("Error: Unable to capture image")

# Release the camera
cap.release()
cv2.destroyAllWindows()
