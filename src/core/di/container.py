from dependency_injector import containers, providers
from escpos.printer import Serial

from src.core.config.config import Config
from src.core.logging.logger import Logger
from src.core.repository.file_repository import FileRepository
from src.core.repository.code_repository import CodeRepository
from src.core.services.barcode_scanner_service import BarcodeScannerService
from src.core.services.thermal_printer_service import ThermalPrinterService
from src.core.services.yolo_service import YOLOService
from src.core.utils.file_utils import FileUtils
from src.core.utils.sound_player import SoundPlayer

# IMPORTANT: import the Flask app at the end to avoid circular dependencies
import src.api.endpoints as api_endpoints


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Config)

    logger = providers.Singleton(Logger, config=config)

    file_utils = providers.Factory(FileUtils)

    file_repository = providers.Factory(
        FileRepository, logger=logger, file_utils=file_utils
    )

    sound_player = providers.Factory(
        SoundPlayer,
        logger=logger.provided.get_logger.call(),
        sound_file="sound/beep.wav",
    )

    code_repository = providers.Singleton(
        CodeRepository, db_path="src/core/database/allCodes.db", logger=logger
    )

    printer = providers.Singleton(
        Serial, devfile="/dev/ttyUSB0", baudrate=9600, timeout=1
    )

    thermal_printer = providers.Factory(
        ThermalPrinterService,
        printer=printer,
        logger=logger,
        code_repository=code_repository,
    )

    barcode_scanner = providers.Factory(
        BarcodeScannerService,
        sound_player=sound_player,
        logger=logger,
        image_output="output.jpg",
        code_repository=code_repository,
        file_repository=file_repository,
        thermal_printer_service=thermal_printer,
    )

    yolo_service = providers.Factory(
        YOLOService,
        model_path="yolo/my_model.pt",
        logger=logger,
        sound_player=sound_player,
        hardware_controller=barcode_scanner.provided.hardware,
    )

    api_app = providers.Object(api_endpoints.app)
