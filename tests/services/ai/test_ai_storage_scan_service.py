from pathlib import Path

import pytest

from backend.services.ai.ai_storage_scan_service import (
    AIStorageScanService,
)


def test_scan_rejects_unauthorized_directory(tmp_path):
    allowed = tmp_path / "allowed"
    outside = tmp_path / "outside"

    allowed.mkdir()
    outside.mkdir()

    service = AIStorageScanService(
        db=None,
        allowed_roots=[str(allowed)],
    )

    with pytest.raises(PermissionError):
        service.scan(str(outside))


def test_scan_rejects_missing_directory(tmp_path):
    service = AIStorageScanService(
        db=None,
        allowed_roots=[str(tmp_path)],
    )

    missing = tmp_path / "missing"

    with pytest.raises(FileNotFoundError):
        service.scan(str(missing))
