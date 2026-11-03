# Filesize

::: humanize.filesize

## Command line

Format a byte count with the `humanize` command or with `python -m humanize`:

```console
$ humanize naturalsize 8589934592
8.6 GB
$ humanize naturalsize --binary 8589934592
8.0 GiB
$ humanize naturalsize --gnu --format "%.2f" 8589934592
8.00G
```

With no positional value, one value is read from each input line:

```console
$ printf '1000\n2048\n' | humanize naturalsize
1.0 kB
2.0 kB
```

Invalid values produce an error identifying the input line and a nonzero exit status.
