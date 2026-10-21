# PS4 Security Research — Firmware 13.04 / 14.00

Research tools, kernel offsets, WebKit ROP gadgets, and exploit framework for PS4 firmware 13.04–14.00 security research.

## 🔥 What's New — FW 14.00 WebKit Release

**Unverified hypothesis:** this repository does not currently include independently reproducible evidence that WebKit on 14.00 is byte-identical to 13.04. Matching gadget offsets alone would not prove that every 13.04 exploit entry vector works on 14.00.

### Current status: research scaffold, not a working 14.00 jailbreak
- ⚠️ Gadget offsets are source claims; the exact binary hash and reproducible extraction evidence are not included here.
- ⚠️ `SYSENT=0x01102B70` has traceable upstream source provenance; independent validation against a matching 14.00 kernel image is still absent. Other offsets remain provisional.
- ❌ `exploit.html` explicitly says the WebKit primitive is not integrated.
- ❌ `jordy_stage2_1400.js` contains unresolved address/primitive placeholders.
- ❌ A compatible kernel exploit for 14.00 has not been demonstrated by this repository.

## Contents

| File | Description |
|------|-------------|
| `exploit.html` | **WebKit entry page** (supports 14.00 and links to 13.04) |
| `exploit_1304.html` | **WebKit + Celsius KEX entry page** (dedicated for FW 13.04) |
| `celsius_kex.js` | **Celsius Kernel Exploit engine** (ROP mount, kernel patches, BinLoader) |
| `build_celsius_ufs.py` | **Celsius UFS image generator** (malformed superblock with integer overflow) |
| `jordy_stage2.js` | Stage 2: persistent R/W + Celsius KEX integration for 13.04 |
| `webkit_gadgets_1304.js` | WebKit ROP gadgets FW 13.04 (16 gadgets) |
| `1304.c` / `1304.h` | FW 13.04 kernel offset definitions; verify against matching inputs |
| `webkit_gadgets_1400.js` | Candidate WebKit gadget list; not independently verified |
| `jordy_stage2_1400.js` | Incomplete FW 14.00 stage-two scaffold; unresolved primitives and addresses remain |
| `1400.c` / `1400.h` | Kernel offset definitions; not independently validated |
| `webkit_gadgets_1350.js` | WebKit ROP gadgets FW 13.50 (18 gadgets) |
| `1400_offsets.txt` | Offset provenance and verification notes |
| `1352_offsets.txt` | Partial kernel offsets FW 13.52 |
| `cve_analysis.md` | CVE analysis for PS4 kernel |
| `hen.bin` | PS4-HEN compiled for FW 13.04 |
| `scanner_1304.iso` | SUID scanner BD-JB ISO |
| `src/` | BD-JB scanner Java source |

## Architecture

```
PS4 Browser loads exploit.html
        │
        ▼
┌─────────────────────────────┐
│  WebKit Exploit Primitive   │  ← NEEDED FROM SCENE
│  (Jordy / ntfargo / DOM)    │     Port from 13.04
│  Gains: candidate + r/w    │
└────────────┬────────────────┘
             │ stage2_init()
             ▼
┌─────────────────────────────┐
│  jordy_stage2_1400.js       │  ← INCOMPLETE SCAFFOLD
│  - Persistent R/W           │  ← NOT IMPLEMENTED/PROVEN
│  - Leak webkit_base         │  ← PLACEHOLDER
│  - Leak libkernel_base      │  ← UNVERIFIED
│  - Build ROP chain          │  ← NOT VALIDATED
│  - Execute via vtable pivot │  ← NOT VALIDATED
└────────────┬────────────────┘
             │ ROP → dlsym → mount()
             ▼
┌─────────────────────────────┐
│  Kernel Exploit (Celsius)   │  ← Needs KEX for 14.00
│  ffs_mount integer overflow │     Celsius patched in 13.50
│  OR new KEX for 14.00       │
└────────────┬────────────────┘
             │ kernel r/w
             ▼
┌─────────────────────────────┐
│  Post-Exploitation          │  ← NOT USABLE WITHOUT VERIFIED KERNEL R/W
│  - Escape sandbox (PRISON0) │
│  - Root vnode               │
│  - Enable debug menu        │
│  - Enable fpkg              │
│  - Load GoldHEN via port    │
│    9021 BinLoader           │
└─────────────────────────────┘
```

