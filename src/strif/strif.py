"""
Strif is a tiny (<1000 loc) library of string and file utilities,
now updated for Python 3.10+.

More information: https://github.com/jlevy/strif
"""

import hashlib
import os
import random
import re
import shutil
import subprocess
import tempfile
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# A pre-opened handle to /dev/null.
DEV_NULL = open(os.devnull, "wb")

BACKUP_SUFFIX = ".bak"
TIMESTAMP_VAR = "{timestamp}"
DEFAULT_BACKUP_SUFFIX = f"{TIMESTAMP_VAR}{BACKUP_SUFFIX}"

_RANDOM = random.SystemRandom()
_RANDOM.seed()

#
# ---- Timestamps ----


def iso_timestamp(microseconds: bool = True) -> str:
    """
    ISO 8601 timestamp. Includes the Z for clarity that it is UTC.

    Example with microseconds: 2015-09-12T08:41:12.397217Z
    Example without microseconds: 2015-09-12T08:41:12Z
    """
    timespec = "microseconds" if microseconds else "seconds"
    return datetime.now(timezone.utc).isoformat(timespec=timespec).replace("+00:00", "Z")


def format_iso_timestamp(datetime_obj: datetime, microseconds: bool = True) -> str:
    """
    Format a datetime as an ISO 8601 timestamp. Includes the Z for clarity that it is timezone.utc.

    Example with microseconds: 2015-09-12T08:41:12.397217Z
    Example without microseconds: 2015-09-12T08:41:12Z
    """
    timespec = "microseconds" if microseconds else "seconds"
    return datetime_obj.astimezone(timezone.utc).isoformat(timespec=timespec).replace("+00:00", "Z")


#
# ---- Identifiers and base36 encodings ----


def new_uid(bits: int = 64) -> str:
    """
    A random alphanumeric value with at least the specified bits of randomness. We use base 36,
    i.e., not case sensitive. Note this makes it suitable for filenames even on case-insensitive disks.
    """
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    length = int(bits / 5.16) + 1  # log2(36) ≈ 5.17
    return "".join(_RANDOM.choices(chars, k=length))


def new_timestamped_uid(bits: int = 32) -> str:
    """
    A unique id that begins with an ISO timestamp followed by fractions of seconds and bits of
    randomness. The advantage of this is it sorts nicely by time, while still being unique.

    Example: 20150912T084555Z-378465-43vtwbx
    """
    timestamp = re.sub(r"[^\w.]", "", datetime.now(timezone.utc).isoformat()).replace(".", "Z-")
    return f"{timestamp}-{new_uid(bits)}"


_NON_ALPHANUM_CHARS = re.compile(r"[^a-z0-9]+", re.IGNORECASE)


def clean_alphanum(string: str, max_length: int | None = None) -> str:
    """
    Convert a string to a clean, readable identifier that includes the (first) alphanumeric
    characters of the given string, replacing non-alphanumeric characters with underscores.

    This mapping is for readability only, and so can easily have collisions on different inputs.
    """
    return _NON_ALPHANUM_CHARS.sub("_", string)[:max_length]


def clean_alphanum_hash(string: str, max_length: int = 64, max_hash_len: int | None = None) -> str:
    """
    Convert a string to a clean, readable identifier that includes the (first) alphanumeric
    characters of the given string. Result is a string of length at most max_length,
    unless max_length is so short that the base36 SHA1 hash won't fit.

    Example: clean_alphanum_hash("foo")
      -> 'foo_1e6gpc3ehk0mu2jqu8cg42g009s796b'

    This includes a base36 SHA1 hash so collisions are unlikely.
    """
    hash_str = hash_string(string, algorithm="sha1").base36
    if max_hash_len:
        hash_str = hash_str[:max_hash_len]
    if max_length < len(hash_str) + 1:
        return hash_str
    else:
        clean_str = clean_alphanum(string, max_length=max_length - len(hash_str))
        return f"{clean_str}_{hash_str}"


