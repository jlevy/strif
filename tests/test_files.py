import os
from pathlib import Path

import pytest

from strif import (
    atomic_output_file,
    atomic_write_bytes,
    atomic_write_text,
    copy_to_backup,
    is_truthy,
    move_file,
    temp_output_dir,
    temp_output_file,
)


def test_atomic_output_file_happy_path(tmp_path: Path):
    out = tmp_path / "out.txt"
    with atomic_output_file(out) as tmp:
        tmp.write_text("hello")
    assert out.read_text() == "hello"
    assert not list(tmp_path.glob("*.partial"))


def test_atomic_output_file_leaves_partial_on_exception(tmp_path: Path):
    out = tmp_path / "out.txt"
    with pytest.raises(RuntimeError):
        with atomic_output_file(out) as tmp:
            tmp.write_text("partial")
            raise RuntimeError("boom")
    assert not out.exists()
    assert list(tmp_path.glob("*.partial"))


def test_atomic_output_file_with_backup_suffix(tmp_path: Path):
    out = tmp_path / "out.txt"
    out.write_text("old")
    with atomic_output_file(out, backup_suffix=".bak") as tmp:
        tmp.write_text("new")
    assert out.read_text() == "new"
    assert (tmp_path / "out.txt.bak").read_text() == "old"


def test_atomic_output_file_make_parents(tmp_path: Path):
    target = tmp_path / "sub" / "nested" / "out.txt"
    with atomic_output_file(target, make_parents=True) as tmp:
        tmp.write_text("deep")
    assert target.read_text() == "deep"


def test_atomic_output_file_raises_if_target_is_dir(tmp_path: Path):
    target = tmp_path / "target"
    target.mkdir()
    with pytest.raises(FileExistsError):
        with atomic_output_file(target) as tmp:
            tmp.write_text("x")


def test_atomic_output_file_force_replaces_dir(tmp_path: Path):
    target = tmp_path / "target"
    target.mkdir()
    (target / "child.txt").write_text("child")
    with atomic_output_file(target, force=True) as tmp:
        tmp.write_text("now a file")
    assert target.is_file()
    assert target.read_text() == "now a file"


def test_atomic_output_file_timestamp_backups_do_not_clobber(tmp_path: Path):
    out = tmp_path / "out.txt"
    out.write_text("v1")
    with atomic_output_file(out, backup_suffix="{timestamp}.bak") as tmp:
        tmp.write_text("v2")
    with atomic_output_file(out, backup_suffix="{timestamp}.bak") as tmp:
        tmp.write_text("v3")
    # Each write keeps its own uniquely-named backup, so both prior versions survive.
    backups = sorted(p.read_text() for p in tmp_path.glob("out.txt*bak"))
    assert out.read_text() == "v3"
    assert backups == ["v1", "v2"]


def test_atomic_write_text_and_bytes(tmp_path: Path):
    text_path = tmp_path / "a.txt"
    atomic_write_text(text_path, "hello")
    assert text_path.read_text() == "hello"

    bytes_path = tmp_path / "b.bin"
    atomic_write_bytes(bytes_path, b"\x00\x01\x02")
    assert bytes_path.read_bytes() == b"\x00\x01\x02"


def test_atomic_write_text_make_parents_and_backup(tmp_path: Path):
    nested = tmp_path / "sub" / "a.txt"
    atomic_write_text(nested, "first", make_parents=True)
    atomic_write_text(nested, "second", backup_suffix=".bak")
    assert nested.read_text() == "second"
    assert (tmp_path / "sub" / "a.txt.bak").read_text() == "first"


@pytest.mark.skipif(not os.path.exists("/proc/self/fd"), reason="Linux-only fd accounting")
def test_temp_output_file_no_fd_leak():
    before = len(os.listdir("/proc/self/fd"))
    for _ in range(5):
        with temp_output_file() as (_fd, _path):
            pass
    after = len(os.listdir("/proc/self/fd"))
    assert after == before


def test_temp_output_file_user_close_still_works():
    with temp_output_file() as (fd, _path):
        os.close(fd)  # Double-close in cleanup must be swallowed.


def test_temp_output_dir_cleanup():
    with temp_output_dir() as d:
        (d / "a.txt").write_text("x")
    assert not d.exists()


def test_is_truthy_bool_inputs():
    assert is_truthy(True) is True
    assert is_truthy(False) is False


def test_is_truthy_string_inputs():
    for val in ("true", "yes", "1", "on", "y", "True", "  YES  "):
        assert is_truthy(val) is True, f"Expected True for {val!r}"
    for val in ("false", "no", "0", "off", "n", ""):
        assert is_truthy(val) is False, f"Expected False for {val!r}"


def test_is_truthy_numeric():
    assert is_truthy(0) is False
    assert is_truthy(1) is True
    assert is_truthy(0.0) is False
    assert is_truthy(3.14) is True


def test_is_truthy_sized():
    assert is_truthy([]) is False
    assert is_truthy([1]) is True
    assert is_truthy({}) is False
    assert is_truthy({"a": 1}) is True


def test_is_truthy_strict():
    with pytest.raises(ValueError):
        is_truthy(object(), strict=True)
    assert is_truthy(object(), strict=False) is True


def test_copy_to_backup_silent_if_missing(tmp_path: Path):
    copy_to_backup(tmp_path / "nonexistent.txt")


def test_copy_to_backup_copies(tmp_path: Path):
    src = tmp_path / "file.txt"
    src.write_text("data")
    copy_to_backup(src, backup_suffix=".bak")
    assert src.read_text() == "data"
    assert (tmp_path / "file.txt.bak").read_text() == "data"


def test_move_file_with_backup(tmp_path: Path):
    src = tmp_path / "src.txt"
    dest = tmp_path / "dest.txt"
    dest.write_text("old")
    src.write_text("new")
    move_file(src, dest, keep_backup=True, backup_suffix=".bak")
    assert dest.read_text() == "new"
    assert not src.exists()
    assert (tmp_path / "dest.txt.bak").read_text() == "old"


def test_move_file_creates_parents(tmp_path: Path):
    src = tmp_path / "src.txt"
    src.write_text("content")
    dest = tmp_path / "sub" / "dest.txt"
    move_file(src, dest, keep_backup=False)
    assert dest.read_text() == "content"
