---
type: is
id: is-01ks9qqxf2p91fdk4e840862fp
title: Add Literal type to hash algorithm parameters
kind: feature
status: open
priority: 3
version: 1
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:18:13.346Z
updated_at: 2026-05-23T06:18:13.346Z
---
hash_string() and hash_file() take algorithm: str. Narrow to a Literal of common algorithms for better autocomplete and agent correctness, while still allowing arbitrary strings hashlib supports.

In src/strif/strif.py define:
    HashAlgorithm = Literal['sha1', 'sha256', 'sha384', 'sha512', 'md5', 'blake2b', 'blake2s']
and type the params as: algorithm: HashAlgorithm | str = 'sha1'
(The | str keeps the escape hatch for any hashlib-supported name; the Literal drives IDE/agent autocomplete to the common set.)

Keep the existing runtime validation in hash_file (algorithm in hashlib.algorithms_available). Consider adding the same guard to hash_string for consistency (hashlib.new already raises ValueError, so this is optional — note it but don't over-engineer).

Acceptance criteria:
- HashAlgorithm exported in __all__ (strif.py and __init__.py).
- Default stays 'sha1' for backward compatibility (changing the default is deferred to a 4.0 major; do NOT change it here).
- Existing tests/test_hash.py passes.
- basedpyright clean.
- lint + pytest green.