def file_mtime_hash(path: str | Path) -> str:
    """
    An imperfect but fast hash to detect file modifications via high-resolution
    modification time. Hashes the file name, size, and modification time,
    and these are preserved in the prefix to help with sorting or debugging.

    Example: file_mtime_hash("foo.txt")
      -> 'foo_txt_1725_1732233268408136030_d1rgdwjlr29083zgd96ws9wq1807mps'

    This is not guaranteed to be perfect like a content hash, but works for simple
    use cases. Nanosecond precision via `st_mtime_ns` works on most platforms.
    """
    path = Path(path)
    name = path.name
    stat = path.stat()
    size = stat.st_size
    mtime = getattr(stat, "st_mtime_ns", int(stat.st_mtime * 1e9))
    key = f"{name}-{size}-{mtime}"
    return clean_alphanum_hash(key, max_length=64)


def base36_encode(n: int) -> str:
    """
    Base 36 encode an integer.
    """
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    if n == 0:
        return "0"
    encoded = ""
    while n > 0:
        n, remainder = divmod(n, 36)
        encoded = chars[remainder] + encoded
    return encoded


@dataclass(frozen=True)
class Hash:
    """
    A simple, flexible hash format. Includes the algorithm used to compute it and
    can convert to hex or base36 format or a prefixed format that includes the
    algorithm name.

    Base 36 format is good for short, friendly identifiers. Length of a SHA1 hash
    in base36 is ~32 chars.

    Example:
      hash_string("foo").base36
      -> '1e6gpc3ehk0mu2jqu8cg42g009s796b'
    """

    algorithm: str
    value: bytes

    @property
    def hex(self) -> str:
        return self.value.hex()

    @property
    def base36(self) -> str:
        return base36_encode(int.from_bytes(self.value, byteorder="big"))

    @property
    def with_prefix(self) -> str:
        return f"{self.algorithm}:{self.hex}"


def hash_string(string: str, algorithm: str = "sha1") -> Hash:
    """
    Flexible hash of a string.
    """
    hasher = hashlib.new(algorithm)
    hasher.update(string.encode("utf8"))
    return Hash(algorithm, hasher.digest())


def hash_file(file_path: str | Path, algorithm: str = "sha1") -> Hash:
    """
    Hash the content of a file.
    """
    if algorithm not in hashlib.algorithms_available:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")

    hasher = hashlib.new(algorithm)
    file_path = Path(file_path)
    with file_path.open("rb") as file:
        while chunk := file.read(8192):
            hasher.update(chunk)
    return Hash(algorithm, hasher.digest())


#
# ---- Abbreviations and formatting ----


def abbrev_str(string: str, max_len: int | None = 80, indicator: str = "…") -> str:
    """
    Abbreviate a string, adding an indicator like an ellipsis if required. Set `max_len` to
    None or 0 not to truncate items.
    """
    if not string or not max_len or len(string) <= max_len:
        return string
    elif max_len <= len(indicator):
        return string[:max_len]
    else:
        return string[: max_len - len(indicator)] + indicator


def abbrev_list(
    items: list[Any],
    max_items: int = 10,
    item_max_len: int | None = 40,
    joiner: str = ", ",
    indicator: str = "…",
) -> str:
    """
    Abbreviate a list, truncating each element and adding an indicator at the end if the
    whole list was truncated. Set `item_max_len` to None or 0 not to truncate items.
    """
    if not items:
        return str(items)
    else:
        shortened = [abbrev_str(str(item), max_len=item_max_len) for item in items[:max_items]]
        if len(items) > max_items:
            shortened.append(indicator)
        return joiner.join(shortened)


abbreviate_str = abbrev_str
"""Deprecated. Use `abbrev_str()` instead."""

abbreviate_list = abbrev_list
"""Deprecated. Use `abbrev_list()` instead."""


