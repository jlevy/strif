# Development

## Setting Up uv

This project is set up to use [uv](https://docs.astral.sh/uv/) to manage Python and
dependencies. First, be sure you
[have uv installed](https://docs.astral.sh/uv/getting-started/installation/)..

Then [fork](https://github.com/jlevy/strif/fork) this repo (having your own fork will
make it easier to contribute) and
[clone it](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

## Basic Developer Workflows

The `Makefile` simply offers shortcuts to `uv` commands for developer convenience.
(For clarity, GitHub Actions don't use the Makefile and just call `uv` directly.)

```shell
# First, install all dependencies and set up your virtual environment.
# This simply runs `uv sync --all-extras --dev` to install all packages,
# including dev dependencies and optional dependencies.
make install

# Run uv sync, lint, and test:
make

# Build wheel:
make build

# Linting:
make lint

# Run tests:
make test

# Delete all the build artifacts:
make clean

# Upgrade dependencies to compatible versions:
make upgrade

# To run tests by hand:
uv run pytest   # all tests
uv run pytest -s src/module/some_file.py  # one test, showing outputs

# Build and install current dev executables, to let you use your dev copies
# as local tools:
uv tool install --editable .

# Dependency management directly with uv:
# Add a new dependency:
uv add package_name
# Add a development dependency:
uv add --dev package_name
# Update to latest compatible versions (including dependencies on git repos):
uv sync --upgrade
# Update a specific package:
uv lock --upgrade-package package_name
# Update dependencies on a package:
uv add package_name@latest

# Run a shell within the Python environment:
uv venv
source .venv/bin/activate
```

See [uv docs](https://docs.astral.sh/uv/) for details.

## Release Process

This project is set up to publish to [PyPI](https://pypi.org/) from GitHub Actions.

Thanks to [the dynamic versioning
plugin](https://github.com/ninoseki/uv-dynamic-versioning/) and the
[`publish.yml` workflow](.github/workflows/publish.yml), you can simply create tagged
releases (using standard format for the tag name, e.g. `v0.1.0`) on GitHub and the tag
will trigger a release build, which then uploads it to PyPI.

For this to work you will need to have a PyPI account and authorize your repository to
publish to PyPI. The simplest way to do that is on [the publishing settings
page](https://pypi.org/manage/account/publishing/). Configure "Trusted Publisher
Management" and register your GitHub repo as a new "pending" trusted publisher, entering
the project name, repo owner, repo name, and `publish.yml` as the workflow name.

* * *

*This file was built with
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv).*
