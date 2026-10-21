"""Shared contract fixtures for JSON and the official emulator."""

import os
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest

from firestore_json import Client, EmulatorConfig, JsonConfig
from firestore_json.models import Config


@pytest.fixture
def config(tmp_path: Path) -> Config:
    """Bind local files or an explicitly selected official emulator."""
    if os.environ.get("FIRESTORE_JSON_TEST_BACKEND", "json") == "emulator":
        return EmulatorConfig(
            project="demo-firestore-json", host=os.environ["FIRESTORE_EMULATOR_HOST"]
        )
    return JsonConfig(directory=tmp_path)


@pytest.fixture
def client(config: Config) -> Iterator[Client]:
    """Close the selected backend after each contract test."""
    with Client(config) as instance:
        yield instance


@pytest.fixture
def document_path() -> str:
    """Isolate contract tests inside unique synthetic document identities."""
    return f"contract_tests/{uuid4().hex}"
