---
type: is
id: is-01ks9qrphymbwr42npfr0b3esg
title: Add AtomicVar test suite (incl. concurrency)
kind: task
status: closed
priority: 2
version: 2
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:18:39.038Z
updated_at: 2026-05-23T06:29:55.941Z
closed_at: 2026-05-23T06:29:55.941Z
close_reason: null
---
src/strif/atomic_var.py (AtomicVar) currently has ZERO tests. This is the biggest coverage gap. Add tests/test_atomic_var.py.

Cover:
- Construction + .value for immutable (int, str) and mutable (list, dict) types.
- set(), swap() returns old value, update() with a returning func and with an in-place func (returns None).
- updates() context manager yields the value and locks; raises ValueError when used on an immutable value (is_immutable guard).
- copy() and deepcopy() return independent copies (mutating the copy doesn't change the var).
- __bool__ reflects underlying truthiness; __repr__/__str__.
- is_immutable inference via value_is_immutable for common types and a frozen dataclass (True) vs a list (False); explicit is_immutable override.
- Concurrency: spin up ~10 threads each calling update(lambda x: x+1) N times on AtomicVar(0); after join, value == 10*N (proves the lock serializes RMW). Use threading + a barrier or just joins. Keep it deterministic and fast (small N).

Acceptance criteria:
- New tests/test_atomic_var.py, function-style like the other test files.
- Includes at least one real concurrency test that would fail without the lock.
- lint + pytest green.
