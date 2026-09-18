"""Atomic JSON persistence for D2R measurement evidence."""

import json
import os
from pathlib import Path
import tempfile


class JsonExperimentStorage:
    """Persist one JSON-compatible experiment record at a caller-selected path."""

    def __init__(self, path: Path):
        self._path = Path(path)

    def save(self, record: dict) -> None:
        if not isinstance(record, dict):
            raise ValueError("record must be a dictionary")
        self._path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self._path.parent, prefix=f".{self._path.name}.", delete=False
            ) as temporary:
                temporary_path = Path(temporary.name)
                json.dump(record, temporary, ensure_ascii=False, indent=2, allow_nan=False)
                temporary.write("\n")
            os.replace(temporary_path, self._path)
            temporary_path = None
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def load(self) -> dict:
        with self._path.open(encoding="utf-8") as source:
            record = json.load(source)
        if not isinstance(record, dict):
            raise ValueError("stored record must be a JSON object")
        return record
