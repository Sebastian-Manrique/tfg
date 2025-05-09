import errno
import os

from src.core.exceptions.exceptions import BusinessException


class FileUtils:
    @staticmethod
    def read_file_content(file_path: str) -> str:
        if not os.path.isfile(file_path):
            raise BusinessException(404, f"File '{file_path}' does not exist.")

        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            raise BusinessException(500, f"Failed to read file '{file_path}': {str(e)}")

    @staticmethod
    def write_content_to_file(content: str, file_path: str):
        if not isinstance(content, str):
            raise BusinessException(400, "Content must be a string")
        if not isinstance(file_path, str):
            raise BusinessException(400, "File path must be a string")

        if not content.strip():
            raise BusinessException(400, "Content must not be empty")

        try:
            if not os.path.exists(os.path.dirname(file_path)):
                try:
                    os.makedirs(os.path.dirname(file_path))
                except OSError as exc:
                    if exc.errno != errno.EEXIST:
                        raise BusinessException(500, f"Error creating directories: {str(exc)}")

            with open(file_path, 'w') as f:
                f.write(content)

        except Exception as e:
            raise BusinessException(500, f"Error writing to file: {str(e)}")
