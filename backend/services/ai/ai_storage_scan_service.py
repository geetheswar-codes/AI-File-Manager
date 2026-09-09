from typing import Any, Dict

from sqlalchemy.orm import Session

from backend.ai_engine.coordinator.ai_scan_coordinator import (
    AIScanCoordinator,
)
from backend.services.storage.storage_access_service import (
    StorageAccessService,
)


class AIStorageScanService:
    """
    Connect authorized storage locations to the AI scanning pipeline.

    This service:
        1. Validates the requested storage location.
        2. Passes the validated directory to the AI coordinator.
        3. Returns the complete scan and analysis result.

    It does not modify user files.
    """

    def __init__(
        self,
        db: Session,
        allowed_roots: list[str],
    ):
        self.storage_access = StorageAccessService(
            allowed_roots=allowed_roots
        )
        self.coordinator = AIScanCoordinator(db)

    def scan(
        self,
        root_path: str,
    ) -> Dict[str, Any]:
        """
        Scan an authorized storage directory with the AI pipeline.
        """

        validated_root = (
            self.storage_access.validate_directory(root_path)
        )

        return self.coordinator.scan_and_analyze(
            root_path=str(validated_root)
        )
