---
type: is
id: is-01ks9qqx23sbgwdes8jc9jggah
title: Convert Insertion and Replacement to NamedTuple
kind: feature
status: open
priority: 2
version: 2
labels: []
dependencies:
  - type: blocks
    target: is-01ks9qszp2tkz3t34va9506jd7
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:18:12.931Z
updated_at: 2026-05-23T06:19:26.580Z
---
In src/strif/string_replace.py, Insertion = tuple[int, str] and Replacement = tuple[int, int, str] are anonymous tuples. Anonymous positional tuples are hard for agents/IDEs to call correctly ((5, 10, 'x') gives no hint which int is start vs end). Convert to typing.NamedTuple with named fields.

    class Insertion(NamedTuple):
        offset: int
        text: str

    class Replacement(NamedTuple):
        start: int
        end: int
        text: str

Backward compatibility: NamedTuple is a subclass of tuple, so positional construction (Insertion(5, ',')), unpacking (start, end, txt = r), and indexing (r[0]) all keep working. insert_multiple/replace_multiple internals that sort by x[0] still work. This is a non-breaking change at runtime.

Acceptance criteria:
- Both converted to NamedTuple, fields named as above.
- Existing tests in tests/test_string_replace.py still pass unchanged (they use positional tuples).
- Add a test that constructs via named fields and via positional, and confirms unpacking still works.
- Update the README 'Multiple String Replacements' section to show the named fields.
- basedpyright clean (the type aliases were exported in __all__; keep them exported).
- lint + pytest green.
