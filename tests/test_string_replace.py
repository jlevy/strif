import pytest

from strif.string_replace import Insertion, Replacement, insert_multiple, replace_multiple


def test_named_tuple_fields_and_positional_compat():
    # NamedTuple gives named access while staying tuple-compatible, so both the named
    # and positional/unpacking APIs must work.
    ins = Insertion(offset=5, text=",")
    assert ins.offset == 5 and ins.text == ","
    assert ins == (5, ",")

    start, end, text = Replacement(0, 3, "x")
    assert (start, end, text) == (0, 3, "x")


def test_insert_multiple():
    assert insert_multiple("hello world", [Insertion(5, ",")]) == "hello, world"
    assert (
        insert_multiple("hello world", [Insertion(0, "Start "), Insertion(11, " End")])
        == "Start hello world End"
    )
    # Out-of-bounds offset clamps to the end.
    assert insert_multiple("short", [Insertion(10, " end")]) == "short end"
    # Negative offset indexes from the end.
    assert insert_multiple("negative test", [Insertion(-1, "ss")]) == "negative tessst"
    assert insert_multiple("no change", []) == "no change"


def test_replace_multiple():
    assert (
        replace_multiple(
            "The quick brown fox", [Replacement(4, 9, "slow"), Replacement(16, 19, "dog")]
        )
        == "The slow brown dog"
    )
    # Out-of-bounds end clamps to the end.
    assert (
        replace_multiple("short text", [Replacement(5, 10, " longer text")]) == "short longer text"
    )
    assert replace_multiple("no change", []) == "no change"


def test_replace_multiple_rejects_overlap():
    with pytest.raises(ValueError):
        replace_multiple("overlap test", [Replacement(0, 6, "start"), Replacement(5, 10, "end")])
