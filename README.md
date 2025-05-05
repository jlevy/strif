# strif

Strif is a tiny (\~1000 loc) library of \~30 string, file, and object utilities for
modern Python. It has **zero dependencies**.

It is simply a few functions and tricks that have repeatedly shown value in various
projects. The goal is not to give a comprehensive suite of utilities but simply to
complement the standard libraries and fill in a few gaps.

✨ **NEW:** **Version 3.0** is out and has additions and updates for Python 3.10-3.13! ✨

## Key Features

- **Atomic file operations** with handling of parent directories and backups.
  This is essential for thread safety and good hygiene so partial or corrupt outputs are
  never present in final file locations, even in case a program crashes.
  See `atomic_output_file()`, `copyfile_atomic()`.

- **Abbreviate and quote strings**, which is useful for logging a clean way.
  See `abbrev_str()`, `single_line()`, `quote_if_needed()`.

- **Random UIDs** that use **base 36** (for concise, case-insensitive ids) and **ISO
  timestamped ids** (that are unique but also conveniently sort in order of creation).
  See `new_uid()`, `new_timestamped_uid()`.

- **File hashing** with consistent convenience methods for hex, base36, and base64
  formats. See `hash_string()`, `hash_file()`, `file_mtime_hash()`.

- **An `AtomicVar` type** that is a convenient way to have an `RLock` on a variable and
  remind yourself to always access the variable in a thread-safe way.

- **String utilities** for replacing or adding multiple substrings at once and for
  validating and type checking very simple string templates.
  See `StringTemplate`, `replace_multiple()`, `insert_multiple()`.

That's all! They are all quite simple.
The libs are all small so see pydoc strings or code for full docs.

