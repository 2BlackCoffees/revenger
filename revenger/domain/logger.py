
from infrastructure.generic_classes import GenericLogger

class Logger(GenericLogger):
    def __init__(self, info: bool = False, debug: bool = False, trace: bool = False):
        self.trace = trace
        self.debug = debug
        self.info = info


    def set_debug(self) -> None:
        self.debug = True

    def set_trace(self) -> None:
        self.trace = True

    def log_info(self, line: str) -> None:
        if self.info or self.debug or self.trace:
            print(f'INFO (py): {line}')

    def log_error(self, line: str) -> None:
        print(f'ERROR (py): {line}')

    def log_warn(self, line: str) -> None:
        print(f'WARN (py): {line}')

    def log_debug(self, line: str) -> None:
        if self.debug or self.trace:
            print(f'DEBUG (py): {line}')

    def log_trace(self, line: str) -> None:
        if self.trace:
            print(f'TRACE (py): {line}')