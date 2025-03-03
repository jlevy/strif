# strif

Strif is a tiny (<1000 loc) library of string and file utilities for modern Python.

It’s an assembly of some functions and tricks that have repeatedly shown value in
various projects. The goal is to complement the standard libs, not replace or wrap them.

✨ **NEW:** **Version 2.0** is now updated for Python 3.10-3.13! ✨

## Highlights

Use `pydoc strif` for full docs!
A quick overview is below.

### Base36 Identifiers

Several functions offer [base 36](https://en.wikipedia.org/wiki/Base36) identifiers.

It’s frequently preferable to use base 36. Base 36 is briefer than hex, avoids ugly
non-alphanumeric characters like base 64, and is case insensitive, which is generally
wise (e.g. due to MacOS case-insensitive filesystems).

### Text Abbreviations and Formatting

- **`abbrev_str(string: str, max_len: Optional[int] = 80, indicator: str = '…')`**

  Abbreviates a string and appends an indicator if the content exceeds the allowed
  length.
- **`abbrev_list(items: List[Any], max_items: int = 10, item_max_len: Optional[int] =
  40, joiner: str = ', ', indicator: str = '…')`**

  Shortens each element of a list and appends an ellipsis if the list is truncated.
- **`single_line(text: str)`**

  Converts multi-line text into a single line by replacing extra whitespace with spaces.
- **`quote_if_needed(arg: Any)`**

  Returns a string with quotes if needed for proper display (for example, for filenames
  with spaces).

### String Identifiers, Timestamps, and Hashing

- **`new_uid(bits: int = 64)`**

  Generates a random base36 alphanumeric string with at least the specified bits of
  randomness. Suitable for filenames (especially on case-insensitive filesystems).
- **`new_timestamped_uid(bits: int = 32)`**

  Creates a unique ID starting with an ISO timestamp, then fractions of seconds and bits
  of randomness. *Example*: `20150912T084555Z-378465-43vtwbx`
- **`iso_timestamp(microseconds: bool = True)`**

  Returns an ISO 8601 timestamp in UTC, e.g. `2015-09-12T08:41:12.397217Z` (with
  microseconds) or `2015-09-12T08:41:12Z` (without).
- **`format_iso_timestamp(datetime_obj: datetime, microseconds: bool = True)`**

  Formats a given datetime object as an ISO 8601 timestamp, ensuring UTC formatting with
  a trailing Z.
- **`clean_alphanum(string: str, max_length: Optional[int] = None)`**

  Converts a string to a clean identifier by keeping only the first alphanumeric
  characters and replacing others with underscores.
- **`clean_alphanum_hash(string: str, max_length: int = 64, max_hash_len: Optional[int]
  = None)`**

  Combines the cleaned version of a string with a base36 SHA1 hash to minimize
  collisions.

### File Hashing

- **`file_mtime_hash(path: str | Path)`**

  Computes a fast hash using a file's name, size, and high-resolution modification time,
  without looking at file contents.
  A useful key for fast caching of file contents.
- **`hash_string(string: str, algorithm: str = 'sha1') -> Hash`** and
  **`hash_file(file_path: str | Path, algorithm: str = 'sha1') -> Hash`**

  Provide flexible hashing mechanisms.
  The returned `Hash` object has properties to output the digest in hexadecimal, base36,
  or with a prefixed algorithm name.

### Atomic File Operations with Optional Backups

- **`atomic_output_file(dest_path: str | Path, make_parents: bool = False,
  backup_suffix: Optional[str] = None, tmp_suffix: str = '.partial')`**

  A context manager for writing files or directories atomically.
  A temporary file is created and, upon successful completion, renamed to the target
  location.
- **`copyfile_atomic(source_path: str | Path, dest_path: str | Path, make_parents: bool
  = False, backup_suffix: Optional[str] = None)`**

  Atomically copies a file while preserving its timestamps.
- **`copytree_atomic(source_path: str | Path, dest_path: str | Path, make_parents: bool
  = False, backup_suffix: Optional[str] = None, symlinks: bool = False)`**

  Recursively copies a directory or file atomically.
- **`move_to_backup(path: str | Path, backup_suffix: str = '{timestamp}.bak')`** and
  **`copy_to_backup(path: str | Path, backup_suffix: str = '{timestamp}.bak')`**

  Functions to move or copy an existing file or directory to a backup destination.
- **`move_file(src_path: Path, dest_path: Path, keep_backup: bool = True, backup_suffix:
  str = '{timestamp}.bak')`**

  Moves a file to a new location, automatically creating parent directories and
  optionally keeping a backup of the destination if it already exists.

It’s generally good practice when creating files to write to a file with a temporary
name, and move it to a final location once the file is complete.
This way, you never leave partial, incorrect versions of files in a directory due to
interruptions or failures.

For example, these can (and in most cases should) be used in place of `shutil.copyfile`
or `shutil.copytree`:

```python
copyfile_atomic(source_path, dest_path, make_parents=True, backup_suffix=None)
```

You also have convenience options for creating parent directories of the target, if they
don't exist. And you can keep a backup of the target, rather than clobber it, if you
prefer. Used judiciously, these options can save you some boilerplate coding.

It’s helpful to have syntax sugar for creating files or directories atomically:

```python
with atomic_output_file("some-dir/my-final-output.txt") as temp_target:
    with open(temp_target, "w") as f:
        f.write("some contents")
```

Now if there is some issue during write, the output will instead be at a temporary
location in the same directory (with a name like
`some-dir/my-final-output.txt.partial.XXXXX`.) This ensures integrity of the file
appearing in the final location.

There are also some handy additional options:

```python
with atomic_output_file("some-dir/my-final-output.txt",
                        make_parents=True, backup_suffix=".old.{timestamp}") as temp_target:
    with open(temp_target, "w") as f:
        sf.write("some contents")
```

This creates parent folders as needed (a major convenience).
And if you would have clobbered a previous output, it keeps a backup with a (fixed or
uniquely timestamped) suffix.

### Syntax Sugar for Temporary Files

Syntax sugar for auto-deleting temporary files or directories using `with`:

```python
with temp_output_file("my-scratch.") as (fd, path):
    # Do a bunch of stuff with the opened file descriptor or path, knowing
    # it will be removed assuming successful termination.


with temp_output_dir("work-dir.", dir="/var/tmp") as work_dir:
    # Create some files in the now-existing path work_dir, and it will be
    # deleted afterwards.
```

Note these don’t delete files in case of error, which is usually what you want.
Add `always_clean=True` if you want the temporary file or directory to be removed no
matter what.

## FAQ

### Why bother, if it’s so short?

Because it saves time, saves you stupid bugs and clumsy repetition, and has zero (yes
zero) dependencies.

### Is it mature?

I’ve used many of these functions in production situations for years.
But it doesn't have comprehensive tests at the moment.

## Installation

```sh
# Use pip
pip install strif
# Or poetry
poetry add strif
```

## Development

For development workflows, see [development.md](development.md).

* * *

*This project was built from
[simple-modern-poetry](https://github.com/jlevy/simple-modern-poetry).*
