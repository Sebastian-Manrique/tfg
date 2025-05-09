import os
from threading import Lock


class Config:
    _instance = None
    _lock = Lock()

    LOG_LEVEL = 'LOG_LEVEL'
    LOG_FORMAT = 'LOG_FORMAT'

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Config, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        if not hasattr(self, 'environ_dict'):
            self.environ_dict = {}

    def get_env_var(self, var_name, default_value=None):
        """Get the value of an environment variable.
        If the environment variable does not exist, it will be created,
        and the default value will be returned.
        """
        if var_name not in self.environ_dict:
            self.environ_dict[var_name] = os.getenv(var_name, default_value)
        return self.environ_dict[var_name]
