from pathlib import Path

from utils.git_mirror_size import (
    SIZE_FILENAME,
    MirrorSizeCollector,
    directory_size_bytes,
    record_mirror_size,
)


def test_directory_size_bytes_sums_files(tmp_path: Path) -> None:
    (tmp_path / "a").write_bytes(b"abc")
    nested = tmp_path / "sub"
    nested.mkdir()
    (nested / "b").write_bytes(b"xy")

    assert directory_size_bytes(tmp_path) == 5


def test_directory_size_bytes_missing_path_is_zero(tmp_path: Path) -> None:
    assert directory_size_bytes(tmp_path / "missing") == 0


def test_record_mirror_size_writes_integer_without_temp(tmp_path: Path) -> None:
    (tmp_path / "pack").write_bytes(b"hello")

    size = record_mirror_size(tmp_path)

    written = tmp_path / SIZE_FILENAME
    assert size == 5
    assert written.read_text() == "5\n"
    temps = [
        path
        for path in tmp_path.iterdir()
        if path.name.startswith(f".{SIZE_FILENAME}.")
    ]
    assert temps == []


def test_record_mirror_size_missing_dir_leaves_nothing(tmp_path: Path) -> None:
    missing = tmp_path / "missing"

    assert record_mirror_size(missing) is None
    assert not missing.exists()


def test_collector_emits_size_and_mtime(tmp_path: Path) -> None:
    size_file = tmp_path / SIZE_FILENAME
    size_file.write_text("42\n")
    mtime = size_file.stat().st_mtime

    families = list(MirrorSizeCollector(size_file).collect())

    by_name = {family.name: family.samples[0].value for family in families}
    assert by_name["git_mirror_size_bytes"] == 42
    assert by_name["git_mirror_size_mtime_seconds"] == mtime


def test_collector_emits_nothing_when_file_is_missing(tmp_path: Path) -> None:
    families = list(MirrorSizeCollector(tmp_path / SIZE_FILENAME).collect())

    assert families == []
