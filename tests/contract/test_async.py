"""Asynchronous clients share the same persistence contract."""

import pytest

from firestore_json import AsyncClient, DocumentData
from firestore_json.errors import DocumentAlreadyExistsError, DocumentNotFoundError
from firestore_json.models import Config


@pytest.mark.asyncio
async def test_async_crud(config: Config, document_path: str) -> None:
    """A should support the complete CRUD lifecycle inside an existing loop."""
    async with AsyncClient(config) as client:
        assert not (await client.get(document_path)).exists
        await client.create(document_path, DocumentData({"nested": {"keep": True}}))
        with pytest.raises(DocumentAlreadyExistsError):
            await client.create(document_path, DocumentData({}))
        await client.set(document_path, DocumentData({"nested": {"new": True}}), merge=True)
        assert (await client.get(document_path)).data == DocumentData(
            {
                "nested": {"keep": True, "new": True},
            }
        )
        await client.update(document_path, DocumentData({"nested": {}}))
        assert (await client.get(document_path)).data == DocumentData({"nested": {}})
        await client.delete(document_path)
        await client.delete(document_path)
        with pytest.raises(DocumentNotFoundError):
            await client.update(document_path, DocumentData({"value": True}))
        with pytest.raises(ValueError, match="empty"):
            await client.update(document_path, DocumentData({}))
