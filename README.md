# strif

Strif is a tiny (<1000 loc) library of string and file utilities for modern Python.

It’s an assembly of some functions and tricks that have repeatedly shown value in
various projects. The goal is to complement the standard libs, not replace or wrap them.

✨ **NEW:** **Version 2.0** is now updated for Python 3.10-3.13! ✨

## FAQ

### Why bother, if it’s so short?

Because it saves time, avoids clumsy repetition, and has zero (yes zero) dependencies.

### Is it mature?

I’ve used many of these functions in production situations for years.
But it’s not a comprehensively tested library.

## Highlights

### Atomic file operations plus extras

It’s generally good practice when creating files to write to a file with a temporary
name, and move it to a final location once the file is complete.
This way, you never leave partial, incorrect versions of files in a directory due to
interruptions or failures.

For example, these can (and in most cases should) be used in place of `shutil.copyfile`
or `shutil.copytree`:

```python
copyfile_atomic(source_path, dest_path, make_parents=True, backup_suffix=None)
copytree_atomic(source_path, dest_path, make_parents=True, backup_suffix=None, symlinks=False)
```

You also have convenience options for creating parent directories of the target, if they
don’t exist. And you can keep a backup of the target, rather than clobber it, if you
prefer. Used judiciously, these options can save you some boilerplate coding.

### Easy atomic file creation

Similarly, you have syntax sugar for creating files or directories atomically using
`with`:

```python
with atomic_output_file("some-dir/my-final-output.txt") as temp_target:
  with open(temp_target, "w") as f:
    f.write("some contents")
```

Now if there is some issue during write, the output will instead be at a temporary
location in the same directory.
(It will have a name like `some-dir/my-final-output.txt.partial.XXXXX`.) This ensures
integrity of the file appearing in the final location.

There are also some handy additional options:

```python
with atomic_output_file("some-dir/my-final-output.txt",
                        make_parents=True, backup_suffix=".old.{timestamp}") as temp_target:
  with open(temp_target, "w") as f:
    f.write("some contents")
```

This creates parent folders as needed (a major convenience).
And if you would have clobbered a previous output, it keeps a backup with a (fixed or
uniquely timestamped) suffix.

### Syntax sugar for temporary files

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

## Other useful utilities

- **Secure random [base 36](https://en.wikipedia.org/wiki/Base36) identifiers:**
  Digression: Use base 36 in general for random id strings.
  It is briefer than hex, avoids ugly non-alphanumeric characters like base 64, and is
  case insensitive, which is generally wise (e.g. due to MacOS case-insensitive
  filesystems).

- **Secure random timestamped identifiers.** These are similar, but start with an ISO
  timestamp plus a base 36 identifier, so that they sort chronologically but are still
  unique.

- **Abbreviations for strings and lists:** Abbreviate strings and lists in a pretty way,
  truncating items and adding ellipses.

## Notes on atomic file operations

Notes on atomic file operations and backups, offered by several functions:

All atomic operations with "atomic" in the sense that they do a single move of a
complete file or directory into its final location.
An incomplete file or directory will never appear in its final location, and multiple
simultaneous operations will never yield corrupt output in the final location.

With `backup_suffix`, the target file or directory will be moved to an alternate
location before any file or directory is put in its place.
You can keep just one backup, or infinitely many by putting the special string
'{timestamp}' into the `backup_suffix` parameter.

Note however that with directories, or with `backup_suffix`, both the old and the new
file or directory may be absent *very* briefly since the old copy needs to be moved
before the new one is moved into place.
With files and no `backup_suffix`, the target is clobbered on the filesystem directly so
will always exist.

## Installation

```sh
# Use pip
pip install strif
# Or poetry
poetry add strif
```

## Further Information

There are quite a few small, useful functions, with full pydoc:

```sh
pydoc strif
```

## Contributing

Please file issues or PRs!
