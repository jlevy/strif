from pathlib import Path
from typing import Any, cast

import pytest

from strif import (
    abbrev_list,
    abbrev_str,
    ensure_bytes,
    ensure_str,
    lenb,
    quote_if_needed,
    single_line,
)


def test_quote_if_needed():
    assert quote_if_needed("foo") == "foo"
    assert quote_if_needed("item_3") == "item_3"
    assert quote_if_needed("foo bar") == "'foo bar'"
    assert quote_if_needed("!foo") == "'!foo'"
    assert quote_if_needed("") == "''"
    assert quote_if_needed(None) == "None"
    assert quote_if_needed(Path("file.txt")) == "file.txt"
    assert quote_if_needed(Path("my file.txt")) == "'my file.txt'"
    assert quote_if_needed("it's a string") == '"it\'s a string"'
    assert quote_if_needed("~/my/path/file.txt") == "~/my/path/file.txt"


def test_abbrev_str():
    assert abbrev_str("short text") == "short text"
    assert abbrev_str("") == ""
    assert abbrev_str("a" * 100, max_len=10) == "aaaaaaaaa…"
    assert abbrev_str("hello world", max_len=8) == "hello w…"
    assert abbrev_str("hello", max_len=None) == "hello"
    assert abbrev_str("hello", max_len=0) == "hello"
    assert abbrev_str("hello", max_len=1) == "h"  # Too short for indicator


def test_abbrev_list():
    assert abbrev_list([]) == "[]"
    assert abbrev_list(["a", "b", "c"]) == "a, b, c"
    assert abbrev_list(["a" * 50, "b"], item_max_len=10) == "aaaaaaaaa…, b"
    assert abbrev_list(list(range(12)), max_items=3) == "0, 1, 2, …"
    assert abbrev_list(["a", "b"], joiner=" | ") == "a | b"


def test_single_line():
    assert single_line("hello\nworld") == "hello world"
    assert single_line("  spaces  \t tabs  \n newlines  ") == "spaces tabs newlines"
    assert single_line("\n\n\n") == ""


def test_lenb():
    assert lenb("hello") == 5
    assert lenb("👋") == 4
    assert lenb("café", encoding="utf-8") == 5
    assert lenb("café", encoding="latin-1") == 4


def test_ensure_str():
    # Str inputs
    assert ensure_str("hello") == "hello"
    assert ensure_str("") == ""
    assert ensure_str("café") == "café"

    # Bytes inputs
    assert ensure_str(b"hello") == "hello"
    assert ensure_str(b"") == ""
    assert ensure_str("café".encode()) == "café"
    assert ensure_str(bytearray(b"hello")) == "hello"

    # Idempotence
    assert ensure_str(ensure_str(b"hello")) == "hello"
    assert ensure_str(ensure_str("hello")) == "hello"

    # Alternative encodings
    assert ensure_str("café".encode("latin-1"), encoding="latin-1") == "café"

    # Errors parameter
    invalid_utf8 = b"\xff\xfe"
    with pytest.raises(UnicodeDecodeError):
        ensure_str(invalid_utf8, errors="strict")
    assert "\ufffd" in ensure_str(invalid_utf8, errors="replace")
    assert ensure_str(invalid_utf8, errors="ignore") == ""

    # Reject invalid/empty encoding or error handlers
    with pytest.raises(LookupError):
        ensure_str(b"hello", encoding="")
    with pytest.raises(LookupError):
        ensure_str(invalid_utf8, errors="")

    # Invalid types
    with pytest.raises(TypeError, match="Expected str or bytes-like object"):
        ensure_str(cast(Any, 123))
    with pytest.raises(TypeError, match="Expected str or bytes-like object"):
        ensure_str(cast(Any, None))


def test_ensure_bytes():
    # Bytes inputs
    assert ensure_bytes(b"hello") == b"hello"
    assert ensure_bytes(b"") == b""
    assert ensure_bytes(bytearray(b"hello")) == b"hello"

    # Str inputs
    assert ensure_bytes("hello") == b"hello"
    assert ensure_bytes("") == b""
    assert ensure_bytes("café") == "café".encode()

    # Idempotence
    assert ensure_bytes(ensure_bytes("hello")) == b"hello"
    assert ensure_bytes(ensure_bytes(b"hello")) == b"hello"

    # Alternative encodings
    assert ensure_bytes("café", encoding="latin-1") == "café".encode("latin-1")

    # Errors parameter
    with pytest.raises(UnicodeEncodeError):
        ensure_bytes("testé ☕", encoding="ascii", errors="strict")
    assert ensure_bytes("testé ☕", encoding="ascii", errors="ignore") == b"test "

    # Reject invalid/empty encoding or error handlers
    with pytest.raises(LookupError):
        ensure_bytes("hello", encoding="")
    with pytest.raises(LookupError):
        ensure_bytes("testé ☕", encoding="ascii", errors="")

    # Invalid types
    with pytest.raises(TypeError, match="Expected str or bytes-like object"):
        ensure_bytes(cast(Any, 123))
    with pytest.raises(TypeError, match="Expected str or bytes-like object"):
        ensure_bytes(cast(Any, None))
