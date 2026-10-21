"""Atomic JSON storage with interprocess read-modify-write serialization."""

import os
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from filelock import FileLock
from pydantic import JsonValue, ValidationError

from firestore_json.errors import (
    CorruptDocumentError,
    DocumentAlreadyExistsError,
    DocumentNotFoundError,
)
from firestore_json.models import (
    DocumentData,
    DocumentPath,
    DocumentSnapshot,
    JsonConfig,
)


def merge_maps(
    previous: dict[str, JsonValue], incoming: dict[str, JsonValue]
) -> dict[str, JsonValue]:
    """Merge nested maps while allowing explicit empty maps to replace values.

    Args:
        previous: Existing document fields.
        incoming: Fields supplied by a merge write.

    Returns:
        Merged fields without mutating the inputs.
    """
    result = previous.copy()
    for key, value in incoming.items():
        old = result.get(key)
        if isinstance(old, dict) and isinstance(value, dict) and value:
            result[key] = merge_maps(old, value)
        else:
            result[key] = value
    return result


class JsonStore:
    """Persist each document separately under one process-shared lock.

    Attributes:
        root: Resolved storage directory.
    """

    def __init__(self, config: JsonConfig) -> None:
        """Bind a directory and a lock shared by every instance using it.

        Args:
            config: Validated file storage settings.
        """
        self.root = config.directory.resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = FileLock(self.root / ".firestore-json.lock", timeout=10)

    def _file(self, path: DocumentPath) -> Path:
        """Escape IDs and reject paths resolving outside the storage root.

        Args:
            path: Validated logical document path.

        Returns:
            Checked filesystem document path.

        Raises:
            ValueError: If a symlink would escape the storage directory.
        """
        parts = [quote(part, safe="") for part in path.root.split("/")]
        target = self.root.joinpath(*parts).with_name(f"{parts[-1]}.json")
        if not target.resolve().is_relative_to(self.root):
            raise ValueError("Document path escapes its storage root")
        return target

    def _read(self, target: Path) -> DocumentData | None:
        """Preserve the distinction between absent and invalid stored data.

        Args:
            target: Checked document file.

        Returns:
            Validated data, or None for an absent file.

        Raises:
            CorruptDocumentError: If JSON is malformed or violates the schema.
            OSError: If reading the filesystem fails.
        """
        if not target.exists():
            return None
        try:
            return DocumentData.model_validate_json(target.read_bytes())
        except ValidationError:
            raise CorruptDocumentError("Stored document must be a valid JSON object") from None

    def _write(self, target: Path, data: DocumentData) -> None:
        """Replace a document after flushing its complete payload.

        Args:
            target: Checked destination.
            data: Validated replacement payload.

        Raises:
            OSError: If persistence fails; errors are never swallowed.
        """
        target.parent.mkdir(parents=True, exist_ok=True)
        with TemporaryDirectory(prefix=".write-", dir=target.parent) as staging:
            temporary = Path(staging) / "document.json"
            with temporary.open("w", encoding="utf-8") as stream:
                stream.write(data.model_dump_json(indent=2) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)

    def get(self, path: DocumentPath) -> DocumentSnapshot:
        """Read a snapshot under the process-shared lock."""
        with self._lock:
            return DocumentSnapshot(path=path, data=self._read(self._file(path)))

    def create(self, path: DocumentPath, data: DocumentData) -> None:
        """Create a document or raise DocumentAlreadyExistsError."""
        with self._lock:
            target = self._file(path)
            if target.exists():
                raise DocumentAlreadyExistsError("Document already exists")
            self._write(target, data)

    def set(self, path: DocumentPath, data: DocumentData, *, merge: bool) -> None:
        """Create or replace data, optionally merging nested maps."""
        with self._lock:
            target = self._file(path)
            if merge:
                previous = self._read(target)
                if previous is not None:
                    data = DocumentData(merge_maps(previous.root, data.root))
            self._write(target, data)

    def update(self, path: DocumentPath, data: DocumentData) -> None:
        """Replace supplied top-level fields or raise DocumentNotFoundError."""
        with self._lock:
            target = self._file(path)
            previous = self._read(target)
            if previous is None:
                raise DocumentNotFoundError("Document does not exist")
            self._write(target, DocumentData(previous.root | data.root))

    def delete(self, path: DocumentPath) -> None:
        """Delete one document, preserving subcollection files."""
        with self._lock:
            self._file(path).unlink(missing_ok=True)

    def close(self) -> None:
        """Finish without retaining open file descriptors."""
