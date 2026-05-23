---
type: is
id: is-01ks9qszp2tkz3t34va9506jd7
title: "README: lead with atomic ops, add agent-use subsection"
kind: task
status: closed
priority: 2
version: 2
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:19:21.153Z
updated_at: 2026-05-23T06:29:57.332Z
closed_at: 2026-05-23T06:29:57.331Z
close_reason: null
---
Two README improvements identified in the senior review:

1. Reorder 'Key Features': atomic file operations are strif's main differentiator and the most agent-relevant capability (atomic writes for mid-stream output). Pull the atomic-ops bullet to the TOP of the Key Features list, ahead of the abbreviate/quote bullets. Identifiers/hashing next, then string utilities.

2. Add a short subsection (a few sentences + a tiny code block) titled something like 'Using strif with LLM agents' explaining the unique value for agent workflows:
   - atomic_output_file / atomic_write_text for safe partial-output writes (never leave corrupt files if a generation is interrupted).
   - content hashing (hash_file/hash_string) for cheap caching / dedup keys.
   - timestamped/base36 ids for run logs.

Also fold in references to the new helpers from this release (atomic_write_text/bytes) once those land, and the named Insertion/Replacement fields.

Dependency: best done AFTER the API beads (atomic_write_*, NamedTuple) so the examples reference the final API.

Acceptance criteria:
- atomic ops appear first in Key Features.
- New agent-use subsection present and accurate.
- Doc links still valid; codespell (part of lint) passes on README.
- lint green.
