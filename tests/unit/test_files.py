"""File persistence must survive concurrency and reject corrupted data."""

from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from unittest.mock import patch

import pytest

from firestore_json import Client, DocumentData, JsonConfig
from firestore_json.errors import CorruptDocumentError, DocumentAlreadyExistsError


def create_competing_document(directory: Path) -> bool:
    """Attempt a competing create from a separate process.

    Args:
        directory: Shared root used by every competing writer.

    Returns:
        Whether this process created the document.
    """
    with Client(JsonConfig(directory=directory)) as client:
        try:
            client.create("race/document", DocumentData({"created": True}))
        except DocumentAlreadyExistsError:
            return False
    return True


def test_create_is_atomic_across_processes(tmp_path: Path) -> None:
    """A must permit exactly one successful create among competing processes."""
    with ProcessPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(create_competing_document, [tmp_path] * 8))
    assert sum(results) == 1


def test_data_survives_client_restart(tmp_path: Path) -> None:
    """A must read committed data from a newly constructed client."""
    config = JsonConfig(directory=tmp_path)
    with Client(config) as first:
        first.set("settings/current", DocumentData({"enabled": True}))
    with Client(config) as second:
        assert second.get("settings/current").data == DocumentData({"enabled": True})


@pytest.mark.parametrize("payload", ["{invalid", "[]", '{"value": NaN}'])
def test_corruption_is_not_missing_data(tmp_path: Path, payload: str) -> None:
    """A must report invalid stored data without overwriting it."""
    file = tmp_path / "settings" / "current.json"
    file.parent.mkdir()
    file.write_text(payload)
    with Client(JsonConfig(directory=tmp_path)) as client, pytest.raises(CorruptDocumentError):
        client.get("settings/current")
    assert file.read_text() == payload


def test_failed_replace_preserves_previous_data(tmp_path: Path) -> None:
    """A must retain the previous document if atomic replacement fails."""
    with Client(JsonConfig(directory=tmp_path)) as client:
        client.set("settings/current", DocumentData({"old": True}))
        with (
            patch("firestore_json.backends.json.os.replace", side_effect=OSError("disk error")),
            pytest.raises(OSError, match="disk error"),
        ):
            client.set("settings/current", DocumentData({"new": True}))
        assert client.get("settings/current").data == DocumentData({"old": True})
    assert not list(tmp_path.rglob(".write-*"))


def test_symlink_escape_is_rejected(tmp_path: Path) -> None:
    """A must reject symlinks pointing outside the configured directory."""
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / "settings").symlink_to(outside, target_is_directory=True)
    with (
        Client(JsonConfig(directory=root)) as client,
        pytest.raises(ValueError, match="escapes"),
    ):
        client.set("settings/current", DocumentData({"value": True}))
    assert list(outside.iterdir()) == []
