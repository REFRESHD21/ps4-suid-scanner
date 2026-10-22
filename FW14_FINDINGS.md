# FW 14.00 findings and next steps

Date: 2026-10-21

## Current conclusion

This repository is a research scaffold, not a demonstrated PS4 firmware 14.00 jailbreak. Static source claims must not be presented as hardware-verified results.

## Evidence ledger

| Finding | Evidence | Status |
|---|---|---|
| Browser entry point lacks an integrated exploit primitive | `exploit.html` explicitly describes the primitive as not integrated | CONFIRMED-IN-SOURCE |
| Stage-two address leaks and setup are incomplete | `jordy_stage2_1400.js` contains TODOs, unknown-offset branches, and placeholder behavior | CONFIRMED-IN-SOURCE |
| Gadget claims are not independently reproducible from this repository alone | Matching binary hash and reproducible extraction output are not supplied | UNVERIFIED |
| `SYSENT=0x01102B70` is present in the upstream PS4-HEN source | Immutable upstream commit below | CONFIRMED-IN-SOURCE |
| Alternative `SYSENT=0x0110A760` is contradicted by the cited upstream source | The cited source uses `0x01102B70`; the alternative is not supported by that source | CONTRADICTED |
| Correctness of `SYSENT=0x01102B70` against genuine firmware 14.00 kernel bytes | No matching kernel image and independent validation record are included here | UNVERIFIED |
| C build inputs are absent from the inspected scanner tree | Required include paths were not present in the inspected tracked file list | BLOCKED |
| Celsius must not be assumed compatible with FW 14.00 | Repository notes say it was patched by 13.50; no compatible 14.00 KEX is demonstrated here | UNVERIFIED |

### SYSENT provenance

- Upstream repository: `Al-Azif/ps4-hen`
- Commit: `d077fb4031cf0e089fb7a233cebeebcd1ed3c68e`
- Source file: [`kpayload/source/offsets/1400.c`](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/source/offsets/1400.c)
- Value in that source: `SYSENT=0x01102B70`
- Interpretation: this establishes the value's upstream source provenance and contradicts the alternate value in the notes file. It does **not** independently validate the offset against a genuine firmware 14.00 kernel image.

## C/header dependency trace

The new static audit checks the quoted includes actually present in the repository's C and header files. On the current branch, it reports six unresolved quoted includes; the GitHub Actions report records them as **BLOCKED**, not as proof that the offsets themselves are wrong.

| Local include | Referencing file | Traceable upstream location |
|---|---|---|
| `sections.h` | `1304.c`, `1400.c` | [PS4-HEN sections.h at the source commit](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/include/sections.h) |
| `offsets/1304.h` | `1304.c` | [PS4-HEN offsets/1304.h](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/include/offsets/1304.h) |
| `offsets/1400.h` | `1400.c` | [PS4-HEN offsets/1400.h](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/include/offsets/1400.h) |
| `../offsets.h` | root-level `1304.h`, `1400.h` | [PS4-HEN offsets.h](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/include/offsets.h) |

The upstream `offsets.h` itself includes `sections.h`. In the scanner repository, the versioned headers are currently at the repository root rather than under `offsets/`, and their `../offsets.h` includes resolve outside the repository when interpreted relative to those root-level files. The canonical upstream layout places `offsets.h` and `sections.h` in `kpayload/include/`, with version headers in `kpayload/include/offsets/`.

These are dependency/layout findings only. The upstream headers were traced but not copied blindly into this repository: first establish the intended build target, applicable license/provenance, and SDK/compiler requirements. Resolving these includes would enable a more meaningful syntax/build check, but would not validate firmware offsets or demonstrate a jailbreak.

## Important interpretation

- JavaScript syntax passing proves only that Node.js can parse the file.
- Source-to-source agreement is not independent verification.
- A gadget claim is reproducible only when the exact input binary is identified by firmware/module and cryptographic hash, the extraction method is documented, and complete gadgets are distinguished from partial instruction sequences.
- An audit result is not evidence that a jailbreak works. Hardware validation and documented test conditions would be required for that claim.

## Work order

1. Keep unsupported success claims clearly marked as unverified.
2. Run the static audit and retain its report as a CI artifact.
3. Resolve missing build dependencies from traceable upstream sources and check whether the C code builds as documented.
4. Preserve the SYSENT provenance correction; do not claim independent offset validation without matching binary evidence.
5. Record source URLs, commit IDs, binary hashes, commands, outputs, and limitations for each new claim.
6. Reassess public research for 14.00 compatibility before describing any exploit as available.

## Not yet established

- A working WebKit primitive on firmware 14.00.
- Correctness of all listed kernel offsets against a genuine matching firmware image.
- A compatible kernel exploit for firmware 14.00.
- An end-to-end jailbreak tested on actual firmware 14.00 hardware.


## Kernel vulnerability lead correction

The CVE analysis now distinguishes the real upstream FreeBSD advisory for CVE-2026-49415 from unproven applicability to PS4. FreeBSD's advisory describes a SUID `execve(2)` TOCTOU race and lists fixes for supported FreeBSD 14.x/15.x releases; it does not establish that the same vulnerable code path exists in Orbis OS's older, customized kernel. Finding generic SUID helper functions in an old source tree is not enough. The lead remains **NOT ESTABLISHED FOR PS4** until the target code path, process-memory access checks, and sandbox reachability are compared and reproduced.

Reference: [FreeBSD-SA-26:39.execve](https://lists.freebsd.org/archives/freebsd-security/2026-June/000522.html).

This qualification changes no overall conclusion: no compatible FW 14.00 kernel exploit or end-to-end jailbreak has been demonstrated by this repository.

## Public-status checkpoint — 2026-10-22

The latest public-source check found no published end-to-end PS4 FW 14.00 jailbreak in the [ConsoleMods exploit chart](https://consolemods.org/wiki/PS4:Exploit_Chart). The [PS4 Developer Wiki vulnerability index](https://www.psdevwiki.com/ps4/Vulnerabilities) describes the public AIO/Relapse implementation as targeting 13.02–13.52 and says it may be patched in 14.00. This is a public-status snapshot, not proof that private research does not exist.

**Research priority remains:** obtain target-specific FW 14.00 evidence for the browser entry point and kernel candidate before changing status labels. Matching a 13.52 offset, finding an upstream FreeBSD advisory, or seeing a GitHub issue request is not a reproduction. No new evidence found in this refresh resolves the three major blockers: userland primitive, verified matching-firmware offsets, and compatible kernel exploit.
