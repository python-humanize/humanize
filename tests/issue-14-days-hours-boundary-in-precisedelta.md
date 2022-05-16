# Days / hours boundary in `precisedelta`

When a `timedelta` is described by `precisedelta`, it
is aimed to be as human as possible.

```python
>>> import humanize
>>> import datetime

>>> humanize.precisedelta(datetime.timedelta(days=31))
'1 month and 12 hours'

>>> humanize.precisedelta(datetime.timedelta(days=62))
'2 months and 1 day'

>>> humanize.precisedelta(datetime.timedelta(days=92))
'3 months and 12 hours'

>>> humanize.precisedelta(datetime.timedelta(days=32))
'1 month, 1 day and 12 hours'
```

Setting a minimum unit forces us to use fractional value for the latest
unit, in this case, `days`:

```python
>>> humanize.precisedelta(datetime.timedelta(days=31), minimum_unit='days')
'1 month and 0.50 days'

>>> humanize.precisedelta(datetime.timedelta(days=62), minimum_unit='days')
'2 months and 1 day'

>>> humanize.precisedelta(datetime.timedelta(days=92), minimum_unit='days')
'3 months and 0.50 days'

>>> humanize.precisedelta(datetime.timedelta(days=32), minimum_unit='days')
'1 month and 1.50 days'
```

The `format` controls how this fractional (latest) value is formatted.
Using an integer representation like `'%d'` may yield unexpected results
as things like `0.50 days` are cast to `0 days` during the formatting:

```python
>>> humanize.precisedelta(datetime.timedelta(days=31), minimum_unit='days', format='%d')
'1 month and 0 days'

>>> humanize.precisedelta(datetime.timedelta(days=62), minimum_unit='days', format='%d')
'2 months and 1 day'

>>> humanize.precisedelta(datetime.timedelta(days=92), minimum_unit='days', format='%d')
'3 months and 0 days'

>>> humanize.precisedelta(datetime.timedelta(days=32), minimum_unit='days', format='%d')
'1 month and 1 days'
```

`precisedelta` accepts a `truncate` flag to truncate and drop values too
close to zero.

```python
>>> humanize.precisedelta(datetime.timedelta(days=31), minimum_unit='days', format='%d', truncate=True)
'1 month'

>>> humanize.precisedelta(datetime.timedelta(days=62), minimum_unit='days', format='%d', truncate=True)
'2 months and 1 day'

>>> humanize.precisedelta(datetime.timedelta(days=92), minimum_unit='days', format='%d', truncate=True)
'3 months'

>>> humanize.precisedelta(datetime.timedelta(days=32), minimum_unit='days', format='%d', truncate=True)
'1 month and 1 days'
```

Notice the `truncate=True` does not imply `format='%d'` as fractional
numbers are still possible and `format` still apply:

```python
>>> humanize.precisedelta(datetime.timedelta(days=31), minimum_unit='days', truncate=True)
'1 month'

>>> humanize.precisedelta(datetime.timedelta(days=62), minimum_unit='days', truncate=True)
'2 months and 1 day'

>>> humanize.precisedelta(datetime.timedelta(days=92), minimum_unit='days', truncate=True)
'3 months'

>>> humanize.precisedelta(datetime.timedelta(days=32), minimum_unit='days', truncate=True)
'1 month and 1.50 days'
```

## References

See [issue 14](https://github.com/python-humanize/humanize/issues/14)
