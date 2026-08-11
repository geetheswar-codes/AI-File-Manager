"""
AI File Management Platform v2.0

AI File Index Service

Purpose:
    Maintain a lightweight persistent index of files discovered
    by the SystemScanner.

Important Principles:
    - Never modify user files
    - Use cheap metadata for change detection
    - Avoid unnecessary deep analysis
    - Support incremental scanning
    - Keep database operations isolated from scanner logic
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from backend.models.ai_file_index import AIFileIndex


class AIFileIndexService:
    """
    Manage the persistent AI file index.

    The service compares scanner metadata with previously indexed
    metadata and determines whether a file is new, changed, or
    unchanged.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_by_path(self, path: str) -> Optional[AIFileIndex]:
        """
        Retrieve an indexed file by its full path.
        """

        return (
            self.db.query(AIFileIndex)
            .filter(AIFileIndex.path == path)
            .first()
        )

    def is_new_file(self, metadata: Dict[str, Any]) -> bool:
        """
        Determine whether a file has never been indexed.
        """

        path = metadata.get("path")

        if not path:
            return False

        return self.get_by_path(path) is None

    def has_changed(
        self,
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Determine whether indexed file metadata has changed.

        Change detection currently uses:
            - File size
            - Modified time
            - File type

        These checks are intentionally inexpensive.
        """

        path = metadata.get("path")

        if not path:
            return False

        indexed_file = self.get_by_path(path)

        if indexed_file is None:
            return True

        return (
            indexed_file.file_size != metadata.get("size")
            or indexed_file.modified_time
            != metadata.get("modified_time")
            or indexed_file.file_type
            != metadata.get("extension")
        )

    def needs_analysis(
        self,
        metadata: Dict[str, Any],
    ) -> bool:
        """
        Determine whether a file requires AI analysis.

        Returns True for:
            - New files
            - Changed files

        Returns False for unchanged files.
        """

        if self.is_new_file(metadata):
            return True

        return self.has_changed(metadata)

    def update_index(
        self,
        metadata: Dict[str, Any],
    ) -> AIFileIndex:
        """
        Insert or update a file's lightweight index record.

        This method modifies only the AI database index.
        It never modifies the actual user file.
        """

        path = metadata.get("path")

        if not path:
            raise ValueError("File metadata must contain a path.")

        indexed_file = self.get_by_path(path)

        if indexed_file is None:
            indexed_file = AIFileIndex(
                path=path,
                file_size=metadata.get("size"),
                modified_time=metadata.get("modified_time"),
                file_type=metadata.get("extension"),
                last_scanned_at=datetime.utcnow(),
            )

            self.db.add(indexed_file)

        else:
            indexed_file.file_size = metadata.get("size")
            indexed_file.modified_time = metadata.get(
                "modified_time"
            )
            indexed_file.file_type = metadata.get("extension")
            indexed_file.last_scanned_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(indexed_file)

        return indexed_file

    def filter_changed_files(
        self,
        files: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Return only files that require analysis.

        New and changed files are included.
        Unchanged files are skipped.
        """

        changed_files = []

        for metadata in files:
            try:
                if self.needs_analysis(metadata):
                    changed_files.append(metadata)

            except (TypeError, AttributeError):
                continue

        return changed_files

    def update_index_batch(
        self,
        files: List[Dict[str, Any]],
    ) -> int:
        """
        Update the index for multiple files.

        Returns:
            Number of successfully indexed files.
        """

        updated_count = 0

        for metadata in files:
            try:
                self.update_index(metadata)
                updated_count += 1

            except (TypeError, ValueError):
                continue

        return updated_count