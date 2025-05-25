# Trabajo de Fin de Grado

<p align="center">
    <img src="https://skillicons.dev/icons?i=git,python,raspberrypi,opencv,linux,flask,sqlite" />
</p>

# ECO Return

**ECO Return** es un sistema de reciclaje inteligente basado en visión por ordenador y control de hardware, desarrollado como Trabajo de Fin de Grado. El objetivo es fomentar el reciclaje mediante identificación automática de residuos, incentivos y generación de tickets. El sistema es autónomo, portátil y escalable.

## Descripción

El sistema tiene como objetivo facilitar la clasificación automática de residuos mediante una cámara conectada a una Raspberry Pi, empleando escaneo de códigos de barras con OpenCV y un modelo de detección con YOLO.

Se ha desarrollado con una arquitectura modular basada en Flask, aplicando principios de separación de responsabilidades y patrón de inyección de dependencias (DI).

## 🎯 Objetivos del Proyecto

El objetivo principal de ECO Return es desarrollar un sistema de reciclaje inteligente que permita:

Identificar residuos mediante códigos de barras o visión artificial.

Clasificarlos automáticamente según el material (plástico, lata, etc.).

Registrar los residuos detectados en una base de datos local.

Generar respuestas sonoras y visuales del resultado (por ejemplo, un beep si se ha detectado correctamente).

Imprimir un resumen o recompensa mediante una impresora térmica.

Este sistema está pensado para integrarse en diferentes lugares de recogida inteligente, fomentando el reciclaje con incentivos.

## ⚙️ Funcionamiento General

1. El usuario introduce el residuo frente a la cámara.

2. El sistema permite escanear un código de barras con OpenCV o detectar con YOLO el tipo de objeto visualmente.

3. Se consulta un diccionario de materiales (material_codes.json) para determinar el tipo de residuo (si se detecta el codigo de barras).

4. Se registra la información en la base de datos SQLite.

5. Se reproduce un sonido de confirmación y se imprime un ticket resumen si está habilitada la impresora.

## 📚 Dependencias principales

- `flask`: servidor web y API
- `opencv-python`: captura y procesamiento de imágenes
- `ultralytics`: modelo YOLO para detección visual
- `python-escpos`: impresión ESC/POS por puerto serie
- `simpleaudio`: reproducción de sonido
- `sqlite3`: base de datos embebida

<br>

<h1> 🔍 Detalles Técnicos

## 📷 Detección con OpenCV

Se emplea OpenCV para capturar frames desde la cámara y detectar códigos de barras.

El código está encapsulado en el servicio barcode_scanner_service.py.

## 🧠 Visión Artificial con YOLO

Se utiliza un modelo personalizado entrenado con imágenes de residuos.

El archivo yolo_service.py es responsable de invocar la deducción, devolver etiquetas y confianza.

## 🧩 Reutilización del Módulo de Visión Artificial

Todo el funcionamiento del modelo de detección por visión artificial está encapsulado en el directorio <code>/yolo</code>, lo que permite su fácil reutilización en otros proyectos.

## 🔁 Portabilidad

El modelo está entrenado y exportado en formatos torchscript y ncnn, lo que lo hace compatible con diversas plataformas, incluidas Raspberry Pi y entornos embebidos.

El archivo de ejecución con el que se puede probar (yolo_detect.py) contiene toda la lógica necesaria para cargar el modelo, procesar una imagen y devolver los resultados de detección.

No depende del resto del sistema, por lo que puede integrarse en otros proyectos simplemente importando ese módulo y adaptando la entrada/salida.

## 📦 Contenido del Módulo

```bash
/yolo/
├── my_model_ncnn_model/
│ ├── metadata.yaml
│ └── model_ncnn.py
├── my_model.torchscript
├── train/
│ ├── args.yaml
│ ├── results.csv
│ └── weights/
└── yolo_detect.py
```

Aqui tambien estan incluidas las clases y los resultados del entrenamiento de este modelo.

## 📄 Cómo reutilizarlo

```python

import cv2
from yolo.yolo_detect import detect_objects

"""Route to the image and the model"""

img_path = "path/to/img"
model_path = "yolo/my_model.torchscript"

"""Load the img"""

img = cv2.imread(img_path)
if img is None:
raise FileNotFoundError(f"Unable to load image: {img_path}")

"""Detect objects and obtain annotated image"""

result, img_annotated = detect_objects(img, model_path=model_path)

"""Show results by console"""

for label, trust in result:
    print(f"Detectado: {label} ({trust:.2f})")

"""Save image with results"""

output_path = "result_detected.jpg"

cv2.imwrite(output_path, img_annotated)
print(f"Image with results saved in: {output_path}")

```

Con el `yolo_detect` la función `detect_objects` permite usarlo en cualquier otro proyecto

## 🖨️ Impresora térmica

La impresora se controla mediante el módulo thermal_printer_service.py, utilizando comunicación serie e imprimiendo mediantes comandos ESC/POS gracias a la libreria, `con Serial`

Cuando se usa:

`from escpos.printer import Serial`

Esta forma parte de la librería `python-escpos`

Esta imprime un resumen del reciclaje (material, fecha, descuento, etc.).

En mi caso, la impresora que utilice funciona tanto con `python-escpos` como con `adafruit_thermal_printer`,
pero para estar seguro, aqui cree dos archivos de prueba.

