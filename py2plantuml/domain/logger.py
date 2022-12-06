
class Logger:
    DEBUG = False
    @staticmethod
    def set_debug() -> None:
        Logger.DEBUG = True
    @staticmethod
    def log_info(line: str) -> None:
        print(line)

    @staticmethod
    def log_debug(line: str) -> None:
        if Logger.DEBUG:
            print(f'{line}')