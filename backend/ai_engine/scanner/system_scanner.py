"""
AI File Management Platform v2.0

System Scanner Module

Purpose:
    The SystemScanner is responsible for scanning user-authorized
    directories and collecting metadata about files and folders.

Important Principles:
    - Read Only (Never modify user files)
    - Privacy First (Scan only user-authorized locations)
    - Security First (Handle permission errors safely)
    - AI First (Provide metadata for AI analysis)

Future AI Features Supported:
    - Natural Language Search
    - Duplicate Detection
    - Storage Analysis
    - Smart Organization
    - Recommendation Engine
    - System Health Monitoring
"""

import mimetypes
import os
import stat
import time
from pathlib import Path


class SystemScanner:
    """
    AI System Scanner

    Responsibilities:
        - Scan authorized directories
        - Discover files and folders
        - Collect metadata
        - Skip inaccessible locations safely
        - Return structured information
    """

    def __init__(self):
        """Initialize scanner state."""

        self.files = []
        self.folders = []
        self.errors = []
        self.start_time = None
        self.end_time = None

    def scan(self, root_path: str):
        """
        Entry point for scanning.

        Args:
            root_path: User-authorized directory to scan.

        Returns:
            Dictionary containing scanned files, folders,
            errors, and summary.
        """

        self.files = []
        self.folders = []
        self.errors = []
        self.start_time = time.time()
        self.end_time = None

        root = Path(root_path).expanduser()

        if not root.exists():
            self.errors.append({
                "path": str(root),
                "error": "Path does not exist"
            })

            self.end_time = time.time()

            return {
                "files": [],
                "folders": [],
                "errors": self.errors,
                "summary": self.get_summary()
            }

        if not root.is_dir():
            self.errors.append({
                "path": str(root),
                "error": "Path is not a directory"
            })

            self.end_time = time.time()

            return {
                "files": [],
                "folders": [],
                "errors": self.errors,
                "summary": self.get_summary()
            }

        try:
            self.scan_directory(str(root))

        except PermissionError:
            self.errors.append({
                "path": str(root),
                "error": "Permission denied"
            })

        except OSError as exc:
            self.errors.append({
                "path": str(root),
                "error": str(exc)
            })

        self.end_time = time.time()

        return {
            "files": self.files,
            "folders": self.folders,
            "errors": self.errors,
            "summary": self.get_summary()
        }

    def scan_directory(self, directory_path: str):
        """
        Scan a directory recursively.

        Responsibilities:
            - Traverse folders
            - Discover files
            - Call scan_file()
        """

        directory = Path(directory_path)

        try:
            with os.scandir(directory) as entries:
                for entry in entries:

                    entry_path = Path(entry.path)

                    if self.should_skip(entry_path):
                        continue

                    try:
                        if entry.is_dir(follow_symlinks=False):
                            self.folders.append({
                                "name": entry.name,
                                "path": str(entry_path)
                            })

                            self.scan_directory(str(entry_path))

                        elif entry.is_file(follow_symlinks=False):
                            metadata = self.scan_file(str(entry_path))

                            if metadata:
                                self.files.append(metadata)

                    except PermissionError:
                        self.errors.append({
                            "path": str(entry_path),
                            "error": "Permission denied"
                        })

                    except OSError as exc:
                        self.errors.append({
                            "path": str(entry_path),
                            "error": str(exc)
                        })

        except PermissionError:
            self.errors.append({
                "path": str(directory),
                "error": "Permission denied"
            })

        except OSError as exc:
            self.errors.append({
                "path": str(directory),
                "error": str(exc)
            })

    def scan_file(self, file_path: str):
        """
        Scan a single file.

        Responsibilities:
            - Read file information
            - Call collect_metadata()
        """

        try:
            return self.collect_metadata(file_path)

        except PermissionError:
            self.errors.append({
                "path": str(file_path),
                "error": "Permission denied"
            })

        except OSError as exc:
            self.errors.append({
                "path": str(file_path),
                "error": str(exc)
            })

        return None

    def collect_metadata(self, file_path: str):
        """
        Collect metadata from a file.

        Current Metadata:
            - Name
            - Full Path
            - Extension
            - Size
            - Created Time
            - Modified Time
            - Accessed Time
            - Hidden Status
            - MIME Type

        Future Metadata:
            - SHA-256 Hash
            - Duplicate ID
            - AI Tags
            - Risk Score
            - File Category
        """

        path = Path(file_path)

        file_stat = path.stat()

        extension = path.suffix.lower()

        mime_type, _ = mimetypes.guess_type(str(path))

        return {
            "name": path.name,
            "path": str(path.resolve()),
            "extension": extension,
            "size": file_stat.st_size,
            "created_time": file_stat.st_ctime,
            "modified_time": file_stat.st_mtime,
            "accessed_time": file_stat.st_atime,
            "hidden": self._is_hidden(path),
            "mime_type": mime_type or "application/octet-stream"
        }

    def should_skip(self, path: str) -> bool:
        """
        Determine whether a file or folder should be skipped.

        Current rules:
            - Broken symbolic links
            - Symbolic links
            - Inaccessible paths

        Hidden files are NOT skipped by default because the AI
        platform may need to understand the complete authorized
        file system.
        """

        path = Path(path)

        try:
            if path.is_symlink():
                return True

            if not os.access(path, os.R_OK):
                return True

        except OSError:
            return True

        return False

    def get_summary(self):
        """
        Return scan summary.

        Returns:
            Dictionary containing scan statistics.
        """

        if self.start_time is None:
            scan_time = 0.0

        elif self.end_time is not None:
            scan_time = self.end_time - self.start_time

        else:
            scan_time = time.time() - self.start_time

        return {
            "folders": len(self.folders),
            "files": len(self.files),
            "errors": len(self.errors),
            "scan_time": round(scan_time, 3)
        }

    @staticmethod
    def _is_hidden(path: Path) -> bool:
        """
        Determine whether a file or directory is hidden.

        Linux/macOS:
            Names beginning with '.' are hidden.

        Windows:
            Uses the hidden file attribute when available.
        """

        if path.name.startswith("."):
            return True

        try:
            attributes = path.stat().st_file_attributes

            return bool(
                attributes & stat.FILE_ATTRIBUTE_HIDDEN
            )

        except (AttributeError, OSError):
            return False