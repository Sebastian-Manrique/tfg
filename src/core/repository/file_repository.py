from src.core.exceptions.exceptions import BusinessException
from src.core.logging.logger import Logger
from src.core.utils.file_utils import FileUtils


class FileRepository:

    def __init__(self, logger: Logger, file_utils: FileUtils):
        self.logger = logger
        self.file_utils = file_utils

    def get_content_file(self, file_path: str) -> str:
        try:
            return self.file_utils.read_file_content(file_path)
        except BusinessException as eBNE:
            self.logger.error(f"Error getting file {eBNE.code}: {eBNE.description}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error reading {file_path}: {e}")
            raise BusinessException(500, f"Error reading {file_path}: {str(e)}")

    def write_json_news_file(self, string_content: str, output_file: str):
        try:
            self.file_utils.write_content_to_file(string_content, output_file)
        except BusinessException as eBNE:
            self.logger.error(f"Error writing file {output_file}: {eBNE.code}: {eBNE.description}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error writing {output_file}: {e}")
            raise BusinessException(500, f"Error writing {output_file}: {str(e)}")
