"""Official synchronous SDK adapter for cloud and official-emulator modes."""

from google.api_core.exceptions import AlreadyExists, NotFound
from google.cloud.firestore_v1 import Client as GoogleClient
from google.cloud.firestore_v1.field_path import FieldPath

from firestore_json.errors import DocumentAlreadyExistsError, DocumentNotFoundError
from firestore_json.models import (
    DocumentData,
    DocumentPath,
    DocumentSnapshot,
    EmulatorConfig,
    GcloudConfig,
)


class GoogleStore:
    """Use the official SDK and its built-in retry policy."""

    def __init__(self, config: GcloudConfig | EmulatorConfig) -> None:
        """Bind explicit project and database after routing validation."""
        self._client = GoogleClient(project=config.project, database=config.database)

    def get(self, path: DocumentPath) -> DocumentSnapshot:
        """Validate SDK output before returning a shared snapshot."""
        snapshot = self._client.document(path.root).get()
        payload: object = snapshot.to_dict()
        data = DocumentData.model_validate(payload) if snapshot.exists else None
        return DocumentSnapshot(path=path, data=data)

    def create(self, path: DocumentPath, data: DocumentData) -> None:
        """Translate duplicate creation to the common storage exception."""
        try:
            self._client.document(path.root).create(data.root)
        except AlreadyExists:
            raise DocumentAlreadyExistsError("Document already exists") from None

    def set(self, path: DocumentPath, data: DocumentData, *, merge: bool) -> None:
        """Delegate replacement and recursive map merge to the official SDK."""
        self._client.document(path.root).set(data.root, merge=merge)

    def update(self, path: DocumentPath, data: DocumentData) -> None:
        """Replace literal top-level fields, rejecting absent documents."""
        updates = {FieldPath(key).to_api_repr(): value for key, value in data.root.items()}
        try:
            self._client.document(path.root).update(updates)
        except NotFound:
            raise DocumentNotFoundError("Document does not exist") from None

    def delete(self, path: DocumentPath) -> None:
        """Delete a document without deleting its subcollections."""
        self._client.document(path.root).delete()

    def close(self) -> None:
        """Release resources owned by the official SDK."""
        self._client.close()
