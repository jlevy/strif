---
type: is
id: is-01ks9qrq23rf2w7c4v4dchgb2z
title: Add new_uid length/bits math test
kind: task
status: open
priority: 3
version: 1
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:18:39.555Z
updated_at: 2026-05-23T06:18:39.555Z
---
new_uid(bits) computes length = int(bits/5.16)+1 over a 36-char alphabet. Untested. Add a small deterministic test.

Cover:
- new_uid() returns only chars from [0-9a-z].
- Length scales with bits: e.g. len(new_uid(64)) > len(new_uid(32)); and length matches int(bits/5.16)+1 for a couple of values.
- new_timestamped_uid() starts with a timestamp-like prefix and contains the random suffix; sorts in time order for two sequentially-created ids (the documented benefit). Keep it robust (don't assert exact timestamps).
- Optional: statistical sanity that two calls differ.

Acceptance criteria:
- Test added (tests/test_ids.py or fold into existing).
- No flaky timing assertions.
- lint + pytest green.
