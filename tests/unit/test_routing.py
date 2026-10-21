"""Explicit modes prevent SDK environment settings from changing the target."""

from pathlib import Path
from unittest.mock import patch

import pytest

from firestore_json import AsyncClient, Client, EmulatorConfig, GcloudConfig, JsonConfig
from firestore_json.clients.factory import validate_google_mode
from firestore_json.errors import ConfigurationError


def test_cloud_passes_explicit_target_to_official_sdk(monkeypatch: pytest.MonkeyPatch) -> None:
    """A must preserve project and database without requiring live cloud access."""
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    with patch("firestore_json.backends.google.GoogleClient", autospec=True) as sdk:
        with Client(GcloudConfig(project="synthetic-test", database="named-database")) as client:
            client.delete("synthetic/document")
        sdk.assert_called_once_with(project="synthetic-test", database="named-database")
        sdk.return_value.document.assert_called_once_with("synthetic/document")
        sdk.return_value.document.return_value.delete.assert_called_once_with()
        sdk.return_value.close.assert_called_once_with()


def test_cloud_rejects_emulator_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """A must reject cloud mode before credential lookup when an emulator is selected."""
    monkeypatch.setenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
    with pytest.raises(ConfigurationError, match="unset"):
        Client(GcloudConfig(project="synthetic-test"))
    with pytest.raises(ConfigurationError, match="unset"):
        AsyncClient(GcloudConfig(project="synthetic-test"))


def test_emulator_requires_matching_host(monkeypatch: pytest.MonkeyPatch) -> None:
    """A must reject emulator mode when the official SDK would use a different host."""
    monkeypatch.delenv("FIRESTORE_EMULATOR_HOST", raising=False)
    with pytest.raises(ConfigurationError, match="match"):
        validate_google_mode(EmulatorConfig(project="demo-test", host="localhost:8080"))
    monkeypatch.setenv("FIRESTORE_EMULATOR_HOST", "localhost:9000")
    with pytest.raises(ConfigurationError, match="match"):
        validate_google_mode(EmulatorConfig(project="demo-test", host="localhost:8080"))


def test_json_ignores_google_environment(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A must leave process-global SDK settings unchanged in JSON mode."""
    monkeypatch.setenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
    with Client(JsonConfig(directory=tmp_path)) as client:
        assert client.mode == "json"
    import os

    assert os.environ["FIRESTORE_EMULATOR_HOST"] == "localhost:8080"
