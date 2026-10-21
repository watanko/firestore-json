"""The same observable CRUD behavior must hold for both local backends."""

import pytest

from firestore_json import Client, DocumentData
from firestore_json.errors import DocumentAlreadyExistsError, DocumentNotFoundError


def test_missing_and_empty_documents_are_distinct(client: Client, document_path: str) -> None:
    """A must distinguish an absent document from an existing empty object."""
    assert not client.get(document_path).exists
    client.set(document_path, DocumentData({}))
    snapshot = client.get(document_path)
    assert snapshot.exists
    assert snapshot.data == DocumentData({})


def test_create_rejects_duplicates(client: Client, document_path: str) -> None:
    """A must reject duplicate creates without replacing the original data."""
    original = DocumentData({"name": "synthetic", "nested": {"enabled": True}})
    client.create(document_path, original)
    with pytest.raises(DocumentAlreadyExistsError):
        client.create(document_path, DocumentData({"name": "replacement"}))
    assert client.get(document_path).data == original


def test_set_replaces_previous_fields(client: Client, document_path: str) -> None:
    """A must replace fields omitted by a non-merge set operation."""
    client.set(document_path, DocumentData({"old": True, "nested": {"a": "x"}}))
    client.set(document_path, DocumentData({"new": ["日本語", None, False]}))
    assert client.get(document_path).data == DocumentData({"new": ["日本語", None, False]})


def test_merge_preserves_nested_fields(client: Client, document_path: str) -> None:
    """A must merge maps recursively while replacing arrays and empty maps."""
    client.set(
        document_path,
        DocumentData(
            {
                "nested": {"keep": True, "replace": "old"},
                "cleared": {"old": True},
                "array": ["old"],
            }
        ),
    )
    client.set(
        document_path,
        DocumentData(
            {
                "nested": {"replace": "new"},
                "cleared": {},
                "array": ["new"],
            }
        ),
        merge=True,
    )
    assert client.get(document_path).data == DocumentData(
        {
            "nested": {"keep": True, "replace": "new"},
            "cleared": {},
            "array": ["new"],
        }
    )


def test_merge_creates_missing_document(client: Client, document_path: str) -> None:
    """A should create a missing document when merge is requested."""
    data = DocumentData({"created": True})
    client.set(document_path, data, merge=True)
    assert client.get(document_path).data == data


def test_update_replaces_literal_top_level_fields(client: Client, document_path: str) -> None:
    """A must replace nested maps and interpret dotted field names literally."""
    client.set(
        document_path,
        DocumentData(
            {
                "keep": True,
                "nested": {"old": True},
                "literal.dot": "old",
            }
        ),
    )
    client.update(
        document_path,
        DocumentData(
            {
                "nested": {"new": True},
                "literal.dot": "new",
            }
        ),
    )
    assert client.get(document_path).data == DocumentData(
        {
            "keep": True,
            "nested": {"new": True},
            "literal.dot": "new",
        }
    )


def test_update_rejects_missing_document(client: Client, document_path: str) -> None:
    """A must not create a missing document through update."""
    with pytest.raises(DocumentNotFoundError):
        client.update(document_path, DocumentData({"value": True}))
    assert not client.get(document_path).exists


def test_delete_preserves_subcollections(client: Client, document_path: str) -> None:
    """A must preserve child documents when their parent is deleted."""
    child = f"{document_path}/children/one"
    client.set(document_path, DocumentData({"parent": True}))
    client.set(child, DocumentData({"child": True}))
    client.delete(document_path)
    client.delete(document_path)
    assert not client.get(document_path).exists
    assert client.get(child).data == DocumentData({"child": True})
    client.delete(child)


def test_empty_update_is_rejected(client: Client, document_path: str) -> None:
    """A must reject empty updates consistently across backends."""
    with pytest.raises(ValueError, match="empty"):
        client.update(document_path, DocumentData({}))
