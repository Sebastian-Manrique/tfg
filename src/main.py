from src.core.di.container import Container
from src.core.exceptions.exceptions import BusinessException
import threading
import signal
import sys

# Event to indicate when exit
shutdown_event = threading.Event()


if __name__ == "__main__":
    container = Container()

    logger_instance = container.logger()
    logger = logger_instance.get_logger()
    logger.info("Sistema iniciado")
    
    def handle_exit(sig, frame):
        logger.info("Shouting down hardware...")
        container.barcode_scanner().hardware.cleanup()
        shutdown_event.set()
        sys.exit(0)


    # Register signals
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        container.sound_player().play_sound()
        container.barcode_scanner().hardware.blink_camera(times=3, delay=0.2)
        # Lauch flask app in a thread
        app = container.api_app()

        def run_flask():
            app.run(host="0.0.0.0", port=5001, debug=False)

        flask_thread = threading.Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

        # Puedes dejar este hilo esperando
        logger.info("Web server active. CTRL+C to quit.")
        shutdown_event.wait()

    except BusinessException as e:
        logger.error(f"Bussiness error {e.code}: {e.description}")
    except Exception as e:
        logger.exception(f" Unexpected error: {e}")
    finally:
        logger.info(" Shouting down.")
