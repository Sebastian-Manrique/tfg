import logging

from src.core.config.config import Config


class Logger:
    def __init__(self, config: Config):
        log_format = "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        log_level = config.get_env_var(Config.LOG_LEVEL, logging.INFO)
        log_format = config.get_env_var(Config.LOG_FORMAT, log_format)

        formatter = logging.Formatter(log_format)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)

        if not self.logger.handlers:
            self.logger.addHandler(handler)

    def get_logger(self):
        return self.logger
