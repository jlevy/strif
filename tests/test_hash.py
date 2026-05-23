import hashlib
from pathlib import Path

import pytest

from strif import hash_file, hash_string


def test_hash_file(tmp_path: Path):
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("Hello, World!")

    result_hash = hash_file(file_path, "sha1").with_prefix
    assert result_hash == "sha1:0a0a9f2a6772942557ab5355d76af442f8f65e01"

    assert hash_string("Hello, World!").with_prefix == result_hash

    assert hash_string("Hello, World!").base64 == "CgqfKmdylCVXq1NV12r0Qvj2XgE="


def test_hash_file_binary_and_chunked(tmp_path: Path):
    # Non-UTF8 bytes plus a payload larger than the 8192-byte read chunk, to exercise
    # the chunked read loop and confirm binary content hashes identically to hashlib.
    payload = bytes(range(256)) * 500  # 128 KB
    file_path = tmp_path / "blob.bin"
    file_path.write_bytes(payload)

    assert hash_file(file_path, "sha256").hex == hashlib.sha256(payload).hexdigest()


def test_hash_file_unsupported_algorithm(tmp_path: Path):
    file_path = tmp_path / "f.txt"
    file_path.write_text("x")
    with pytest.raises(ValueError):
        hash_file(file_path, "not-a-real-algo")
