# ShipGate findings index — python-humanize/humanize

Captured 2026-07-30 during follow-up auto-expand pass.

| Artifact              | Description                              |
| --------------------- | ---------------------------------------- |
| `check.out`           | `shipgate check --suite full --target .` |
| `refactor-strict.out` | `shipgate refactor check --strict .`     |
| `format.out`          | `shipgate format --target .`             |

## Counts (from captures)

- **Check findings:** ~220 (lint-heavy; security clean)
- **Strict refactor opportunities:** ~49 (JSON array in `refactor-strict.out`)
- **Format issues:** ~90 (ruff format/lint during format pass)

See `SUMMARY.md` for the owner-facing report.
