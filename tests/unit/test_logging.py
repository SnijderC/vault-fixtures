import sys
from unittest import mock

import pytest
from vault_fix._log import Logger, LogLevel


@pytest.mark.parametrize("msg_level", list(LogLevel), ids=lambda lvl: f"msg-lvl-{lvl}")
@pytest.mark.parametrize("log_level", list(LogLevel), ids=lambda lvl: f"log-lvl-{lvl}")
def test_levels_respected(msg_level: LogLevel, log_level: int):
    with mock.patch("vault_fix._log.Console") as mock_console:
        log = Logger(log_level=LogLevel(log_level))
        log.log("foo", level=msg_level)

        if msg_level <= LogLevel(log_level):
            assert mock_console.return_value.log.call_count == 1
        else:
            assert mock_console.return_value.log.call_count == 0


@pytest.mark.parametrize(
    "method, level",
    [
        ["debug", LogLevel.DEBUG],
        ["info", LogLevel.INFO],
        ["warning", LogLevel.WARNING],
        ["error", LogLevel.ERROR],
        ["critical", LogLevel.CRITICAL],
    ],
    ids=lambda lvl: f"log-lvl-{lvl}",
)
def test_log_methods_call_with_correct_level(method: str, level: LogLevel) -> None:
    with mock.patch("vault_fix._log.Logger.log") as mock_log:
        log = Logger(log_level=LogLevel.DEBUG)
        getattr(log, method)("foo")
        assert mock_log.call_args[1]["level"] == level


def test_log_level_too_high():
    assert LogLevel(max(LogLevel) + 1) == LogLevel.DEBUG


def test_log_trace():
    log = Logger(log_level=LogLevel.DEBUG)
    with mock.patch.object(log._console, "print") as mock_print:
        try:
            raise ValueError("This is bad")
        except ValueError:
            log.exception(*sys.exc_info())  # type: ignore
        assert mock_print.call_args.args[0].trace.stacks[0].exc_type == "ValueError"
        assert mock_print.call_args.args[0].trace.stacks[0].exc_value == "This is bad"
