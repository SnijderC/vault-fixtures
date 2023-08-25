import enum
from types import TracebackType
from typing import Type

from rich.console import Console
from rich.traceback import Traceback


class LogLevel(enum.IntEnum):
    DEBUG = 5
    INFO = 4
    WARNING = 3
    ERROR = 2
    CRITICAL = 1

    def _missing_(self):
        return LogLevel.DEBUG


class Logger:
    def __init__(self, log_level=LogLevel.ERROR) -> None:
        self._console = Console(stderr=True)
        self.level = log_level

    def debug(self, msg: str) -> None:
        self.log(f"[gray]DEBUG[/] {msg}", level=LogLevel.DEBUG)

    def info(self, msg: str) -> None:
        self.log(f"[blue]INFO[/] {msg}", level=LogLevel.INFO)

    def warning(self, msg: str) -> None:
        self.log(f"[yellow]WARNING[/] {msg}", level=LogLevel.WARNING)

    def error(self, msg: str) -> None:
        self.log(f"[bold red]ERROR[/] {msg}", level=LogLevel.ERROR)

    def critical(self, msg: str) -> None:
        self.log(f"[bold yellow on red]CRITICAL[/] {msg}", level=LogLevel.CRITICAL)

    def log(self, msg: str, *, level: LogLevel) -> None:
        if level <= self.level:
            self._console.log(msg)

    def exception(self, exc_type: Type[BaseException], exc_val: BaseException, exc_tb: TracebackType) -> None:
        self._console.print(Traceback.from_exception(exc_type, exc_val, exc_tb))
