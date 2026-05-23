from importlib.metadata import PackageNotFoundError, version

__all__ = (  # noqa: F405
    "__version__",
    # atomic_var.py
    "AtomicVar",
    # strif.py
    "DEV_NULL",
    "iso_timestamp",
    "format_iso_timestamp",
    "new_uid",
    "new_timestamped_uid",
    "clean_alphanum",
    "clean_alphanum_hash",
    "file_mtime_hash",
    "base36_encode",
    "HashAlgorithm",
    "Hash",
    "hash_string",
    "hash_file",
    "abbrev_str",
    "abbrev_list",
    "single_line",
    "is_quotable",
    "quote_if_needed",
    "is_truthy",
    "move_to_backup",
    "copy_to_backup",
    "move_file",
    "make_parent_dirs",
    "atomic_output_file",
    "atomic_write_text",
    "atomic_write_bytes",
    "temp_output_file",
    "temp_output_dir",
    "copyfile_atomic",
    "copytree_atomic",
    "rmtree_or_file",
    "chmod_native",
    "lenb",
    # string_replace.py
    "Insertion",
    "Replacement",
    "insert_multiple",
    "replace_multiple",
    # string_template.py
    "StringTemplate",
)

try:
    __version__ = version("strif")
except PackageNotFoundError:
    # Running from a source tree that isn't installed.
    __version__ = "0.0.0.dev0"

from .atomic_var import *  # noqa: F403, E402
from .strif import *  # noqa: F403, E402
from .string_replace import *  # noqa: F403, E402
from .string_template import *  # noqa: F403, E402
