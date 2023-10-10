import logging
import config
import os

class LoggerClass(object):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if LoggerClass.__instance is None:
            LoggerClass.__instance = object.__new__(cls)
        return LoggerClass.__instance

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] - %(message)s')

        if (not config.logger_append):
            self.logger.handlers.clear()
            open('logs.log', 'w').close()
        
        self.file_handler = logging.FileHandler('logs.log')
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)

        if (config.logger_console_print):
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setFormatter(self.formatter)
            self.logger.addHandler(self.stream_handler)

        if (config.logger_tail):
            if (config.env_os == 0):
                os.system("xterm -T \"Pro Scraper (Logger)\" -e \"tail -f logs.log\"")
            elif (config.env_os == 1):
                os.system("start \"Pro Scraper (Logger)\" cmd /c tail -f logs.log")
        

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def warning(self, message):
        self.logger.warning(message)    
    
    def debug(self, message):
        self.logger.debug(message)
    
    def critical(self, message):
        self.logger.critical(message)
    
    def exception(self, message):
        self.logger.exception(message)

logger =  LoggerClass()