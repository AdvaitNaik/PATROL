import logging
import logging.config
import os
from pathlib import Path

FILE_PATH = Path(__file__)
SOURCE_PATH = FILE_PATH.parent.parent
STATIC_PATH = os.path.join(SOURCE_PATH, "static")
LOG_CONFIG_PATH = os.path.join(STATIC_PATH, "log_config.ini")

logging.config.fileConfig(LOG_CONFIG_PATH)
 
# create logger
class Logger:
    def __init__(self, name, filename="/tmp/patrol.log", level="INFO") -> None:
        self.name = name
        self.filename = filename
        self.level = level
  
        self.logger = logging.getLogger(f"PATROL: {self.name}")

        self.handler = logging.FileHandler(self.filename)
        self.handler.setLevel(self.level)
        formatter=logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        
# 'application' code
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warn message')
# logger.error('error message')
# logger.critical('critical message')

# if __name__ == "__main__":
#     logger = Logger("test").logger
#     logger.info("test")