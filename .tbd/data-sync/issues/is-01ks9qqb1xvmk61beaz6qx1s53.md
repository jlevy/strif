---
type: is
id: is-01ks9qqb1xvmk61beaz6qx1s53
title: Add atomic_write_text() and atomic_write_bytes() helpers
kind: feature
status: closed
priority: 2
version: 3
labels: []
dependencies:
  - type: blocks
    target: is-01ks9qszp2tkz3t34va9506jd7
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:17:54.492Z
updated_at: 2026-05-23T06:29:54.739Z
closed_at: 2026-05-23T06:29:54.738Z
close_reason: null
---
Add two convenience wrappers around atomic_output_file() so the common 'write a whole string/bytes atomically' case is one call instead of nested with-blocks.

Motivation: agents writing files mid-stream are the prime use case for atomic writes. Today that requires:
    with atomic_output_file(path) as tmp:
        with open(tmp, 'w') as f:
            f.write(content)
Two nested context managers per write is noisy for LLMs.

Implement in src/strif/strif.py:
    def atomic_write_text(dest_path, text, *, make_parents=False, backup_suffix=None, encoding='utf-8') -> None
    def atomic_write_bytes(dest_path, data, *, make_parents=False, backup_suffix=None) -> None
Both delegate to atomic_output_file() and write via Path.write_text/write_bytes on the temp path. Forward make_parents/backup_suffix.

Acceptance criteria:
- Both added to __all__ in strif.py AND src/strif/__init__.py.
- Docstrings with a one-line summary + short example.
- Tests: round-trip text and bytes; make_parents=True creates dirs; backup_suffix keeps a backup; exception path leaves no partial in final location (reuse atomic_output_file guarantees).
- README mentions them in the atomic-ops section.
- lint + pytest green.
