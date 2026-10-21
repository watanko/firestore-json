"""Synchronous public CRUD client."""

from typing import Self

import structlog

from firestore_json.clients.factory import build_store
from firestore_json.models import Config, DocumentData, DocumentPath, DocumentSnapshot


class Client:
    """Typed document CRUD with one backend selected at initialization.

    Attributes:
        mode: Selected storage mode for diagnostics.
    """

    def __init__(self, config: Config) -> None:
        """Bind a backend using validated mode-specific configuration."""
        self.mode = config.mode
        self._store = build_store(config)
        self._logger = structlog.get_logger(__name__)

    def get(self, path: str) -> DocumentSnapshot:
        """Read a snapshot preserving the missing/empty distinction."""
        result = self._store.get(DocumentPath(path))
        self._logger.debug("firestore_operation", mode=self.mode, operation="get", operations=1)
        return result

    def create(self, path: str, data: DocumentData) -> None:
        """Create a document, rejecting duplicates."""
        self._store.create(DocumentPath(path), data)
        self._logger.debug("firestore_operation", mode=self.mode, operation="create", operations=1)

    def set(self, path: str, data: DocumentData, *, merge: bool = False) -> None:
        """Create or replace a document, optionally merging nested maps."""
        self._store.set(DocumentPath(path), data, merge=merge)
        self._logger.debug("firestore_operation", mode=self.mode, operation="set", operations=1)

    def update(self, path: str, data: DocumentData) -> None:
        """Replace supplied top-level fields of an existing document."""
        if not data.root:
            raise ValueError("An update cannot be empty")
        self._store.update(DocumentPath(path), data)
        self._logger.debug("firestore_operation", mode=self.mode, operation="update", operations=1)

    def delete(self, path: str) -> None:
        """Delete a document while preserving its subcollections."""
        self._store.delete(DocumentPath(path))
        self._logger.debug("firestore_operation", mode=self.mode, operation="delete", operations=1)

    def close(self) -> None:
        """Release resources owned by the selected backend."""
        self._store.close()

    def __enter__(self) -> Self:
        """Enter a context with deterministic cleanup."""
        return self

    def __exit__(self, *_exc: object) -> None:
        """Close storage without suppressing caller exceptions."""
        self.close()
