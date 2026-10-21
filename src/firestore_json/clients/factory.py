"""Explicit routing without mutating global SDK environment variables."""

import os
from importlib.util import find_spec

from firestore_json.backends.contracts import AsyncStore, Store
from firestore_json.backends.json import JsonStore
from firestore_json.errors import ConfigurationError
from firestore_json.models import Config, EmulatorConfig, GcloudConfig, JsonConfig


def validate_google_mode(config: GcloudConfig | EmulatorConfig) -> None:
    """Reject ambiguous routing before credentials or transport initialization.

    Args:
        config: Cloud or official-emulator connection settings.

    Raises:
        ConfigurationError: If settings conflict or the Google extra is absent.
    """
    host = os.environ.get("FIRESTORE_EMULATOR_HOST")
    if isinstance(config, GcloudConfig) and host is not None:
        raise ConfigurationError("gcloud mode requires FIRESTORE_EMULATOR_HOST to be unset")
    if isinstance(config, EmulatorConfig) and host != config.host:
        raise ConfigurationError("emulator mode requires FIRESTORE_EMULATOR_HOST to match host")
    if find_spec("google") is None or find_spec("google.cloud") is None:
        raise ConfigurationError("Install firestore-json[google] to use this mode")
    if find_spec("google.cloud.firestore_v1") is None:
        raise ConfigurationError("Install firestore-json[google] to use this mode")


def build_store(config: Config) -> Store:
    """Construct the synchronous backend selected by mode."""
    if isinstance(config, JsonConfig):
        return JsonStore(config)
    validate_google_mode(config)
    from firestore_json.backends.google import GoogleStore

    return GoogleStore(config)


def build_async_store(config: Config) -> AsyncStore:
    """Construct the asynchronous backend selected by mode."""
    if isinstance(config, JsonConfig):
        from firestore_json.backends.async_json import AsyncJsonStore

        return AsyncJsonStore(config)
    validate_google_mode(config)
    from firestore_json.backends.async_google import AsyncGoogleStore

    return AsyncGoogleStore(config)
