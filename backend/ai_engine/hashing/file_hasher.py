"""
AI File Management Platform v2.0

File Hashing Service

Purpose:
    Calculate cryptographic hashes for files so the AI engine
    can identify files with identical contents.

Important Principles:
    - Read only
    - Never modify user files
    - Stream large files instead of loading them completely
"""

import hashlib
from pathlib import Path


class FileHasher:
    """
    Calculate SHA-256 hashes for files.

    Files are read in chunks to avoid excessive memory usage.
    """

    CHUNK_SIZE = 1024 * 1024  # 1 MB

    @classmethod
    def sha256(cls, file_path: str) -> str:
        """
        Calculate the SHA-256 hash of a file.

        Args:
            file_path: Path to the file.

        Returns:
            Lowercase hexadecimal SHA-256 digest.

        Raises:
            FileNotFoundError: If the file does not exist.
            IsADirectoryError: If the path is a directory.
            PermissionError: If the file cannot be read.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(str(path))

        if not path.is_file():
            raise IsADirectoryError(str(path))

        digest = hashlib.sha256()

        with path.open("rb") as file:
            while True:
                chunk = file.read(cls.CHUNK_SIZE)

                if not chunk:
                    break

                digest.update(chunk)

        return digest.hexdigest()
