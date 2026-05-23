---
type: is
id: is-01ks9qsd85d8tr84krx5dc6s22
title: Add Windows and macOS to the CI matrix
kind: task
status: open
priority: 2
version: 1
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:19:02.277Z
updated_at: 2026-05-23T06:19:02.277Z
---
CI currently runs ubuntu-latest only. strif is a FILE-operations library and os.replace / atomic-rename semantics differ on Windows (renaming/replacing an open or locked file behaves differently than POSIX). This is exactly the kind of library where cross-OS CI catches real bugs.

Action: in .github/workflows/ci.yml, expand the matrix os to ['ubuntu-latest', 'macos-latest', 'windows-latest']. Keep the python-version matrix. Consider 'fail-fast: false' so one OS failing doesn't cancel the others.

Expect possible failures to surface (and fix) on Windows:
- The /proc/self/fd FD-leak test is Linux-only (already guarded with skipif) — confirm it skips cleanly on win/mac.
- atomic_output_file replace-over-existing and force-replaces-dir paths may behave differently on Windows (file locking). If genuine failures appear, capture them as new bugs (separate beads) rather than weakening tests.
- chmod_native is POSIX-only (shells out to chmod) — it has no tests today, but if any get added they must skip on Windows.

Acceptance criteria:
- 3-OS x N-python matrix runs.
- Any newly-revealed real bugs are filed as child bugs of the v3.1.0 epic, not papered over.
- If a Windows-specific issue is too deep for this release, document it and keep Windows non-blocking (continue-on-error) with a tracking bead — decide with the maintainer.
