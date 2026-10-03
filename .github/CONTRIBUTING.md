# Contributing

## Running tests

Use Python 3.10 or newer. From the repository root, create a virtual environment:

```sh
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on Linux or macOS, or
`.venv\Scripts\Activate.ps1` in Windows PowerShell. Then install the project and
its test dependencies:

```sh
python -m pip install -e ".[tests]"
```

Run the full suite, a single file, or tests matching a name:

```sh
python -m pytest
python -m pytest tests/test_number.py
python -m pytest tests/test_number.py -k intcomma
```

Some localisation tests are skipped when compiled `.mo` translation files are
missing. Generate them with `scripts/generate-translation-binaries.sh`, which
requires Bash and GNU gettext's `msgfmt`. Translation-update tests also require
`xgettext` and `msgmerge`. Use `python -m pytest -rs` to see skip reasons.

CI generates translation binaries and runs tests through [tox](../tox.ini).
See the [test workflow](workflows/test.yml) for supported Python versions and
platforms.

## Linting

Linting is run on the CI using [prek](https://prek.j178.dev//), and can be run locally:

```sh
pip install prek
prek install  # optional: to run when you commit, on just the staged changes
prek run --all-files  # to run on all files now
```

## Docstrings

Follow
[Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
for docstrings.

## Localization

See [README](https://github.com/python-humanize/humanize#localization).
