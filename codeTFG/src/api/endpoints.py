from flask import Flask, render_template

app = Flask(__name__)


translations = {
    'es': {
        'title': 'Backend de Escáner de Botellas',
        'status': 'Estado de la máquina',
        'manual_scan': 'Iniciar escaneo manual',
        'restart': 'Reiniciar máquina',
    },
    'en': {
        'title': 'Bottle Scanner Backend',
        'status': 'Machine Status',
        'manual_scan': 'Start Manual Scan',
        'restart': 'Restart Machine',
    }
}

@app.route('/camera')
def hello():
    hora_fun_flask = "12:79"
    camera_fun_flask = True
    return render_template("camera.html", hora=hora_fun_flask, cameraBool=camera_fun_flask)

app.run(host="0.0.0.0", port=301, debug=True)