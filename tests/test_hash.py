import os

from strif import hash_file


def test_hash_file():
    os.makedirs("tmp", exist_ok=True)
    file_path = "tmp/test_file.txt"

    with open(file_path, "w") as f:
        f.write("Hello, World!")

    result_hash = hash_file(file_path, "sha1").with_prefix
    assert result_hash == "sha1:0a0a9f2a6772942557ab5355d76af442f8f65e01"
