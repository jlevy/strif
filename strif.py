"""
Strif is a tiny (<1000 loc) library of string- and file-related utilities for Python 2.7 and 3.

More information: https://github.com/jlevy/strif
"""

from string import Template
import re
import os
import errno
import random
import shutil
import shlex
import pipes
import tempfile
import hashlib
import codecs
from contextlib import contextmanager
from datetime import datetime

__author__ = 'jlevy'

VERSION = "0.2.2"
DESCRIPTION = "Tiny, useful lib for strings and files"
LONG_DESCRIPTION = __doc__

# The subprocess module has known threading issues, so prefer subprocess32.
try:
  import subprocess32 as subprocess
except ImportError:
  import subprocess

# A pre-opened handle to /dev/null.
DEV_NULL = open(os.devnull, 'wb')

BACKUP_SUFFIX = ".bak"

_RANDOM = random.SystemRandom()
_RANDOM.seed()


def dict_merge(*dict_list):
  """
  Given zero or more dicts, shallow copy and merge them into a new dict, with
  precedence to dictionary values later in the dict list.
  """
  result = {}
  for d in dict_list:
    result.update(d)
  return result


#
# ---- Identifiers and abbreviations ----

def new_uid(bits=64):
  """
  A random alphanumeric value with at least the specified bits of randomness. We use base 36,
  i.e. not case sensitive. Note this makes it suitable for filenames even on case-insensitive disks.
  """
  return "".join(_RANDOM.sample("0123456789abcdefghijklmnopqrstuvwxyz",
                                int(bits / 5.16) + 1))  # log(26 + 10)/log(2) = 5.16


def iso_timestamp():
  """
  ISO timestamp. With the Z for usual clarity.
  Example: 2015-09-12T08:41:12.397217Z
  """
  return datetime.now().isoformat() + 'Z'


def new_timestamped_uid(bits=32):
  """
  A unique id that begins with an ISO timestamp followed by fractions of seconds and bits of
  randomness. The advantage of this is it sorts nicely by time, while still being unique.
  Example: 20150912T084555Z-378465-43vtwbx
  """
  return "%s-%s" % (re.sub('[^\w.]', '', datetime.now().isoformat()).replace(".", "Z-"), new_uid(bits))


def abbreviate_str(string, max_len=80, indicator="..."):
  """
  Abbreviate a string, adding an indicator like an ellipsis if required.
  """
  if not string or not max_len or len(string) <= max_len:
    return string
  elif max_len <= len(indicator):
    return string[0:max_len]
  else:
    return string[0:max_len - len(indicator)] + indicator


def abbreviate_list(items, max_items=10, item_max_len=40, joiner=", ", indicator="..."):
  """
  Abbreviate a list, truncating each element and adding an indicator at the end if the
  whole list was truncated. Set item_max_len to None or 0 not to truncate items.
  """
  if not items:
    return items
  else:
    shortened = [abbreviate_str("%s" % item, max_len=item_max_len) for item in items[0:max_items]]
    if len(items) > max_items:
      shortened.append(indicator)
    return joiner.join(shortened)


#
# ---- Templating ----

def expand_variables(template_str, value_map, transformer=None):
  """
  Expand a template string like "blah blah $FOO blah" using given value mapping.
  """
  if template_str is None:
    return None
  else:
    if transformer is None:
      transformer = lambda v: v
    try:
      # Don't bother iterating items for Python 2+3 compatibility.
      transformed_value_map = {k: transformer(value_map[k]) for k in value_map}
      return Template(template_str).substitute(transformed_value_map)
    except Exception as e:
      raise ValueError("could not expand variable names in command '%s': %s" % (template_str, e))


def shell_expand_variables(template_str, value_map):
  """
  Expand a shell template string like "cp $SOURCE $TARGET/blah", also quoting values as needed
  to ensure shell safety.
  """
  return expand_variables(template_str, value_map, transformer=pipes.quote)


def shell_expand_to_popen(template, values):
  """
  Expand a template like "cp $SOURCE $TARGET/blah" into a list of popen arguments.
  """
  return [expand_variables(item, values) for item in shlex.split(template)]


#
# ---- File operations ----

def move_to_backup(path, backup_suffix=BACKUP_SUFFIX):
  """
  Move the given file or directory to the same name, with a backup suffix.
  If backup_suffix not supplied, move it to the extension ".bak".
  NB: If backup_suffix is supplied and is None, don't do anything.
  """
  if backup_suffix and os.path.exists(path):
    backup_path = path + backup_suffix
    # Some messy corner cases need to be handled for existing backups.
    # TODO: Note if this is a directory, and we do this twice at once, there is a potential race
    # that could leave one backup inside the other.
    if os.path.islink(backup_path):
      os.unlink(backup_path)
    elif os.path.isdir(backup_path):
      shutil.rmtree(backup_path)
    shutil.move(path, backup_path)


def make_all_dirs(path, mode=0o777):
  """
  Ensure local dir, with all its parent dirs, are created.
  Unlike os.makedirs(), will not fail if the path already exists.
  """
  # Avoid races inherent to doing this in two steps (check then create).
  # Python 3 has exist_ok but the approach below works for Python 2+3.
  # https://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
  try:
    os.makedirs(path, mode=mode)
  except OSError as e:
    if e.errno == errno.EEXIST and os.path.isdir(path):
      pass
    else:
      raise
  return path


def make_parent_dirs(path, mode=0o777):
  """
  Ensure parent directories of a file are created as needed.
  """
  parent = os.path.dirname(path)
  if parent:
    make_all_dirs(parent, mode)
  return path


