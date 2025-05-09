from dependency_injector import containers, providers

from src.core.config.config import Config
from src.core.logging.logger import Logger
from src.core.repository.file_repository import FileRepository
from src.core.utils.file_utils import FileUtils
from src.core.utils.sound_player import SoundPlayer
from src.core.services.barcode_scanner_service import BarcodeScannerService


class Container(containers.DeclarativeContainer):
    config = providers.Singleton(Config)
    logger = providers.Singleton(Logger, config=config)
    file_utils = providers.Factory(FileUtils)
    file_repository = providers.Factory(FileRepository, logger=logger, file_utils=file_utils)

    sound_player = providers.Factory(
        SoundPlayer,
        logger=logger,
        sound_file="sound/beep.wav"
    )

    barcode_scanner = providers.Factory(
        BarcodeScannerService,
        sound_player=sound_player,
        logger=logger,
        image_output="code.png"
    )