def single_line(text: str) -> str:
    """
    Convert newlines and other whitespace to spaces.
    """
    return re.sub(r"\s+", " ", text).strip()


def is_quotable(s: str) -> bool:
    """
    Does this string need to be quoted? Same as the logic used by `shlex.quote()`
    but with the addition of ~ since this character isn't generally needed to be quoted.
    """
    return bool(re.compile(r"[^\w@%+=:,./~-]").search(s))


def quote_if_needed(
    arg: Any,
    to_str: Callable[[Any], str] = str,
    quote: Callable[[Any], str] = repr,
    is_quotable: Callable[[str], bool] = is_quotable,
) -> str:
    """
    A friendly way to format a Path or string for display, adding quotes only
    if needed for clarity. Intended for brevity and readability, not as a
    parsable format.

    Quotes strings similarly to `shlex.quote()`, so is mostly compatible with
    shell quoting rules. By default, uses `str()` on non-string objects and
    `repr()` for quoting, so is compatible with Python.
    ```
    print(quote_if_needed("foo")) -> foo
    print(quote_if_needed("item_3")) -> item_3
    print(quote_if_needed("foo bar")) -> 'foo bar'
    print(quote_if_needed("!foo")) -> '!foo'
    print(quote_if_needed("")) -> ''
    print(quote_if_needed(None)) -> None
    print(quote_if_needed(Path("file.txt"))) -> file.txt
    print(quote_if_needed(Path("my file.txt"))) -> 'my file.txt'
    print(quote_if_needed("~/my/path/file.txt")) -> '~/my/path/file.txt'
    ```

    For true shell compatibility, use `shlex.quote()` instead. But note
    `shlex.quote()` can be confusingly ugly because of shell quoting rules:
    ```
    print(quote_if_needed("it's a string")) -> "it's a string"
    print(shlex.quote("it's a string")) -> 'it'"'"'s a string'
    ```

    Can pass in `to_str` and `quote` functions to customize this behavior.
    """
    if not arg:
        return quote(arg)
    if not isinstance(arg, str) and not isinstance(arg, Path):
        return to_str(arg)

    if isinstance(arg, Path):
        arg = str(arg)  # Treat Paths like strings for display.
    if is_quotable(arg):
        return quote(arg)
    else:
        return to_str(arg)


#
# ---- File operations ----


def _expand_backup_suffix(backup_suffix: str) -> str:
    return (
        backup_suffix.replace(TIMESTAMP_VAR, new_timestamped_uid())
        if TIMESTAMP_VAR in backup_suffix
        else backup_suffix
    )


# Clear the target of the backup in case it already exists.
# Note this isn't perfectly atomic, if another thread does a backup
# to an identical backup directory but this would be very rare.
def _prepare_for_backup(path: Path, backup_suffix: str) -> Path:
    if not backup_suffix:
        raise ValueError("No backup_suffix")

    backup_path = path.with_name(path.name + _expand_backup_suffix(backup_suffix))

    if backup_path.is_symlink():
        backup_path.unlink()
    elif backup_path.is_dir():
        shutil.rmtree(backup_path)

    return backup_path


def move_to_backup(path: str | Path, backup_suffix: str = DEFAULT_BACKUP_SUFFIX):
    """
    Move the given file or directory to the same name, with a backup suffix.
    If the path doesn't exist, do nothing.

    If backup_suffix not supplied, move it to the extension "{timestamp}.bak".
    In backup_suffix, the string "{timestamp}", if present, will be replaced
    by a new_timestamped_uid(), allowing infinite numbers of timestamped backups.
    If backup_suffix is supplied and is None, don't do anything.

    Important:
    Without "{timestamp}", earlier backup files and directories, if they exist,
    will be clobbered!
    """
    path = Path(path)
    if not path.exists():
        return

    backup_path = _prepare_for_backup(path, backup_suffix)
    try:
        shutil.move(str(path), str(backup_path))
    except FileNotFoundError:
        pass


