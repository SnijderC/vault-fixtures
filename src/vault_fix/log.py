import logging

from rich.logging import RichHandler


def get_log_level(verbose):
    log_levels = [logging.ERROR, logging.WARNING, logging.INFO, logging.DEBUG]
    return log_levels[min(len(log_levels) - 1, verbose)]


def get_logger(name: str, level: int):
    logging.basicConfig(
        level=level,
        format="[%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(rich_tracebacks=True)],
    )
    log = logging.getLogger(name)
    log.setLevel(level)
    return log
