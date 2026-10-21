"""Validated configuration, JSON payloads, and document identities."""

from math import isfinite
from pathlib import Path
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, Field, JsonValue, RootModel


class GcloudConfig(BaseModel, extra="forbid", frozen=True):
    """Google Cloud connection using Application Default Credentials.

    Attributes:
        mode: Cloud mode discriminator.
        project: Explicit Google Cloud project.
        database: Target Firestore database.
    """

    mode: Literal["gcloud"] = "gcloud"
    project: str = Field(min_length=1)
    database: str = Field(default="(default)", min_length=1)


class EmulatorConfig(BaseModel, extra="forbid", frozen=True):
    """Connection to a running official Firestore emulator.

    Attributes:
        mode: Official emulator discriminator.
        project: Local project namespace.
        database: Target database.
        host: Host and port matching FIRESTORE_EMULATOR_HOST.
    """

    mode: Literal["emulator"] = "emulator"
    project: str = Field(min_length=1)
    host: str = Field(pattern=r"^[^/\s]+:[0-9]+$")
    database: str = Field(default="(default)", min_length=1)


class JsonConfig(BaseModel, extra="forbid", frozen=True):
    """Local storage configuration.

    Attributes:
        mode: File storage discriminator.
        directory: Dedicated directory for JSON files.
    """

    mode: Literal["json"] = "json"
    directory: Path


type Config = GcloudConfig | EmulatorConfig | JsonConfig


def validate_finite_numbers(value: JsonValue) -> None:
    """Reject non-finite numbers consistently after JSON and Python decoding.

    Args:
        value: Validated JSON-shaped value to inspect recursively.

    Raises:
        ValueError: If any nested numeric value is NaN or infinite.
    """
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("Document numbers must be finite")
    if isinstance(value, dict):
        for item in value.values():
            validate_finite_numbers(item)
    if isinstance(value, list):
        for item in value:
            validate_finite_numbers(item)


def validate_document_fields(value: dict[str, JsonValue]) -> dict[str, JsonValue]:
    """Apply identical numeric constraints after Python and JSON decoding.

    Args:
        value: Decoded document fields.

    Returns:
        Validated fields.

    Raises:
        ValueError: If a nested number is non-finite.
    """
    validate_finite_numbers(value)
    return value


def validate_document_path(value: str) -> str:
    """Reject ambiguous paths before storage access.

    Args:
        value: Caller-supplied document path.

    Returns:
        Validated relative path.

    Raises:
        ValueError: If a path is incomplete or contains unsafe segments.
    """
    parts = value.split("/")
    if len(parts) % 2:
        raise ValueError("A document path must alternate collection and document IDs")
    if any(part in {"", ".", ".."} or "\\" in part or "\x00" in part for part in parts):
        raise ValueError("Invalid document path segment")
    return value


class DocumentData(
    RootModel[Annotated[dict[str, JsonValue], AfterValidator(validate_document_fields)]],
    strict=True,
    allow_inf_nan=False,
):
    """A document restricted to finite JSON-native values.

    Attributes:
        root: String-keyed data; SDK sentinels and datetimes are unsupported.
    """


class DocumentPath(RootModel[Annotated[str, AfterValidator(validate_document_path)]]):
    """An alternating collection/document path.

    Attributes:
        root: Validated relative document identity.
    """


class DocumentSnapshot(BaseModel, extra="forbid", frozen=True):
    """A read result distinguishing an absent document from an empty object.

    Attributes:
        path: Canonical document identity.
        data: Validated data, or None only for a missing document.
    """

    path: DocumentPath
    data: DocumentData | None

    @property
    def exists(self) -> bool:
        """Return whether this snapshot describes an existing document."""
        return self.data is not None
