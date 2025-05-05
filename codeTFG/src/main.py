from src.core.di.container import Container
from src.core.exceptions.exceptions import BusinessException

if __name__ == '__main__':
    container = Container()

    logger_instance = container.logger()
    logger = logger_instance.get_logger()
    logger.info("Start main")

    try:
        sound = container.sound_player()
        sound.play_sound()

        scanner = container.barcode_scanner()
        scanner.start_scanning()
    except BusinessException as eBNE:
        logger.error(f"Error when instance the BarcodeScannerService class {eBNE.code}: {eBNE.description}")
    finally:
        logger.info("Finish main")

