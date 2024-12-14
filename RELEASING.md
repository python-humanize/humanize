# Release checklist

- [ ] Get `main` to the appropriate code release state.
      [GitHub Actions](https://github.com/python-humanize/humanize/actions) should be
      running cleanly for all merges to `main`.
      [![GitHub Actions status](https://github.com/python-humanize/humanize/workflows/Test/badge.svg)](https://github.com/python-humanize/humanize/actions)

- [ ] Edit release draft, adjust text if needed:
      https://github.com/python-humanize/humanize/releases

- [ ] Check next tag is correct, amend if needed

- [ ] Publish release

- [ ] Check the tagged
      [GitHub Actions build](https://github.com/python-humanize/humanize/actions/workflows/release.yml)
      has released to [PyPI](https://pypi.org/project/humanize/#history)

- [ ] Check installation:

```bash
pip3 uninstall -y humanize && pip3 install -U humanize && python3 -c "import humanize; print(humanize.__version__)"
```
