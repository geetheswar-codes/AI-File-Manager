"""
AI File Management Platform v2.0

Duplicate File Detection Service

Purpose:
    Identify files with identical content using SHA-256 hashes.

Important Principles:
    - Read only
    - Never modify or delete user files
    - Duplicate detection is based on content, not filename
    - Files with the same SHA-256 hash are considered duplicates
"""

from collections import defaultdict
from typing import Any, Dict, List


class DuplicateFileDetector:
    """
    Detect duplicate files from indexed file metadata.
    """

    @staticmethod
    def find_duplicates(
        files: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Group files that have identical content hashes.

        Args:
            files: File records containing at least:
                - path
                - content_hash

        Returns:
            A list of duplicate groups.

        Files without a content_hash are ignored.
        Groups containing only one file are not returned.
        """

        hash_groups = defaultdict(list)

        for file in files:
            content_hash = file.get("content_hash")
            path = file.get("path")

            if not content_hash or not path:
                continue

            hash_groups[content_hash].append(path)

        duplicates = []

        for content_hash, paths in hash_groups.items():
            if len(paths) > 1:
                duplicates.append(
                    {
                        "content_hash": content_hash,
                        "files": paths,
                        "count": len(paths),
                    }
                )

        return duplicates