## Status (October 2026)

### WebKit Entry Points (13.04 → 14.00)
The following vectors are documented as tested on 13.04 only. Their applicability to 14.00 is unverified:
- ✅ **DOM postMessage** — Type confusion, confirmed on 13.04
- ✅ **DOM getters** — UAF, confirmed on 13.04
- ✅ **LLInt OOB** — Out-of-bounds read, confirmed on 13.04
- ✅ **CSSFontFace** (Jordy/ntfargo) — UAF, tested on 13.04
- ✅ **PlayStation Vue** — Potential entry via installed app

### Kernel Exploits
- 🔥 **Celsius (ffs_mount)** — Works ≤13.04, patched in 13.50. **Not available for 14.00.**
- ⚠️ **CVE-2026-49415** — execve TOCTOU race. Affects all FreeBSD. Under investigation.
- ⚠️ **MP4 Parser** — Heap overflow in moov.udta.meta. Under investigation.

### What the Scene Needs to Provide
1. **WebKit exploit primitive for 14.00** — Port Jordy or ntfargo (same offsets as 13.04)
2. **Kernel exploit for 14.00** — Celsius is patched. Need new KEX:
   - CVE-2026-49415 (execve TOCTOU) is a candidate
   - MP4 parser heap overflow needs more analysis
   - Or discover a new kernel bug in 14.00

## Quick Start

### On PS4 (FW 13.04 — Celsius KEX Active)
1. Build malicious UFS image:
   ```bash
   python3 build_celsius_ufs.py -o celsius.img
   ```
2. Copy `celsius.img` to the root of a FAT32/exFAT USB drive (appears at `/mnt/usb0/celsius.img` on PS4).
3. Insert USB into the PS4.
4. Host the exploit directory on PC/local network:
   ```bash
   python3 -m http.server 8080
   ```
5. Navigate PS4 browser to `http://<your-ip>:8080/exploit_1304.html`.
6. Click **Run Exploit (Celsius)** to trigger the userland chain + Celsius kernel exploit.
7. Once kernel patches are applied, send payload (GoldHEN/HEN) to port 9021.

### On PS4 (FW 14.00 — incomplete research scaffold)
There is no working 14.00 exploit flow to run in this repository. The page is a diagnostic scaffold; the WebKit primitive and compatible kernel exploit are missing. Do not interpret its analysis output as a jailbreak or run unverified offset/payload code on a console.

### For Development (PC)
1. Open `exploit_1304.html` or `exploit.html` in any browser.
2. Automatically detects non-PS4 and enters survey/analysis mode.
3. Displays source-declared gadget candidates and offsets for analysis; this view does not independently verify them.

## WebKit Gadgets (14.00)

Offsets claimed by repository source; the matching binary hash and reproducible extraction output are not supplied:

| Gadget | Offset | Bytes | Status |
|--------|--------|-------|--------|
| RET | `0x4032` | `c3` | Source claim only |
| LEAVE_RET | `0x1c2f7` | `c9 c3` | Source claim only |
| POP_RAX_RET | `0x14504` | `58 c3` | Source claim only |
| POP_RBX_RET | `0xb9e8` | `5b c3` | Source claim only |
| POP_RCX_RET | `0x1fade` | `59 c3` | Source claim only |
| POP_RDI_RET | `0x60480` | `5f c3` | Source claim only |
| POP_RDX_RET | `0x1305ba` | `5a c3` | Source claim only |
| POP_RSI_RET | `0x7245e` | `5e c3` | Source claim only |
| POP_RBP_RET | `0x40b6` | `5d c3` | Source claim only |
| POP_RSP_RET | `0x73017` | `5c c3` | Claimed stack pivot; unverified |
| POP_R8_RET | `0x230cbe1` | `41 58 c3` | Source claim only |
| POP_R9_RET | `0x9df883` | `41 59 c3` | Source claim only |
| POP_R10_RET | `0x2dc33b5` | `41 5a 41...` | Partial/unverified |
| POP_R11_RET | `0x19c9ba` | `41 5b 41...` | Partial/unverified |
| POP_R12_RET | `0x242ab15` | `41 5c c3` | Source claim only |
| POP_R13_R14_R15_RET | `0x6047b` | `41 5d 41 5e 41 5f c3` | Claimed multi-pop; unverified |
| POP_R14_RET | `0xa9e91` | `41 5e c3` | Source claim only |
| POP_R15_RET | `0x6047f` | `41 5f c3` | Source claim only |

