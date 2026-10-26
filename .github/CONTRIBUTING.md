# Contributing

## Running tests

Use [tox](https://tox.wiki/) from the repository root. It creates an isolated
environment and installs the project and its test dependencies:

```sh
python -m pip install tox
tox -e py
```

Pass pytest arguments after `--` to run a single file or tests matching a name:

```sh
tox -e py -- tests/test_number.py
tox -e py -- tests/test_number.py -k intcomma
```

Some localisation tests are skipped when compiled `.mo` translation files are missing.
Generate them with `scripts/generate-translation-binaries.sh`, which requires Bash and
GNU gettext's `msgfmt`. Translation-update tests also require `xgettext` and `msgmerge`.
Use `tox -e py -- -rs` to see skip reasons.

CI generates translation binaries and runs the
[configured tox environments](../tox.ini). See the [test workflow](workflows/test.yml)
for supported Python versions and platforms.

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