@contextmanager
def atomic_output_file(dest_path, make_parents=False, backup_suffix=None, suffix=".partial.%s"):
  """
  A context manager for convenience in writing a file or directory in an atomic way. Set up
  a temporary name, then rename it after the operation is done, optionally making a backup of
  the previous file or directory, if present.
  """
  if dest_path == os.devnull:
    # Handle the (probably rare) case of writing to /dev/null.
    yield dest_path
  else:
    tmp_path = ("%s" + suffix) % (dest_path, new_uid())
    if make_parents:
      make_parent_dirs(tmp_path)

    yield tmp_path

    # Note this is not in a finally block, so that result won't be renamed to final location
    # in case of abnormal exit.
    if not os.path.exists(tmp_path):
      raise IOError("failure in writing file '%s': target file '%s' missing" % (dest_path, tmp_path))
    if backup_suffix:
      move_to_backup(dest_path, backup_suffix=backup_suffix)
    # If the target already exists, and is a directory, it has to be removed.
    if os.path.isdir(dest_path):
      shutil.rmtree(dest_path)
    shutil.move(tmp_path, dest_path)


def temp_output_file(prefix="tmp", suffix="", dir=None, make_parents=False, always_clean=False):
  """
  A context manager for convenience in creating a temporary file,
  which is deleted when exiting the context.

  Usage:
    with temp_output_file() as (fd, path):
      ...
  """
  return _temp_output(False, prefix=prefix, suffix=suffix, dir=dir, make_parents=make_parents,
                      always_clean=always_clean)


def temp_output_dir(prefix="tmp", suffix="", dir=None, make_parents=False, always_clean=False):
  """
  A context manager for convenience in creating a temporary directory,
  which is deleted when exiting the context.

  Usage:
    with temp_output_dir() as dirname:
      ...
  """
  return _temp_output(True, prefix=prefix, suffix=suffix, dir=dir, make_parents=make_parents,
                      always_clean=always_clean)


@contextmanager
def _temp_output(is_dir, prefix="tmp", suffix="", dir=None, make_parents=False, always_clean=False):
  if dir and make_parents:
    make_all_dirs(dir)

  if is_dir:
    path = tempfile.mkdtemp(prefix=prefix, suffix=suffix, dir=dir)
    result = path
  else:
    (fd, path) = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=dir)
    result = (fd, path)

  def clean():
    try:
      rmtree_or_file(path, ignore_errors=True)
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


def read_string_from_file(path, encoding="utf8"):
  """
  Read entire contents of file into a string.
  """
  with codecs.open(path, "rb", encoding=encoding) as f:
    value = f.read()
  return value


def write_string_to_file(path, string, make_parents=False, backup_suffix=BACKUP_SUFFIX, encoding="utf8"):
  """
  Write entire file with given string contents, atomically. Keeps backup by default.
  """
  with atomic_output_file(path, make_parents=make_parents, backup_suffix=backup_suffix) as tmp_path:
    with codecs.open(tmp_path, "wb", encoding=encoding) as f:
      f.write(string)


def set_file_mtime(path, mtime, atime=None):
  """Set access and modification times on a file."""
  if not atime:
    atime = mtime
  f = open(path, 'a')
  try:
    os.utime(path, (atime, mtime))
  finally:
    f.close()


def copyfile_atomic(source_path, dest_path, make_parents=False, backup_suffix=None):
  """
  Copy file on local filesystem in an atomic way, so partial copies never exist. Preserves timestamps.
  """
  with atomic_output_file(dest_path, make_parents=make_parents, backup_suffix=backup_suffix) as tmp_path:
    shutil.copyfile(source_path, tmp_path)
    set_file_mtime(tmp_path, os.path.getmtime(source_path))


def copytree_atomic(source_path, dest_path, make_parents=False, backup_suffix=None, symlinks=False):
  """
  Copy a file or directory recursively, and atomically, reanaming file or top-level dir when done.
  Unlike shutil.copytree, this will not fail on a file.
  """
  if os.path.isdir(source_path):
    with atomic_output_file(dest_path, make_parents=make_parents, backup_suffix=backup_suffix) as tmp_path:
      shutil.copytree(source_path, tmp_path, symlinks=symlinks)
  else:
    copyfile_atomic(source_path, dest_path, make_parents=make_parents, backup_suffix=backup_suffix)


def movefile(source_path, dest_path, make_parents=False, backup_suffix=None):
  """
  Move file. With a few extra options.
  """
  if make_parents:
    make_parent_dirs(dest_path)
  move_to_backup(dest_path, backup_suffix=backup_suffix)
  shutil.move(source_path, dest_path)


def rmtree_or_file(path, ignore_errors=False, onerror=None):
  """
  rmtree fails on files or symlinks. This removes the target, whatever it is.
  """
  # TODO: Could add an rsync-based delete, as in
  # https://github.com/vivlabs/instaclone/blob/master/instaclone/instaclone.py#L127-L143
  if ignore_errors and not os.path.exists(path):
    return
  if os.path.isdir(path) and not os.path.islink(path):
    shutil.rmtree(path, ignore_errors=ignore_errors, onerror=onerror)
  else:
    os.unlink(path)


def chmod_native(path, mode_expression, recursive=False):
  """
  This is ugly and will only work on POSIX, but the built-in Python os.chmod support
  is very minimal, and neither supports fast recursive chmod nor "+X" type expressions,
  both of which are slow for large trees. So just shell out.
  """
  popenargs = ["chmod"]
  if recursive:
    popenargs.append("-R")
  popenargs.append(mode_expression)
  popenargs.append(path)
  subprocess.check_call(popenargs)


def file_sha1(path):
  """
  Compute SHA1 hash of a file.
  """
  sha1 = hashlib.sha1()
  with open(path, "rb") as f:
    while True:
      block = f.read(2 ** 10)
      if not block:
        break
      sha1.update(block)
    return sha1.hexdigest()
