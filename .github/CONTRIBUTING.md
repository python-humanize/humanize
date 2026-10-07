# Contributing

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

## Testing

When contributing bug fixes or new features, add unit tests to verify the
behavior and prevent regressions.

### 1. Locate the relevant test file

Test files live in the `tests/` directory and mirror the modules in
`src/humanize/`:

- `tests/test_number.py` for number formatting (`intcomma`, `clamp`, `ordinal`,
  etc.)
- `tests/test_time.py` for time utilities (`naturaltime`, `naturaldelta`,
  `naturaldate`, etc.)
- `tests/test_filesize.py` for file size formatting (`naturalsize`)
- `tests/test_lists.py` for list formatting (`natural_list`)
- `tests/test_i18n.py` for internationalization and locale translations

### 2. Follow existing test patterns and use parameterization

Follow `pytest` conventions and use `@pytest.mark.parametrize` when testing
multiple inputs or boundary conditions.

For example, when testing boundary behavior such as `humanize.clamp()`:

```python
@pytest.mark.parametrize(
    ("value", "format", "floor", "ceil", "expected"),
    [
        (5, "%s", 0, 10, "5"),
        (-1, "%s", 0, 10, "0"),
        (15, "%s", 0, 10, "10"),
    ],
)
def test_clamp_boundaries(value, format, floor, ceil, expected):
    assert humanize.clamp(value, format=format, floor=floor, ceil=ceil) == expected
```

### 3. Run focused tests locally

Run only the relevant test file or specific test case while developing:

```sh
pytest tests/test_number.py
pytest tests/test_number.py -k test_clamp
```

### 4. Verify that the test catches regressions

Before finalizing your changes, intentionally introduce a defect or temporarily
revert your implementation to verify that the new test fails. This confirms that
the test actively protects against regressions rather than passing vacuously.

### 5. Run the full test suite

Run the complete test suite locally before opening a pull request:

```sh
pytest
```

Or using `tox` across supported environments:

```sh
tox
```

## Localization

See [README](https://github.com/python-humanize/humanize#localization).
