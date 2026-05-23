---
type: is
id: is-01ks9qsczpppzcyq6hdge3g55t
title: Bump astral-sh/setup-uv v7 -> v8
kind: chore
status: open
priority: 3
version: 1
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:19:02.006Z
updated_at: 2026-05-23T06:19:02.006Z
---
setup-uv latest is v8.x; we pin v7.6.0 in ci.yml and publish.yml. Not a security issue, just version drift. v8.0.0 introduced 'immutable releases and secure tags'.

Action: bump the SHA-pinned astral-sh/setup-uv to the latest v8.x in BOTH .github/workflows/ci.yml and .github/workflows/publish.yml. Resolve SHA:
    gh api repos/astral-sh/setup-uv/git/ref/tags/<v8.x> --jq '.object.sha'
Update SHA + '# v8.x' comment in both files. Review v8 changelog for breaking input changes (the 'version', 'enable-cache', 'python-version' inputs we use should be stable; verify).

Acceptance criteria:
- Both workflows reference setup-uv v8.x by SHA.
- CI green across the full matrix after the bump.
- Consider also bumping the pinned uv 'version' (currently 0.10.2) to a recent release if convenient — note but don't force.
