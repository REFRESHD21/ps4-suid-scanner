# FW 14.00 findings ledger

Audit baseline: branch `audit/fw14-evidence`, repository commit
`915a234d798c9ac154417d54342eb4d540203129` (the starting `main` commit).
No firmware dump or PS4 hardware was available. “Source” below means a claim
in this checkout, not independent confirmation.

| Claim | Status | Source / upstream reference | Firmware/module | SHA-256 | Method and limitation |
|---|---|---|---|---|---|
| `SYSENT` is `0x01102B70` | CONFIRMED-IN-SOURCE | [`1400.c`](1400.c#L29); upstream [`d077fb4031cf0e089fb7a233cebeebcd1ed3c68e`](https://github.com/Scene-Collective/ps4-hen/tree/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e) | PS4 14.00 kernel offsets; exact binary unavailable | unavailable | Independent source comparison agrees, but this is not firmware-binary or hardware verification. |
| `SYSENT` is `0x0110A760` | CONTRADICTED | [`1400_offsets.txt`](1400_offsets.txt#L11); upstream [`d077fb4031cf0e089fb7a233cebeebcd1ed3c68e`](https://github.com/Scene-Collective/ps4-hen/tree/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e) and [`1400.c`](1400.c#L29) disagree with it | PS4 14.00 kernel offsets; exact binary unavailable | unavailable | Retained as a historical conflicting claim only; do not use without firmware-matched binary evidence. |
| The listed kernel offsets are present in a 14.00 source table | CONFIRMED-IN-SOURCE | [`1400.c`](1400.c#L7); upstream [`d077fb4031cf0e089fb7a233cebeebcd1ed3c68e`](https://github.com/Scene-Collective/ps4-hen/tree/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e) | PS4 14.00 kernel offsets; binary unavailable | unavailable | Source comparison agrees for the table values. No firmware-matched binary verification. |
| Kernel offsets are correct for a 14.00 kernel | UNVERIFIED | [`1400.c`](1400.c#L7), [`1400_offsets.txt`](1400_offsets.txt#L1) | PS4 14.00 kernel; no dump/ELF | unavailable | No firmware-matched binary, symbol proof, byte signatures, or hardware test. |
| The 17 WebKit gadget offsets are 14.00 gadgets | UNVERIFIED | [`webkit_gadgets_1400.js`](webkit_gadgets_1400.js#L2); repository commits `2bbe092c60745c793816646199f16adae65a66b8` and `349e4c1827dfd2f021e00d9c8780b8b284315a12` | `libSceNKWebKit.sprx.decrypted`, PS4 14.00; binary unavailable | unavailable | The file contains claimed opcodes, but the referenced dump and extraction script are absent. `POP_R10`/`POP_R11` are explicitly partial. |
| 14.00 WebKit is identical to 13.04 and 13.04 entry vectors should work | UNVERIFIED | [`README.md`](README.md#L7), [`webkit_gadgets_1400.js`](webkit_gadgets_1400.js#L57) | PS4 13.04 vs 14.00 WebKit; binaries unavailable | unavailable | Matching constants in two source files are not an independent binary comparison; no 14.00 primitive or hardware validation is included. |
| The 14.00 WebKit exploit chain is operational | BLOCKED | [`exploit.html`](exploit.html#L199), [`jordy_stage2_1400.js`](jordy_stage2_1400.js#L243) | PS4 browser / WebKit 14.00; primitive and dump unavailable | unavailable | The entry page labels itself analysis mode and the stage has TODOs for vtable/GOT values. No payload was executed. |
| Celsius is available on 14.00 | CONTRADICTED | [`README.md`](README.md#L90), [`cve_analysis.md`](cve_analysis.md#L47) | PS4 14.00 kernel; no 14.00 test | unavailable | Repository text says Celsius is patched before 14.00 and also describes a 13.04-only path. No 14.00 KEX is supplied. |
| A clean checkout can build `1400.c` | BLOCKED | [`1400.c`](1400.c#L1), [`1400.h`](1400.h#L4) | C toolchain; project headers unavailable | unavailable | `sections.h`, `offsets.h`, and `offsets/1400.h` are referenced but absent. This audit does not invent replacements. |
| Firmware 14.00 jailbreak support is demonstrated | UNVERIFIED | repository release/UI text | PS4 14.00 hardware; no validation record | unavailable | No authorized hardware test log, binary inputs, or reproducible end-to-end evidence is present. |

## Highest-value next evidence

1. Obtain an authorized, firmware-matched 14.00 kernel dump and record its
   SHA-256, module identity, and extraction commands.
2. Obtain the exact `libSceNKWebKit.sprx.decrypted` used for the gadget table,
   plus the byte-search script and complete opcode windows.
3. Reconcile `SYSENT` and every kernel offset against those artifacts; keep
   unresolved values marked `UNVERIFIED`.
4. Restore the missing build headers or document their upstream commit and
   reproducible acquisition without fabricating substitutes.
