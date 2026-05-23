---
type: is
id: is-01ks9qscq9jsafgj6sfg4981hy
title: Bump softprops/action-gh-release v2.6.2 -> v3.0.0 (Node 20 deprecation)
kind: chore
status: open
priority: 1
version: 1
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:19:01.736Z
updated_at: 2026-05-23T06:19:01.736Z
---
The v3.0.2 publish run emitted: 'Node.js 20 actions are deprecated ... softprops/action-gh-release@<sha>. Actions will be forced to run with Node.js 24 by default starting June 2nd, 2026.' Our pinned v2.6.2 runs on Node 20. v3.0.0 of the action runs on Node 24.

Action: in .github/workflows/publish.yml, bump the SHA-pinned softprops/action-gh-release to v3.0.0. Keep SHA-pinning (this is a single-maintainer third-party action). Resolve the v3.0.0 commit SHA:
    gh api repos/softprops/action-gh-release/git/ref/tags/v3.0.0 --jq '.object.sha'
Update both the SHA and the trailing '# v3.0.0' comment. Review the v3.0.0 release notes for any breaking input changes (generate_release_notes / prerelease inputs should be unchanged, but verify).

Time-sensitive: deadline June 2, 2026.

Acceptance criteria:
- publish.yml uses softprops/action-gh-release@<v3.0.0-sha> # v3.0.0.
- No deprecation warning on the next release run.
- Inputs (generate_release_notes, prerelease) still valid for v3.0.0.
