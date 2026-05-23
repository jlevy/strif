import re

from strif import new_timestamped_uid, new_uid

_BASE36 = re.compile(r"^[0-9a-z]+$")


def test_new_uid_charset_and_length():
    assert _BASE36.match(new_uid())
    # Length follows int(bits / 5.16) + 1 over the 36-char alphabet.
    assert len(new_uid(32)) == int(32 / 5.16) + 1
    assert len(new_uid(64)) == int(64 / 5.16) + 1
    assert len(new_uid(128)) > len(new_uid(64))


def test_new_uid_is_random():
    assert new_uid() != new_uid()


def test_new_timestamped_uid_sorts_by_time():
    first = new_timestamped_uid()
    second = new_timestamped_uid()
    # Timestamp prefix means lexical order tracks creation order.
    assert first < second
    # Starts with a UTC date like 20150912T...
    assert re.match(r"^\d{8}T\d{6}", first)
