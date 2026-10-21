# Maintainer summary

## Changed

- Added `FW14_FINDINGS.md`, a status ledger with provenance, commit references,
  missing SHA-256 inputs, methods, and limitations.
- Added `FW14_AUDIT.md` and `scripts/audit_fw14.py` to inspect the real checkout
  layout, surface missing build/evidence inputs, and report the `SYSENT`
  contradiction with locations.
- Added tests for expected findings, clean fixtures, and alternate `SYSENT`
  spellings. Added CI that uploads the report even when a test/build step
  fails.
- Reworded README/UI/source comments so source-listed candidates are not
  presented as verified 14.00 support.

## Tested

- `python3 scripts/audit_fw14.py --output /tmp/fw14-audit-report.txt` — exit 0;
  reports 3 blocked build inputs, the `SYSENT` contradiction, and 6 unverified
  evidence/provenance items.
- `python3 -m unittest discover -s tests -v` — 3 tests passed.
- `python3 -m py_compile scripts/audit_fw14.py` — passed.
- `node --check webkit_gadgets_1400.js` and `node --check jordy_stage2_1400.js`
  — passed. No exploit code was executed.

## Failed or blocked

- `clang -fsyntax-only -I. 1400.c` fails because `sections.h` is absent; the
  referenced `offsets.h` and `offsets/1400.h` are also absent.
- The initial audit could not fetch upstream because DNS was unavailable. A
  follow-up source comparison now confirms commit
  `d077fb4031cf0e089fb7a233cebeebcd1ed3c68e` and its matching `SYSENT` value;
  this still does not replace firmware-binary evidence.
- No firmware-matched kernel/WebKit binaries, SHA-256 hashes, extraction
  script, or authorized hardware validation record is included.

## Next highest-value evidence

Obtain an authorized 14.00 kernel dump and the exact decrypted WebKit module,
record their SHA-256 hashes and extraction commands, then resolve `SYSENT` and
the remaining offsets against those artifacts before any support claim is
promoted.