def copy_to_backup(path: str | Path, backup_suffix: str = DEFAULT_BACKUP_SUFFIX):
    """
    Same as `move_to_backup()` but only copies.
    """
    path = Path(path)
    backup_path = _prepare_for_backup(path, backup_suffix)
    if path.is_dir():
        copytree_atomic(path, backup_path)
    else:
        copyfile_atomic(path, backup_path)


def move_file(
    src_path: Path,
    dest_path: Path,
    keep_backup: bool = True,
    backup_suffix: str = DEFAULT_BACKUP_SUFFIX,
):
    """
    Move file, handling parent directory creation and optionally keeping a backup
    if the destination file already exists, using `move_to_backup()`.
    """
    if not keep_backup and dest_path.exists():
        raise FileExistsError(f"Destination file already exists: {quote_if_needed(str(dest_path))}")
    if keep_backup and src_path.exists():
        move_to_backup(str(dest_path), backup_suffix=backup_suffix)

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(src_path, dest_path)

    # TODO: If we created a backup, compare file contents and remove the backup if it's
    # identical, to avoid clutter.


def make_parent_dirs(path: str | Path, mode: int = 0o777) -> Path:
    """
    Ensure parent directories of a file are created as needed.
    """
    path = Path(path)
    parent = path.parent
    if parent:
        parent.mkdir(mode=mode, parents=True, exist_ok=True)
    return path


@contextmanager
def atomic_output_file(
    dest_path: str | Path,
    make_parents: bool = False,
    backup_suffix: str | None = None,
    tmp_suffix: str = ".partial",
    force: bool = False,
) -> Generator[Path, None, None]:
    """
    A context manager for convenience in writing a file or directory in an atomic way.
    Set up a temporary name, then rename it after the operation is done, optionally making
    a backup of the previous file or directory, if present.

    An incomplete file will never appear in its final location, and multiple simultaneous
    operations will never yield corrupt output in the final location.

    With `backup_suffix`, the target file or directory will be moved to an alternate
    location before any file is put in its place. You can keep just one backup, or
    infinitely many by putting the special string '{timestamp}' into the `backup_suffix`
    parameter.

    Note that with `backup_suffix`, the output file may be absent *very* briefly
    since the old copy needs to be moved before the new one is moved into place.
    Without `backup_suffix`, the target is clobbered on the filesystem directly so
    will always exist.

    Enable `force` to force the destructive corner case of overwriting an existing
    file or directory with no backup.
    """
    dest_path = Path(dest_path)
    if dest_path == Path(os.devnull):
        # Handle the (probably rare) case of writing to /dev/null.
        yield dest_path
    else:
        tmp_path = dest_path.with_name(dest_path.name + new_uid() + tmp_suffix)
        if make_parents:
            make_parent_dirs(tmp_path)

        yield tmp_path

        # Note this is not in a finally block, so that result won't be renamed to final location
        # in case of abnormal exit.
        if not os.path.exists(tmp_path):
            raise OSError(
                f"Failure in writing file: {quote_if_needed(dest_path)}: target file missing: {quote_if_needed(tmp_path)}"
            )
        if backup_suffix:
            move_to_backup(dest_path, backup_suffix=backup_suffix)
        if os.path.isdir(dest_path):
            if force:
                # If the target already exists, and is a directory, it has to be removed.
                shutil.rmtree(dest_path)
            else:
                raise FileExistsError(f"Destination is a directory: {quote_if_needed(dest_path)}")
        shutil.move(tmp_path, dest_path)


