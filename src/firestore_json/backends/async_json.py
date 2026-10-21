"""Thread-backed asynchronous access to the shared JSON engine."""

from asyncio import to_thread

from firestore_json.backends.json import JsonStore
from firestore_json.models import (
    DocumentData,
    DocumentPath,
    DocumentSnapshot,
    JsonConfig,
)


class AsyncJsonStore:
    """Offload file operations without blocking the caller's event loop."""

    def __init__(self, config: JsonConfig) -> None:
        """Bind a synchronous engine whose lock covers worker threads."""
        self._store = JsonStore(config)

    async def get(self, path: DocumentPath) -> DocumentSnapshot:
        """Read a snapshot preserving the missing/empty distinction."""
        return await to_thread(self._store.get, path)

    async def create(self, path: DocumentPath, data: DocumentData) -> None:
        """Create a document, rejecting duplicates."""
        await to_thread(self._store.create, path, data)

    async def set(self, path: DocumentPath, data: DocumentData, *, merge: bool) -> None:
        """Create or replace a document, optionally merging nested maps."""
        await to_thread(self._store.set, path, data, merge=merge)

    async def update(self, path: DocumentPath, data: DocumentData) -> None:
        """Replace supplied top-level fields of an existing document."""
        await to_thread(self._store.update, path, data)

    async def delete(self, path: DocumentPath) -> None:
        """Delete a document while preserving its subcollections."""
        await to_thread(self._store.delete, path)

    async def close(self) -> None:
        """Finish without retaining open file descriptors."""
        await to_thread(self._store.close)