> [!TIP]
> 
> If you're using strif, you might also want to check out
> [prettyfmt](https://github.com/jlevy/prettyfmt), another small library built on strif
> that has some extra functions for pretty, human-readable outputs for objects, sizes,
> times and dates, etc.

## Installation

```sh
# Use uv
uv add strif
# Or poetry
poetry add strif
# Or pip
pip install strif
```

## Text Abbreviations and Formatting

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

## String Identifiers, Timestamps, and Hashing

> [!TIP]
> 
> These functions use [base 36](https://en.wikipedia.org/wiki/Base36). If you need a
> readable, concise identifier, api key format, or hash format, consider base 36. In my
> humble opinion, base 36 ids are underrated and should be used more often:
> 
> - Base 36 is briefer than hex and yet avoids ugly non-alphanumeric characters.
>
> - Base 36 is case insensitive.
>   If you use identifiers for filenames, you definitely should prefer case insensitive
>   identifiers because of case-insensitive filesystems (like macOS).
>
> - Base 36 is easier to read aloud over the phone for an auth code or to type manually.
>
> - Base 36 is only `log(64)/log(36) - 1 = 16%` longer than base 64.
> 

- **`new_uid(bits: int = 64)`**

  Generates a random base36 alphanumeric string with at least the specified bits of
  randomness. Suitable for filenames (especially on case-insensitive filesystems).
  Uses `random.SystemRandom()` for randomness.

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

## File Hashing

- **`file_mtime_hash(path: str | Path)`**

  Computes a fast hash using a file's name, size, and high-resolution modification time,
  without looking at file contents.
  A useful key for fast caching of file contents.

- **`hash_string(string: str, algorithm: str = 'sha1') -> Hash`** and
  **`hash_file(file_path: str | Path, algorithm: str = 'sha1') -> Hash`**

  Provide flexible hashing mechanisms.
  The returned `Hash` object has properties to output the digest in hexadecimal, base36,
  or with a prefixed algorithm name.

## Atomic File Operations with Optional Backups

> [!TIP]
> 
> It’s generally good practice when creating files to write to a file with a temporary
> name, and move it to a final location once the file is complete.
> This way, you never leave partial, incorrect versions of files in a directory due to
> interruptions or failures.

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

For example, it is generally a good idea to wrap an `open()` call with
`atomic_output_file()`:

```python
with atomic_output_file("some-dir/my-final-output.txt") as temp_target:
    with open(temp_target, "w") as f:
        f.write("some contents")
```

And this can (and in most cases should) be used in place of `shutil.copyfile`:

```python
copyfile_atomic(source_path, dest_path, make_parents=True, backup_suffix=None)
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

Used judiciously, these options can save boilerplate coding and avoid debugging ugly
corner case failures with zero-length or truncated files.

## Syntax Sugar for Temporary Files

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

## Atomic Vars

`AtomicVar` is a simple zero-dependency thread-safe variable that works for any type.
It simply combines a value with reentrant lock (`threading.RLock`) to make thread-safe
use of the variable less error prone.

Often the standard "Pythonic" approach is to use locks directly, but for some common use
cases, `AtomicVar` may be simpler and more readable.
Works on any type, including lists and dicts.

Other options include `threading.Event` (for shared booleans), `threading.Queue` (for
producer-consumer queues), and `multiprocessing.Value` (for process-safe primitives).

Examples:

```python
# Immutable types are always safe:
count = AtomicVar(0)
count.update(lambda x: x + 5)  # In any thread.
count.set(0)  # In any thread.
current_count = count.value  # In any thread.

# Useful for flags:
global_flag = AtomicVar(False)
global_flag.set(True)  # In any thread.
if global_flag:  # In any thread.
    print("Flag is set")


# For mutable types,consider using `copy` or `deepcopy` to access the value:
my_list = AtomicVar([1, 2, 3])
my_list_copy = my_list.copy()  # In any thread.
my_list_deepcopy = my_list.deepcopy()  # In any thread.

# For mutable types, the `updates()` context manager gives a simple way to
# lock on updates:
with my_list.updates() as value:
    value.append(5)

# Or if you prefer, via a function:
my_list.update(lambda x: x.append(4))  # In any thread.

# You can also use the var's lock directly. In particular, this encapsulates
# locked one-time initialization:
initialized = AtomicVar(False)
with initialized.lock:
    if not initialized:  # checks truthiness of underlying value
        expensive_setup()
        initialized.set(True)

# Or:
lazy_var: AtomicVar[list[str] | None] = AtomicVar(None)
with lazy_var.lock:
    if not lazy_var:
            lazy_var.set(expensive_calculation())
```

## Simple String Template

A validated template string that supports only specified fields.
Can subclass to have a type with a given set of `allowed_fields`. Provide a type with a
field name to allow validation of int/float format strings.

Examples:

```python
>>> t = StringTemplate("{name} is {age} years old", ["name", "age"])
>>> t.format(name="Alice", age=30)
'Alice is 30 years old'

>>> t = StringTemplate("{count:3d}@{price:.2f}", [("count", int), ("price", float)])
>>> t.format(count=10, price=19.99)
' 10@19.99'
```

## Multiple String Replacements

- **`insert_multiple(text: str, insertions: list[Insertion]) -> str`**

  Insert multiple strings into `text` at the given offsets, at once.

- **`replace_multiple(text: str, replacements: list[Replacement]) -> str`**

  Replace multiple substrings in `text` with new strings, simultaneously.
  The replacements are a list of tuples (start_offset, end_offset, new_string).

## FAQ

### Why bother, if it’s so short?

Because it saves time, saves you stupid bugs and clumsy repetition, and has zero (yes
zero) dependencies.

### Are there other libraries that offer these utilities?

A few yes.
Some support has improved in Python 3; for example `textwrap.shorten()` can be
used instead of `abbrev_str()` (that said, strif also offers `abbrev_list()`).

[boltons](https://github.com/mahmoud/boltons) is a much larger library of general
utilities. strif is intended to be much smaller.
The [atomicwrites](https://github.com/untitaker/python-atomicwrites) library is similar
to `atomic_output_file()` but is no longer maintained.
For some others like the base36 tools I haven't seen equivalents elsewhere.

If you don't want the dependency on strif, also feel free to just copy the bit you want!
They're short.

### Is it mature?

I’ve used many of these functions in production situations for years.
We don't have comprehensive tests currently.
But they're mostly so small you can inspect them yourself.

* * *

## Development

For how to install uv and Python, see [installation.md](installation.md).

For development workflows, see [development.md](development.md).

For instructions on publishing to PyPI, see [publishing.md](publishing.md).

* * *

*This project was built from
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