## ESC/POS

```python
printer = Serial(devfile="/dev/ttyUSB0", baudrate=9600, timeout=3)

print("Rodando papel...")

printer.text("\n" * 2)

print("Papel rodado!")
```

## adafruit

```python
# mas codigo aqui: https://learn.adafruit.com/mini-thermal-receipt-printer/circuitpython
# On the Raspberry Pi with USB
import serial
uart = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=3000)

import adafruit_thermal_printer
ThermalPrinter = adafruit_thermal_printer.get_printer_class(2.69)

printer = ThermalPrinter(uart)
print("Rodando papel!")

printer.feed(2)

print("Papel rodado!")
```

## 🔬 Prueba rápida

1. Clona el repositorio:

```bash
git clone https://github.com/Sebastian-Manrique/tfg.git
cd tfg-eco-return
```

🐍 Instalación del entorno virtual (venv)

Para aislar las dependencias del proyecto y facilitar la instalación en otros sistemas, se recomienda usar un entorno virtual de Python.

2. Crear el entorno virtual
   Desde la raíz del proyecto, ejecuta:

```python
python3 -m venv venv
```

Esto creará una carpeta venv/ que contiene el entorno virtual.

3. Activar el entorno virtual (En Linux da problemas si no se tiene instalado `libasound2-dev` instalar con `sudo apt install libasound2-dev`)

```python
   source venv/bin/activate
```

🔹 En Windows (limitante en Windows y el paquete simpleaudio da problemas si no se tiene Microsoft Visual C++ instalado https://visualstudio.microsoft.com/es/visual-cpp-build-tools/)

```python
venv\Scripts\activate
```

Si usas PowerShell, cambia `Scripts\activate` por `Scripts\Activate.ps1`.

4. Instalar dependencias con el entorno activado, instala todas las librerías necesarias:

```python
pip install -r requirements.txt
```

5. Verificar que todo está funcionando
   Lanza una prueba rápida:

```python
python src/main.py
```

O el archivo que quieras ejecutar para verificar la instalación.

6. Desactivar el entorno virtual (opcional)
   Cuando termines de trabajar, puedes desactivar el entorno virtual con:

```python
deactivate
```

## 🏗️ Arquitectura

El proyecto está desarrollado siguiendo una arquitectura modular, utilizando Flask como framework web principal y aplicando principios de separación de responsabilidades, inyección de dependencias (DI) y buenas prácticas de escalabilidad y mantenimiento.

Además, se ha incorporado un sistema de logging (src/core/logging) basado en el módulo logging de Python, que permite registrar:

- Eventos del sistema (inicio, apagado, carga de modelos)

- Actividades del usuario (detecciones, reciclajes)

- Errores (problemas de hardware, fallos de conexión, etc.)

Estos logs son esenciales para la trazabilidad, depuración y mejora continua del sistema, y están listos para redirigirse a consola, archivos o sistemas externos si fuera necesario.

<br>

# 🧱 Estructura

El proyecto esta diseñado teniendo en cuenta las dependencias y los paquetes.

| 📂 Carpeta / 📄 Archivo | 📝 Descripción                                                                                                                                                                                                                                                                             |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `src/`                  | 💻 Contiene el código principal del backend (API, lógica de negocio, utilidades, configuración).                                                                                                                                                                                           |
| `src/api/`              | 🌐 Módulos de Flask, incluyendo endpoints, plantillas HTML, CSS y JS.                                                                                                                                                                                                                      |
| `src/core/services/`    | 🧠 Servicios del sistema como escaneo de códigos, impresión térmica y detección por visión artificial.                                                                                                                                                                                     |
| `src/core/utils/`       | 🛠️ Funciones auxiliares: manejo de ficheros, hardware, IP local, sonido, etc.                                                                                                                                                                                                              |
| `src/core/config/`      | ⚙️ Ccnfiguraciones: traducciones, codigos de los materiales.                                                                                                                                                                                                                               |
| `src/core/database/`    | 🗂️ Directorio de la Base De Datos, allCodes.db.                                                                                                                                                                                                                                            |
| `src/core/di/`          | 📦 Modulo del contenedor, en cual inyecta todas las clases.                                                                                                                                                                                                                                |
| `src/core/logging/`     | 📋 Contiene el logger usado en todas las clases.                                                                                                                                                                                                                                           |
| `src/core/repository/`  | 🧰 🗄️ Contiene los repositories del proyecto (repositorios en el sentido del patrón de diseño, no relacionados con Git). Estas clases encapsulan el acceso a datos, incluyendo operaciones para obtener la IP local, leer y escribir archivos, y consultar o actualizar la base de datos.. |
| `yolo/`                 | 🤖 Módulo de visión artificial. Contiene modelos entrenados, información sobre este, scripts y configuración YOLO.                                                                                                                                                                         |
| `sound/`                | 🔊 El efecto de sonido utilizados (confirmaciones sonoras).                                                                                                                                                                                                                                |
| `requirements.txt`      | 📦 Lista de dependencias Python necesarias para el proyecto.                                                                                                                                                                                                                               |

<br>

## 📁 Estructura del proyecto

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

</pre>

## English

This is the same [README](README_EN.md) in english.
