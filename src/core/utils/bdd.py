from src.core.utils.file_utils import FileUtils
from src.core.repository.file_repository import FileRepository
from src.core.logging.logger import Logger
from src.core.config.config import Config
import json

# Instancias necesarias para usar FileRepository
config = Config()
logger = Logger(config)
file_utils = FileUtils()
file_repo = FileRepository(logger, file_utils)

# Leemos el JSON de traducciones
try:
    file_content = file_repo.get_content_file('src/core/config/translations.json')
    translations = json.loads(file_content)
    print(f"Traducciones cargadas correctamente:\n{translations}")
except Exception as e:
    print(f"Error cargando traducciones: {e}")
    translations = {"es": {}, "en": {}}  # fallback vacío
