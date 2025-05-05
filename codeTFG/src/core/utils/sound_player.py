import simpleaudio as sa

from src.core.exceptions.exceptions import BusinessException
from src.core.logging.logger import Logger


class SoundPlayer:
    def __init__(self, sound_file: str, logger: Logger):
        self.logger = logger.get_logger()
        try:
            self.sound_file = sound_file
        except Exception as e:
            raise BusinessException(500, f"Error loading sound file: {e}")

    def play_sound(self):
        self.logger.info(f"Start play sound: {self.sound_file}")
        try:
            wave_obj = sa.WaveObject.from_wave_file(self.sound_file)
            wave_obj.play()
        except Exception as e:
            self.logger.error(f"Error playing sound: {e}")
            raise BusinessException(500, f"Error playing sound: {e}")
