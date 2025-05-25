# Final Degree Project

<p align="center">
    <img src="https://skillicons.dev/icons?i=git,python,raspberrypi,opencv,linux,flask,sqlite" />
</p>

# ECO Return

**ECO Return** is a smart recycling system based on computer vision and hardware control, developed as a Final Degree Project. Its goal is to promote recycling through automatic waste identification, incentives, and ticket generation. The system is autonomous, portable, and scalable.

## Description

The system aims to facilitate the automatic classification of waste using a camera connected to a Raspberry Pi, employing barcode scanning with OpenCV and object detection using a YOLO model.

It has been developed with a modular architecture based on Flask, applying principles of responsibility separation and dependency injection (DI).

## 🎯 Project Objectives

The main goal of ECO Return is to develop a smart recycling system that allows:

- Identifying waste using barcodes or computer vision.
- Automatically classifying it by material (plastic, can, etc.).
- Logging the detected waste into a local database.
- Providing auditory and visual feedback (e.g., a beep if successfully detected).
- Printing a summary or reward using a thermal printer.

This system is designed to integrate into various smart collection points, encouraging recycling through incentives.

## ⚙️ General Functionality

1. The user presents the waste in front of the camera.
2. The system scans a barcode using OpenCV or detects the object type with YOLO.
3. A materials dictionary (`material_codes.json`) is consulted to determine the waste type (if barcode is detected).
4. The data is logged in a local SQLite database.
5. A confirmation sound is played, and a summary ticket is printed if the printer is enabled.

## 📚 Main Dependencies

- `flask`: Web server and API
- `opencv-python`: Image capture and processing
- `ultralytics`: YOLO visual detection model
- `python-escpos`: ESC/POS printing via serial port
- `simpleaudio`: Sound playback
- `sqlite3`: Embedded database

...

# 🔍 Technical Details

## 📷 Detection with OpenCV

OpenCV is used to capture frames from the camera and detect barcodes.

The code is encapsulated in the `barcode_scanner_service.py` service.

## 🧠 Computer Vision with YOLO

A custom model trained with images of waste is used.

The `yolo_service.py` file is responsible for invoking inference and returning labels and confidence.

## 🧩 Reusing the Computer Vision Module

The entire operation of the computer vision detection model is encapsulated in the `<code>/yolo</code>` directory, allowing for easy reuse in other projects.

## 🔁 Portability

The model is trained and exported in TorchScript and NCNN formats, making it compatible with various platforms, including Raspberry Pi and embedded environments.

The execution file (`yolo_detect.py`) contains all the logic needed to load the model, process an image, and return detection results.

It does not depend on the rest of the system, so it can be integrated into other projects simply by importing that module and adapting input/output.

## 📦 Module Contents

```bash
/yolo/
├── my_model_ncnn_model/
│   ├── metadata.yaml
│   └── model_ncnn.py
├── my_model.torchscript
├── train/
│   ├── args.yaml
│   ├── results.csv
│   └── weights/
└── yolo_detect.py
```

This directory also includes the classes and training results of the model.

## 📄 How to Reuse It

```python
import cv2
from yolo.yolo_detect import detect_objects

# Path to the image and model
img_path = "path/to/img"
model_path = "yolo/my_model.torchscript"

# Load the image
img = cv2.imread(img_path)
if img is None:
    raise FileNotFoundError(f"Unable to load image: {img_path}")

# Detect objects and get annotated image
result, img_annotated = detect_objects(img, model_path=model_path)

# Display results in the console
for label, trust in result:
    print(f"Detected: {label} ({trust:.2f})")

# Save image with detection results
output_path = "result_detected.jpg"
cv2.imwrite(output_path, img_annotated)
print(f"Image with results saved in: {output_path}")
```

With `yolo_detect`, the `detect_objects` function allows it to be used in any other project.

## 🖨️ Thermal Printer

The printer is controlled using the `thermal_printer_service.py` module, via serial communication and ESC/POS commands using the `Serial` class.

When used:

`from escpos.printer import Serial`

This is part of the `python-escpos` library.

It prints a recycling summary (material, date, discount, etc.).

In my case, the printer used works with both `python-escpos` and `adafruit_thermal_printer`, so two test files were created.

## ESC/POS

```python
printer = Serial(devfile="/dev/ttyUSB0", baudrate=9600, timeout=3)

print("Feeding paper...")

printer.text("\n" * 2)

print("Paper fed!")
```

## adafruit

```python
# More code here: https://learn.adafruit.com/mini-thermal-receipt-printer/circuitpython
# On the Raspberry Pi with USB
import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3000)

import adafruit_thermal_printer
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)

printer = ThermalPrinter(uart)
print("Feeding paper!")

printer.feed(2)

print("Paper fed!")
```

## 🔬 Quick Test

1. Clone the repository:

```bash
git clone https://github.com/Sebastian-Manrique/tfg.git
cd tfg-eco-return
```

🐍 Virtual environment installation (venv)

To isolate project dependencies and simplify installation on other systems, it's recommended to use a Python virtual environment.

