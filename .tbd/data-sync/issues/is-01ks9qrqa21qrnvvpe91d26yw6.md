---
type: is
id: is-01ks9qrqa21qrnvvpe91d26yw6
title: Add atomic_output_file {timestamp} backup test (remaining gap)
kind: task
status: open
priority: 3
version: 1
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:18:39.810Z
updated_at: 2026-05-23T06:18:39.810Z
---
v3.0.2 added atomic_output_file tests for backup_suffix='.bak' (fixed suffix). The {timestamp} variant — which expands to a unique timestamped suffix allowing infinitely many backups — is still untested.

Add a test that:
- Pre-creates a target file with content A.
- Writes new content B via atomic_output_file(target, backup_suffix='{timestamp}.bak').
- Asserts target now has B, and exactly one backup file matching the glob 'target*{,.}bak' exists with content A.
- Optionally: a second write produces a SECOND distinct backup (proving {timestamp} doesn't clobber the first). Beware: timestamps must differ — new_timestamped_uid includes random bits so suffixes should differ even within the same second; assert two backups exist.

Put in tests/test_files.py alongside the existing atomic_output_file tests.

Acceptance criteria:
- {timestamp} expansion produces unique backups (no clobber).
- lint + pytest green.
