# FW 14.00 audit protocol

This audit separates what is present in repository text from what has been
independently reproduced. It does not run JavaScript exploit code, mount an
image, or require a PS4.

## Commands

Run from the repository root:

```sh
python3 scripts/audit_fw14.py --output fw14-audit-report.txt
python3 -m unittest discover -s tests -v
git status --short --branch
git log --oneline --decorate -12
```

The audit reads the actual root-level layout, checks the C include inputs,
extracts `SYSENT` values using token-aware parsing, and reports missing
firmware artifacts with file/line references. A report containing
`UNVERIFIED` or `CONTRADICTED` research items is expected; those items are not
treated as successful verification. Parser and test errors are failures.

## Evidence rules

`CONFIRMED-IN-SOURCE` means a value is present in a named source file only.
`INDEPENDENTLY-VERIFIED` requires a firmware-matched binary, SHA-256, and a
repeatable extraction or test. `UNVERIFIED` means required evidence is absent.
`CONTRADICTED` means repository sources disagree. `BLOCKED` means a required
input or build dependency is unavailable.

The cited upstream commit is now available for source comparison as
`d077fb4031cf0e089fb7a233cebeebcd1ed3c68e`; it agrees with `1400.c` on
`SYSENT=0x01102B70`. The upstream source is still not a firmware-matched
binary, so the value remains `CONFIRMED-IN-SOURCE`, not
`INDEPENDENTLY-VERIFIED`.
