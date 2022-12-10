
from infrastructure.generic_classes import GenericLogger

class Logger(GenericLogger):
    def __init__(self, debug: bool = False):
        self.debug = debug

    def set_debug(self) -> None:
        self.debug = True

    def log_info(self, line: str) -> None:
        print(f'INFO: {line}')

    def log_error(self, line: str) -> None:
        print(f'ERROR: {line}')


    def log_debug(self, line: str) -> None:
        if self.debug:
            print(f'DEBUG: {line}')