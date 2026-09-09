from pathlib import Path


class StorageAccessService:
    """
    Resolve and validate filesystem locations that the AI scanner
    is allowed to access.

    This service does not modify files.
    """

    def __init__(self, allowed_roots: list[str]):
        self.allowed_roots = [
            Path(root).expanduser().resolve()
            for root in allowed_roots
        ]

    def is_allowed(self, path: str) -> bool:
        """
        Return True only when the requested path is inside
        one of the configured authorized roots.
        """

        requested_path = Path(path).expanduser().resolve()

        for root in self.allowed_roots:
            try:
                requested_path.relative_to(root)
                return True
            except ValueError:
                continue

        return False

    def validate_directory(self, path: str) -> Path:
        """
        Validate that a path is an accessible authorized directory.
        """

        resolved_path = Path(path).expanduser().resolve()

        if not self.is_allowed(str(resolved_path)):
            raise PermissionError(
                "Path is outside the authorized storage areas."
            )

        if not resolved_path.exists():
            raise FileNotFoundError(
                "Storage path does not exist."
            )

        if not resolved_path.is_dir():
            raise NotADirectoryError(
                "Storage path is not a directory."
            )

        return resolved_path
