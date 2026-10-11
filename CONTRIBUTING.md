# Contributing

Travel OS welcomes focused fixes that make planning, execution, version recovery or collaboration more reliable.

## Before opening a change

1. Start from a reproducible user problem or an existing Issue.
2. Use fictional trips, dates, names and booking details.
3. Keep the eight sheet names and the Active Version contract stable unless the change includes a migration plan.
4. Update the Skill instructions, reference rules, template and tests together when the data contract changes.

## Validate

Run:

```text
python -m unittest discover -s tests -p "test_*.py" -v
python skill/travel-os/scripts/validate_archive.py templates/TravelOS-Example.xlsx
```

Open both workbooks in Excel or a compatible editor after workbook changes. Confirm that filters, dropdowns, dates, column widths and frozen headers still work.

## Releases

Prepare the README link, `RELEASE_NOTES.md` and `CHANGELOG.md` in a pull request. After it merges, push the matching `v*` tag. GitHub Actions reruns the contract tests, builds the full source ZIP and direct-install Skill ZIP from that exact commit, verifies the Skill root, writes their SHA-256 values, and creates the prerelease.

## Pull requests

Explain the user-visible problem, the resulting behavior and how you verified it. Avoid unrelated formatting or dependency changes.
