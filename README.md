# strif

Strif is a tiny (<1000 loc) library of string- and file-related utilities for Python 2.

Why bother, if it's so short?
Because it saves time, fills in gaps, avoids clumsy repetition, and has
no other dependencies.

The goal is to complement the standard libs, not replace or wrap them.
It's basically an assembly of some functions and tricks that have repeatedly
shown value in various projects.

## Highlights

### Atomic file operations plus extras

It's generally good practice when creating files to write to a file with a
temporary name, and move it to a final location once the file is complete.
This way, you never leave partial, incorrect versions of files in a directory
due to interruptions or failures. For example, these can be used in place of
`shutil.copyfile` or `shutil.copytree`:

```python
copyfile_atomic(source_path, dest_path, make_parents=True, backup_suffix=None)
copytree_atomic(source_path, dest_path, make_parents=True, backup_suffix=None, symlinks=False)
```

You also have convenience options for creating parent directories of the
target, if they don't exist. And you can keep a backup of the target, rather
than clobber it, if you prefer. Used judiciously, these options can save you some
boilerplate coding.

### Syntax sugar for atomic file creation

Similarly, you have syntax sugar for creating files or directories atomically using `with`:

```python
with atomic_output_file("some-dir/my-final-output.txt", make_parents=True) as temp_target:
  with open(temp_target, "w") as f:
    f.write("some contents")
```

Now if there is some issue during write, the output will instead be at a
temporary location in the same directory (called `some-dir/my-final-output.txt.partial.XXXXX`).
This ensures integrity of the file appearing in the final location.

### Syntax sugar for temporary files

Syntax sugar for auto-deleting temporary files or directories using `with`:

```python
with temp_output_file("my-scratch.") as (fd, path):
  # Do a bunch of stuff with the opened file descriptor or path, knowing
  # it will be removed assuming successful termination.


with temp_output_dir("work-dir.", dir="/var/tmp") as work_dir:
  # Create some files in the now-existing path work_dir, and it will be
  # deleted afterwords.
```

Note these don't delete files in case of error, which is usually what you want.
Add `always_clean=True` if you want the temporary file or directory to be removed
no matter what.

### Miscellany

- Secure random [base 36](https://en.wikipedia.org/wiki/Base36) identifiers.
  Digression: Use base 36 in general for random id strings. It is briefer than
  hex, avoids ugly non-alphanumeric characters like base 64, and is case insensitive,
  which is generally wise (e.g. due to MacOS case-insensitive filesystems).
- Secure random timestamped and base 36 identifiers. These are similar, but start with
  an ISO timestamp, so that they sort chronologically but are still unique.
- Abbreviate strings and lists in a pretty way, truncating items and adding ellipses.

## Installation

```bash
pip install strif
```

Or add as a dependency in your setup.py.

## Contributing

Please file issues or PRs!

## License

Apache 2.
