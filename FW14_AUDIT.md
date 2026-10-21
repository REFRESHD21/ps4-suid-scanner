# Firmware 14.00 audit workflow

This repository contains preliminary PS4 firmware research. The presence of offsets,
gadget candidates, or a browser entry page does **not** establish a working jailbreak.

## Run the static audit

Requirements: Python 3 and Node.js 22.

```bash
python3 tools/audit_fw14.py
cat audit-report.md
```

The script checks JavaScript parser syntax, expected files and include dependencies,
conflicting SYSENT claims, explicit TODO/placeholder markers, and source-declared
gadget confidence. It writes `audit-report.md`.

GitHub Actions runs the same audit on pushes, pull requests, and manual dispatches.
Download the `fw14-static-audit-report` artifact from the workflow run.

## Status meanings

- **PASS** — a narrow static check succeeded; this does not mean an exploit works.
- **FAIL** — an inconsistency or explicit missing component was detected.
- **UNVERIFIED** — source claims lack sufficient independent evidence.
- **BLOCKED** — a check could not be completed because required inputs are absent.

## Important limitations

- This audit does not run browser exploit code or kernel payloads.
- It cannot validate firmware offsets without the exact matching binary/dump and
  reproducible evidence.
- Hardware testing is required to claim support for a particular PS4 firmware.
- Treat kernel offsets and gadget addresses as unverified until independently confirmed.
