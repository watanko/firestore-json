"""Exceptions shared by all storage implementations."""


class ConfigurationError(ValueError):
    """Mode settings conflict with the SDK environment."""


class DocumentAlreadyExistsError(FileExistsError):
    """A create operation targets an existing document."""


class DocumentNotFoundError(FileNotFoundError):
    """An update operation targets a missing document."""


class CorruptDocumentError(ValueError):
    """Persisted data violates the document schema."""
