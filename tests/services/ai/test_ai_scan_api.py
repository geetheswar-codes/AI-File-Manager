from pathlib import Path as RealPath
from types import SimpleNamespace

from backend.api.v1 import ai


def test_managed_scan_passes_only_current_users_files_to_coordinator(
    tmp_path, monkeypatch
):
    """A flat upload directory must not cause a cross-user AI scan."""

    uploads_root = tmp_path / "storage" / "uploads"
    uploads_root.mkdir(parents=True)
    owned_path = uploads_root / "owned.txt"
    other_user_path = uploads_root / "other-user.txt"
    owned_path.write_text("owned content")
    other_user_path.write_text("other user content")

    selected_file = SimpleNamespace(
        id=1,
        owner_id=1,
        storage_path=str(owned_path),
    )
    other_user_file = SimpleNamespace(
        id=2,
        owner_id=2,
        storage_path=str(other_user_path),
    )
    captured = {}

    class FakeCoordinator:
        def __init__(self, db):
            assert db == "db-session"

        def scan_and_analyze(self, **kwargs):
            captured.update(kwargs)
            return {"scan": "complete"}

    def fake_path(path):
        if str(path) == "storage/uploads":
            return uploads_root
        return RealPath(path)

    monkeypatch.setattr(ai, "Path", fake_path)
    monkeypatch.setattr(ai, "AIScanCoordinator", FakeCoordinator)
    monkeypatch.setattr(
        ai.FileService,
        "get_file",
        staticmethod(lambda **kwargs: selected_file),
    )
    monkeypatch.setattr(
        ai.FileService,
        "get_all_files",
        staticmethod(lambda db, owner_id: [selected_file]),
    )

    result = ai.scan_file_directory(
        file_id=selected_file.id,
        db="db-session",
        current_user=SimpleNamespace(id=1),
    )

    assert result == {"scan": "complete"}
    assert captured == {"file_paths": [str(owned_path.resolve())]}
    assert str(other_user_file.storage_path) not in captured["file_paths"]