2. Create the virtual environment
   From the root of the project, run:

```bash
python3 -m venv venv
```

This will create a `venv/` folder containing the virtual environment.

3. Activate the virtual environment (On Linux, if `libasound2-dev` is not installed, run `sudo apt install libasound2-dev`)

```bash
source venv/bin/activate
```

🔹 On Windows (Note: `simpleaudio` package may have issues if Microsoft Visual C++ is not installed https://visualstudio.microsoft.com/es/visual-cpp-build-tools/)

```bash
venv\Scripts\activate
```

If using PowerShell, change `Scripts\activate` to `Scripts\Activate.ps1`.

4. Install dependencies
   With the virtual environment activated, install all required libraries:

```bash
pip install -r requirements.txt
```

5. Verify everything works
   Run a quick test:

```bash
python src/main.py
```

Or run any script to verify the installation.

6. Deactivate the virtual environment (optional)
   When finished, deactivate the environment with:

```bash
deactivate
```

## 🏗️ Architecture

The project follows a modular architecture, using Flask as the main web framework and applying principles of responsibility separation, dependency injection (DI), and best practices for scalability and maintainability.

Additionally, a logging system (in `src/core/logging`) based on Python’s `logging` module has been incorporated, which records:

- System events (startup, shutdown, model loading)
- User activities (detections, recycling actions)
- Errors (hardware issues, connection failures, etc.)

These logs are essential for traceability, debugging, and continuous improvement of the system. They are ready to be redirected to the console, files, or external systems if needed.

## 🧱 Structure

The project is designed with clear dependencies and packages in mind.

| 📂 Folder / 📄 File    | 📝 Description                                                                                                             |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| `src/`                 | 💻 Main backend code (API, business logic, utilities, configuration).                                                      |
| `src/api/`             | 🌐 Flask modules, including endpoints, HTML templates, CSS, and JS.                                                        |
| `src/core/services/`   | 🧠 System services such as barcode scanning, thermal printing, and computer vision.                                        |
| `src/core/utils/`      | 🛠️ Utility functions: file handling, hardware, local IP, sound, etc.                                                       |
| `src/core/config/`     | ⚙️ Configurations: translations, material codes.                                                                           |
| `src/core/database/`   | 🗂️ Database directory, `allCodes.db`.                                                                                      |
| `src/core/di/`         | 📦 Dependency injection container module.                                                                                  |
| `src/core/logging/`    | 📋 Logger used across classes.                                                                                             |
| `src/core/repository/` | 🧰 🗄️ Design pattern repositories (not Git). Encapsulates data access, local IP queries, file handling, and DB operations. |
| `yolo/`                | 🤖 Computer vision module. Contains trained models, YOLO config, and scripts.                                              |
| `sound/`               | 🔊 Sound effects (confirmation beeps).                                                                                     |
| `requirements.txt`     | 📦 Python dependency list.                                                                                                 |

## 📁 Project Structure

```bash
├── README.md
├── requirements.txt
├── sound
│   └── beep.wav
├── sql-view.py
├── src
│   ├── api
│   │   ├── endpoints.py
│   │   ├── __init__.py
│   │   ├── static
│   │   │   ├── css
│   │   │   │   └── styles.css
│   │   │   ├── img
│   │   │   └── js
│   │   │       └── script.js
│   │   └── templates
│   │       ├── camera.html
│   │       ├── summary.html
│   │       └── template.html
│   ├── core
│   │   ├── config
│   │   │   ├── config.py
│   │   │   ├── __init__.py
│   │   │   ├── material_codes.json
│   │   │   └── translations.json
│   │   ├── database
│   │   │   └── allCodes.db
│   │   ├── di
│   │   │   ├── container.py
│   │   │   └── __init__.py
│   │   ├── exceptions
│   │   │   ├── exceptions.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── logging
│   │   │   ├── __init__.py
│   │   │   └── logger.py
│   │   ├── repository
│   │   │   ├── code_repository.py
│   │   │   ├── file_repository.py
│   │   │   └── __init__.py
│   │   ├── services
│   │   │   ├── barcode_scanner_service.py
│   │   │   ├── __init__.py
│   │   │   ├── thermal_printer_service.py
│   │   │   └── yolo_service.py
│   │   └── utils
│   │       ├── bdd.py
│   │       ├── file_utils.py
│   │       ├── get_ip.sh
│   │       ├── hardware_controller.py
│   │       ├── __init__.py
│   │       ├── shared_flags.py
│   │       └── sound_player.py
│   ├── __init__.py
│   ├── main.py
│   ├── printer.py
│   └── test_printer.py
├── test-bdd.py
└── yolo
    ├── __init__.py
    ├── my_model_ncnn_model
    │   ├── metadata.yaml
    │   └── model_ncnn.py
    ├── my_model.torchscript
    ├── train
    │   ├── args.yaml
    │   ├── results.csv
    │   └── weights
    └── yolo_detect.py
```

## Español

Este es el mismo [README](README.md) en español.
