---
type: is
id: is-01ks9qqxrfhpzjvq2q8v30fbcc
title: Delete unreachable abbreviate_str / abbreviate_list aliases
kind: chore
status: closed
priority: 3
version: 2
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:18:13.647Z
updated_at: 2026-05-23T06:29:55.710Z
closed_at: 2026-05-23T06:29:55.710Z
close_reason: null
---
src/strif/strif.py lines ~289-292 define deprecated aliases:
    abbreviate_str = abbrev_str
    abbreviate_list = abbrev_list
These are NOT in __all__ and are not re-exported from __init__.py, so they are unreachable via the public 'import strif' API. Only a caller doing 'from strif.strif import abbreviate_str' could reach them — extremely unlikely.

Action: delete both alias lines and their docstring comments.

This is an intentional breaking change for the (essentially nonexistent) population importing from the private submodule. Note it in the v3.1.0 release notes under a short 'Removed' note.

Acceptance criteria:
- Lines removed; abbrev_str/abbrev_list remain the canonical names.
- grep confirms no internal references to abbreviate_str/abbreviate_list.
- lint + pytest green.
