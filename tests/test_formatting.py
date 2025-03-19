from pathlib import Path

from strif.strif import abbrev_list, abbrev_str, quote_if_needed, single_line


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
