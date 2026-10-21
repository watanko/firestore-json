"""Payload and configuration boundaries reject invalid values."""

from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from firestore_json import DocumentData, EmulatorConfig, GcloudConfig, JsonConfig
from firestore_json.models import DocumentPath


@pytest.mark.parametrize(
    "path",
    ["", "collection", "/a/b", "a/b/", "a/../b/c", "a/./b/c", "a/xx\\yy", "a/xx\x00yy"],
)
def test_invalid_paths(path: str) -> None:
    """A must reject paths before any filesystem or network operation."""
    with pytest.raises(ValidationError):
        DocumentPath(path)


@pytest.mark.parametrize("value", [float("nan"), float("inf"), datetime.now(UTC), b"bytes"])
def test_unsupported_values(value: object) -> None:
    """A must reject values outside the documented finite JSON subset."""
    with pytest.raises(ValidationError):
        DocumentData.model_validate({"value": value})


def test_modes_reject_inapplicable_settings() -> None:
    """A must reject mode-specific parameters that belong to another backend."""
    with pytest.raises(ValidationError):
        JsonConfig.model_validate({"directory": "/tmp/example", "project": "unused"})
    with pytest.raises(ValidationError):
        GcloudConfig(project="")
    with pytest.raises(ValidationError):
        EmulatorConfig(project="demo-test", host="https://localhost:8080")
