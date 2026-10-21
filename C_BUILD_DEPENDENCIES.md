# C build dependency investigation

Date: 2026-10-21

## Result

The scanner repository's current C files cannot yet be treated as a self-contained build. The missing quoted includes map to paths in the upstream PS4-HEN source tree, but the scanner's current file layout differs from that tree. No headers have been copied into this repository as part of this investigation.

## Traceable upstream layout

Reference commit: [Al-Azif/ps4-hen `d077fb4031cf0e089fb7a233cebeebcd1ed3c68e`](https://github.com/Al-Azif/ps4-hen/tree/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e)

| Required header | Canonical upstream path | Purpose / include relationship |
|---|---|---|
| `sections.h` | `kpayload/include/sections.h` | Defines the `PAYLOAD_*` section attributes used by payload structures |
| `offsets.h` | `kpayload/include/offsets.h` | Defines `struct kpayload_offsets`; includes `sections.h` |
| `1304.h` | `kpayload/include/offsets/1304.h` | Firmware-specific offsets header; includes `../offsets.h` |
| `1400.h` | `kpayload/include/offsets/1400.h` | Firmware-specific offsets header; includes `../offsets.h` |

The corresponding upstream Makefile uses GCC, objcopy, make, and an include path of `-Iinclude`; it also expects the upstream `kpayload/source`, linker script, and payload build layout. This is evidence about how that upstream project builds, not proof that the scanner's root-level C files are drop-in compatible with it.

Sources:
- [Upstream `sections.h`](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/include/sections.h)
- [Upstream `offsets.h`](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/include/offsets.h)
- [Upstream `kpayload/Makefile`](https://github.com/Al-Azif/ps4-hen/blob/d077fb4031cf0e089fb7a233cebeebcd1ed3c68e/kpayload/Makefile)
- [Upstream build instructions](https://github.com/Al-Azif/ps4-hen)

## SDK and license gate

The upstream README describes installing `ps4-payload-sdk` before building PS4-HEN. The scanner repository does not currently include that SDK, its own complete build instructions, or the upstream project's build tree.

A license file was not found at the inspected upstream commit's repository root during this check. That is not a legal conclusion about every file or contributor; it means licensing/provenance must be verified before vendoring these headers into this repository. For now, use links and documented paths rather than copying files.

## Next build investigation

1. Confirm the intended target of the scanner's root-level `1304.c` and `1400.c`: standalone compile, payload translation unit, or source intended to be integrated into a larger PS4-HEN tree.
2. Identify the required SDK/toolchain version and exact build command from the project's own source history or maintainers.
3. Verify license/provenance for each required header before vendoring or adapting it.
4. Once build context is established, add a reproducible compile/check job. Do not compile a partial payload with guessed headers or treat a successful generic C syntax check as firmware-offset validation.

## What this does not establish

This investigation does not verify kernel offsets against a genuine FW 14.00 binary, validate WebKit gadget addresses, supply a missing exploit primitive, or demonstrate a working jailbreak.
