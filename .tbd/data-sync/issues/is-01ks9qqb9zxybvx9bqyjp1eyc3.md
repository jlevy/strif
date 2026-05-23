---
type: is
id: is-01ks9qqb9zxybvx9bqyjp1eyc3
title: Expose __version__ on the strif package
kind: feature
status: closed
priority: 2
version: 2
labels: []
dependencies: []
parent_id: is-01ks9qpwke3tyatft5y2bzrb58
created_at: 2026-05-23T06:17:54.751Z
updated_at: 2026-05-23T06:29:54.978Z
closed_at: 2026-05-23T06:29:54.978Z
close_reason: null
---
Add a runtime __version__ attribute to the top-level package. Humans and agents routinely reach for strif.__version__; it currently does not exist.

Implementation (src/strif/__init__.py):
    from importlib.metadata import version, PackageNotFoundError
    try:
        __version__ = version('strif')
    except PackageNotFoundError:
        __version__ = '0.0.0.dev0'  # not installed (e.g. running from source tree without install)
Add '__version__' to __all__.

Note: versioning is dynamic (uv-dynamic-versioning from git tags), so do NOT hardcode a number. importlib.metadata reads the installed dist metadata.

Acceptance criteria:
- import strif; strif.__version__ returns the installed version string.
- Works when installed from PyPI/wheel; degrades gracefully (no crash) when imported from a source checkout that isn't installed.
- Test: assert strif.__version__ is a non-empty str.
- lint + pytest green.
