"""Storage behavior independent of concrete persistence engines."""

from typing import Protocol

from firestore_json.models import DocumentData, DocumentPath, DocumentSnapshot


class Store(Protocol):
    """Synchronous document persistence contract."""

    def get(self, path: DocumentPath) -> DocumentSnapshot:
        """Read a snapshot preserving the missing/empty distinction."""
        ...

    def create(self, path: DocumentPath, data: DocumentData) -> None:
        """Create a document, rejecting duplicates."""
        ...

    def set(self, path: DocumentPath, data: DocumentData, *, merge: bool) -> None:
        """Create or replace a document, optionally merging nested maps."""
        ...

    def update(self, path: DocumentPath, data: DocumentData) -> None:
        """Replace supplied top-level fields of an existing document."""
        ...

    def delete(self, path: DocumentPath) -> None:
        """Delete a document while preserving its subcollections."""
        ...

    def close(self) -> None:
        """Release owned resources."""
        ...


class AsyncStore(Protocol):
    """Asynchronous document persistence contract."""

    async def get(self, path: DocumentPath) -> DocumentSnapshot:
        """Read a snapshot preserving the missing/empty distinction."""
        ...

    async def create(self, path: DocumentPath, data: DocumentData) -> None:
        """Create a document, rejecting duplicates."""
        ...

    async def set(self, path: DocumentPath, data: DocumentData, *, merge: bool) -> None:
        """Create or replace a document, optionally merging nested maps."""
        ...

    async def update(self, path: DocumentPath, data: DocumentData) -> None:
        """Replace supplied top-level fields of an existing document."""
        ...

    async def delete(self, path: DocumentPath) -> None:
        """Delete a document while preserving its subcollections."""
        ...

    async def close(self) -> None:
        """Release owned resources."""
        ...