**Evidence status:** these offsets are claims in repository source. Without the exact 14.00 binary, its hash, and reproducible byte-pattern verification, they do not confirm that WebKit was unchanged.

## Kernel Offsets (14.00)

Copied from `1400.c`; values are **unverified for this repository's target firmware** until independently checked against a matching kernel image. The `SYSENT` value has upstream source provenance but remains independently unverified against a matching kernel image.

```
PRISON0    = 0x0111FA18    (sandbox escape)
ROOTVNODE  = 0x02136E90    (root filesystem)
ALLPROC    = 0x01B28538    (process list)
SYSENT     = 0x01102B70    (syscall table)
memcpy     = 0x002BD850    (changed from 13.04: was 0x002BD4F0)
proc_rwmem = 0x00366A10    (process memory r/w)
```

## Celsius Technical Analysis

See `cve_analysis.md` for full details. Summary:

- **Bug:** Integer overflow in `ffs_mountfs()` → heap overflow
- **Trigger:** Mount crafted UFS image with `fs_ncg = 0x40000001`
- **Works on:** ≤13.04, PS5 ≤12.70
- **Patched in:** PS4 13.50, PS5 13.00
- **Not available for 14.00** — need alternative KEX

## SUID Scanner

BD-JB based scanner for SUID/SGID binaries on PS4 filesystem.

1. Burn `scanner_1304.iso` to BD-R at 4x speed
2. Insert USB drive (FAT32/exFAT) in PS4
3. Insert BD-R disc
4. Results appear on screen and saved to USB

## Timeline

| Date | Event |
|------|-------|
| 2026-10-18 | **FW 14.00 WebKit release** — gadgets + stage2 + exploit.html |
| 2026-09-24 | FW 14.00 kernel offsets added (Al-Azif) |
| 2026-09-21 | PS4 13.04 jailbroken — GoldHEN v2.4b18.12 (SiSTRo) |
| 2026-09-19 | PS4 13.04 jailbroken — HEN 2.2.0 |
| 2026-09-16 | Sony releases FW 14.00 |
| 2026-07-21 | MasterMaind confirms BD-J escape up to 13.52 |
| 2026-07-18 | Celsius (ffs_mount KEX) announced by bollars |
| 2026-07-18 | 13.04 kernel offsets published |

## Credits

- **adri22235** — WebKit gadget extraction, stage 2 porting, exploit framework
- **ps3120** — BD-JB-1250
- **Gezine** — BD-JB vulnerability discovery
- **Al-Azif** — 14.00 kernel offsets (Scene-Collective/ps4-hen)
- **Scene-Collective** — ps4-hen open source offsets
- **Pharaoh2k** — 13.04 kernel offsets verification
- **SiSTRo** — GoldHEN v2.4b18.12
- **bollars** — Celsius (ffs_mount) discovery
- **MasterMaind (@ASaudidos)** — BD-J escape confirmation up to 13.52
- **Shunsui** — MP4 parser vulnerability discovery
- **Victor** — Celsius confirmation and technical guidance

## Based on

- [BD-JB-1250](https://github.com/ps3120/BD-JB-1250) by ps3120/Gezine
- [Scene-Collective/ps4-hen](https://github.com/Scene-Collective/ps4-hen) for offset format
- [PPPwn](https://github.com/TheOfficialFloW/PPPwn) by TheFloW for exploit architecture reference

## License

This research is for educational and security research purposes only.
