import sqlite3
import subprocess
import os
import hashlib
from datetime import datetime
from src.core.exceptions.exceptions import BusinessException
from src.core.logging.logger import Logger


class CodeRepository:
    def __init__(self, db_path: str, logger: Logger):
        self.db_path = db_path
        self.logger = logger.get_logger()

    def __get_local_ip_from_shell(self) -> str:
        # Private method inside of the class because its not needed anywhere else
        try:
            script_path = os.path.join(
                os.path.dirname(__file__), "../utils/get_ip.sh")
            result = subprocess.run(
                ["bash", script_path], capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return "localhost"

    def save_code(self, code: str, code_type: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ip = self.__get_local_ip_from_shell()
        # More professional way to create the web link
        hash_code = hashlib.sha256(code.encode()).hexdigest()[:4]
        url_generated = (
            # cambiar code
            f"http://{ip}:5001/codes/{now.replace(' ', '-').replace(':', '')}-{hash_code}"
        )
        is_used = 0  # False by default

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO codes (code, type, datetime, url_generated, isUsed)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (code, code_type, now, url_generated, is_used),
                )
                conn.commit()
                self.logger.info(
                    f"Barcode save: {code} ({code_type}) - used: {bool(is_used)}"
                )
        except Exception as e:
            self.logger.error(f"Error saving the code in the BDD: {e}")
            raise BusinessException(
                500, "Error saving the code in the database")

    def mark_as_used(self, code: str):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE codes SET isUsed = 1 WHERE code = ?", (code,))
                conn.commit()
                self.logger.info(f"Codes marked as used: {code}")
        except Exception as e:
            self.logger.error(f"Error trying to mark the code as used: {e}")
            raise BusinessException(
                500, "Error updating the state of the code")
