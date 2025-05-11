from flask import Flask, render_template, Response, jsonify, after_this_request
import cv2

app = Flask(__name__)

translations = {
    'es': {
        'title': 'Backend de Escáner de Botellas',
        'status': 'Estado de la máquina',
        'manual_scan': 'Iniciar escaneo manual',
        'video_actual': 'Video actual de la cámara',
        'ver_camara': 'Ver cámara en linea',
        'restart': 'Reiniciar máquina',
    },
    'en': {
        'title': 'Bottle Scanner Backend',
        'status': 'Machine Status',
        'manual_scan': 'Start Manual Scan',
        'video_actual': 'Actual camera video',
        'ver_camara': 'View camera online',
        'restart': 'Restart Machine',
    }
}

camera = cv2.VideoCapture(0)  # Open the default camera (0)


def camera_frames():
    while True:
        isEnable, frame = camera.read()
        if not isEnable:
            print("Failed to capture image")
            break
        else:
            # Encode the frame as JPEG
            response, jpeg = cv2.imencode('.jpg', frame)
            frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    hour_fun_flask = "12:79"
    camera_fun_flask = True
    return render_template("camera.html", hora=hour_fun_flask, cameraBool=camera_fun_flask, lang=translations['es'])


@app.route('/en')
def index_en():
    hour_fun_flask = "12:79"
    camera_fun_flask = True
    return render_template("camera.html", hora=hour_fun_flask, cameraBool=camera_fun_flask, lang=translations['en'])


@app.route('/video')
def camera_stream():
    return Response(camera_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/restart-camera', methods=['POST'])
def restart():
    camera.release()
    return jsonify({"status": "Camera restarted"})


app.run(host="0.0.0.0", port=5001, debug=True)
