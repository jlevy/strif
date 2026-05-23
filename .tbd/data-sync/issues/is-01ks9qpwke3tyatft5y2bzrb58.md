---
type: is
id: is-01ks9qpwke3tyatft5y2bzrb58
title: "v3.1.0: agent-friendly API, test coverage, and tooling refresh"
kind: epic
status: closed
priority: 1
version: 15
labels: []
dependencies: []
child_order_hints:
  - is-01ks9qqb1xvmk61beaz6qx1s53
  - is-01ks9qqb9zxybvx9bqyjp1eyc3
  - is-01ks9qqx23sbgwdes8jc9jggah
  - is-01ks9qqxf2p91fdk4e840862fp
  - is-01ks9qqxrfhpzjvq2q8v30fbcc
  - is-01ks9qrphymbwr42npfr0b3esg
  - is-01ks9qrpt40jhpd378rt971358
  - is-01ks9qrq23rf2w7c4v4dchgb2z
  - is-01ks9qrqa21qrnvvpe91d26yw6
  - is-01ks9qscq9jsafgj6sfg4981hy
  - is-01ks9qsczpppzcyq6hdge3g55t
  - is-01ks9qsd85d8tr84krx5dc6s22
  - is-01ks9qszp2tkz3t34va9506jd7
created_at: 2026-05-23T06:17:39.693Z
updated_at: 2026-05-23T21:03:52.747Z
closed_at: 2026-05-23T21:03:52.747Z
close_reason: null
---
Next minor release (v3.1.0) for strif. Groups three themes:

1. Agent-friendly API additions (atomic_write_text/bytes, __version__, NamedTuple aliases, Literal hash algorithm types) — make the most-used surfaces easier for LLM agents and IDEs to call correctly.
2. Test coverage for the gaps remaining after v3.0.2 (AtomicVar has zero tests; hash_file chunked path, new_uid math, and the {timestamp} backup edge case are untested).
3. Tooling refresh (Node 20 deprecation on action-gh-release, setup-uv v8, Windows+macOS CI matrix).

NOTE on prior work: v3.0.2 already added tests/test_files.py covering atomic_output_file (happy/exception/backup_suffix/make_parents/target-is-dir/force) and temp_output_file (fd-leak/double-close). Do NOT recreate those. Remaining test work is tracked in the child beads.

Backward compatibility: strif is a published library. Changes that touch public API (NamedTuple, Literal types, deleting aliases) must preserve runtime behavior for existing callers where reasonable; deleting the abbreviate_* aliases is an intentional breaking change (they were already unreachable from the public __init__ export). Strif stays zero-runtime-dependency.

All child beads should be implemented, tested (uv run pytest), and linted (uv run python devtools/lint.py) before the release is tagged. Release mechanics: tag v3.1.0 -> publish.yml auto-publishes to PyPI + creates GitHub Release.
