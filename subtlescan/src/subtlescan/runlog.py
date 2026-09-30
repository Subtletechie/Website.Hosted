"""Logging: human-readable to the console via rich, structured JSON lines to the run folder."""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from rich.console import Console
from rich.logging import RichHandler

console = Console(stderr=True)
log = logging.getLogger("subtlescan")

_RESERVED = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime"}


class JsonLinesHandler(logging.Handler):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self._fh = path.open("a", encoding="utf-8")

    def emit(self, record: logging.LogRecord) -> None:
        entry = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname.lower(),
            "logger": record.name,
            "msg": record.getMessage(),
        }
        entry.update({k: v for k, v in record.__dict__.items() if k not in _RESERVED})
        self._fh.write(json.dumps(entry, default=str) + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()
        super().close()


def setup_console(verbose: bool = False) -> None:
    if any(isinstance(h, RichHandler) for h in log.handlers):
        return
    handler = RichHandler(console=console, show_path=False, markup=False)
    log.addHandler(handler)
    log.setLevel(logging.DEBUG if verbose else logging.INFO)
    # Azure SDK logs every HTTP call at INFO; keep the console readable.
    logging.getLogger("azure").setLevel(logging.WARNING)


def attach_run_log(run_dir: Path) -> JsonLinesHandler:
    handler = JsonLinesHandler(run_dir / "log.jsonl")
    handler.setLevel(logging.DEBUG)
    log.addHandler(handler)
    return handler