@contextmanager
def temp_output_file(
    prefix: str = "tmp",
    suffix: str = "",
    dir: str | Path | None = None,
    make_parents: bool = False,
    always_clean: bool = False,
) -> Generator[tuple[int, Path], None, None]:
    """
    A context manager for convenience in creating a temporary file,
    which is deleted when exiting the context.

    Usage:
      with temp_output_file() as (fd, path):
        ...
    """
    if dir and make_parents:
        Path(dir).mkdir(parents=True, exist_ok=True)

    fd, path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=str(dir) if dir else None)
    result = (fd, Path(path))

    def clean():
        try:
            rmtree_or_file(result[1], ignore_errors=True)
        except OSError:
            pass

    if always_clean:
        try:
            yield result
        finally:
            clean()
    else:
        yield result
        clean()


@contextmanager
def temp_output_dir(
    prefix: str = "tmp",
    suffix: str = "",
    dir: str | Path | None = None,
    make_parents: bool = False,
    always_clean: bool = False,
) -> Generator[Path, None, None]:
    """
    A context manager for convenience in creating a temporary directory,
    which is deleted when exiting the context.

    Usage:
      with temp_output_dir() as dirname:
        ...
    """
    if dir and make_parents:
        Path(dir).mkdir(parents=True, exist_ok=True)

    path = tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=str(dir) if dir else None)
    result = Path(path)

    def clean():
        try:
            rmtree_or_file(result, ignore_errors=True)
        except OSError:
            pass

    if always_clean:
        try:
            yield result
        finally:
            clean()
    else:
        yield result
        clean()


def copyfile_atomic(
    source_path: str | Path,
    dest_path: str | Path,
    make_parents: bool = False,
    backup_suffix: str | None = None,
):
    """
    Copy file on local filesystem in an atomic way, so partial copies never exist. Preserves timestamps.
    """
    source_path = Path(source_path)
    dest_path = Path(dest_path)
    with atomic_output_file(
        dest_path, make_parents=make_parents, backup_suffix=backup_suffix
    ) as tmp_path:
        shutil.copyfile(str(source_path), str(tmp_path))
        mtime = source_path.stat().st_mtime
        os.utime(tmp_path, (mtime, mtime))


def copytree_atomic(
    source_path: str | Path,
    dest_path: str | Path,
    make_parents: bool = False,
    backup_suffix: str | None = None,
    symlinks: bool = False,
):
    """
    Copy a file or directory recursively, and atomically, renaming file or top-level dir when done.
    Unlike shutil.copytree, this will not fail on a file.
    """
    source_path = Path(source_path)
    dest_path = Path(dest_path)
    if source_path.is_dir():
        with atomic_output_file(
            dest_path, make_parents=make_parents, backup_suffix=backup_suffix
        ) as tmp_path:
            shutil.copytree(str(source_path), str(tmp_path), symlinks=symlinks)
    else:
        copyfile_atomic(
            source_path, dest_path, make_parents=make_parents, backup_suffix=backup_suffix
        )


def rmtree_or_file(path: str | Path, ignore_errors: bool = False):
    """
    rmtree fails on files or symlinks. This removes the target, whatever it is.
    """
    # TODO: Could add an rsync-based delete, as in
    # https://github.com/vivlabs/instaclone/blob/master/instaclone/instaclone.py#L127-L143
    if ignore_errors and not os.path.exists(path):
        return
    if os.path.isdir(path) and not os.path.islink(path):
        shutil.rmtree(path, ignore_errors=ignore_errors)
    else:
        os.unlink(path)


def chmod_native(path: str | Path, mode_expression: str, recursive: bool = False):
    """
    This is ugly and will only work on POSIX, but the built-in Python os.chmod support
    is very minimal, and neither supports fast recursive chmod nor "+X" type expressions,
    both of which are slow for large trees. So just shell out.
    """
    path = Path(path)
    popenargs = ["chmod"]
    if recursive:
        popenargs.append("-R")
    popenargs.append(mode_expression)
    popenargs.append(str(path))
    subprocess.check_call(popenargs)


#
# ---- Strings ----


def lenb(s: str, encoding: str = "utf-8") -> int:
    """
    Convenience for length of a string in bytes.
    """
    return len(s.encode(encoding))
