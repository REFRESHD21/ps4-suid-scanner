# Public FW 14.00 Research Claims Review

Date: 2026-10-21

## Executive conclusion

The public material reviewed here identifies legitimate upstream FreeBSD security advisories and several plausible research leads, but it does **not** establish that any of them affect the PS4's customized Orbis kernel, are reachable from an ordinary PS4 process, or can be turned into a kernel exploit on firmware 14.00. No end-to-end FW 14.00 jailbreak is demonstrated by the reviewed sources.

This review is evidence triage, not an exploit implementation. It deliberately distinguishes upstream advisory facts from PS4-specific claims.

## Sources reviewed

- [PS4 13.xx / 14.00 research README](https://github.com/adri22235/ps4-13xx-research/blob/main/README.md)
- [PS4 FW 14.00 vulnerability candidate notes](https://github.com/adri22235/ps4-13xx-research/blob/main/vuln_research_1400.md)
- [FreeBSD-SA-26:54.sysvsem / CVE-2026-58087](https://cgit.freebsd.org/src/commit/sys/kern?id=8c5e2d26cde5d06c362e6925dbcdbd43aa315a12)
- [FreeBSD-SA-26:64.sysvsem / CVE-2026-58098](https://lists.freebsd.org/archives/freebsd-security/2026-September/000569.html)
- [FreeBSD-SA-26:62.tty / CVE-2026-58093](https://security.freebsd.org/advisories/FreeBSD-SA-26:62.tty.asc)
- [FreeBSD-SA-26:63.posixshm / CVE-2026-58094](https://security.freebsd.org/advisories/FreeBSD-SA-26:63.posixshm.asc)
- [FreeBSD-SA-26:55.elf](https://security.freebsd.org/advisories/FreeBSD-SA-26:55.elf.asc)
- [FreeBSD security advisory index](https://www.freebsd.org/security/advisories/)

## Candidate-by-candidate assessment

| Candidate | Upstream evidence | PS4 FW 14.00 status | Current conclusion |
|---|---|---|---|
| CVE-2026-58087, semctl GETALL/SETALL race | Official FreeBSD advisory describes a sequence-number/locking race that can cause kernel heap out-of-bounds reads/writes and potentially privilege escalation on affected supported FreeBSD versions. | No target-kernel source/binary comparison or reproducible Orbis test is supplied in the reviewed repository. The phrase “all supported versions” refers to FreeBSD's supported branches, not every historical FreeBSD-derived OS. | High-value lead to investigate; not established for Orbis. |
| CVE-2026-58098, semop race | Official FreeBSD advisory describes sequence-number wraparound after a blocking semop operation and a possible out-of-bounds access. | Same applicability gap. Disclosure after the PS4 14.00 release does not itself prove the PS4 fork contains the vulnerable implementation. | High-value lead to investigate; not established for Orbis. |
| CVE-2026-58093, TIOCSCTTY race | Official FreeBSD review/advisory describes failure to revalidate terminal state after dropping and reacquiring a lock; the issue can be security relevant. | Presence of a tty subsystem in an ancestor OS does not prove the same locking/state logic exists in Orbis, nor that the needed ioctl/device is reachable. Calling it simply a “UAF” may overstate the demonstrated root cause unless target evidence supports that wording. | Plausible lead; target applicability and reachability unverified. |
| CVE-2026-58094, posixshm | Public research notes identify a large-page shared-memory ioctl race. | Must verify the specific ioctl, large-page shared-memory implementation, and affected code path exist in the target kernel. General POSIX shared-memory support is insufficient. | Lower-priority lead until target code presence is established. |
| CVE-2026-58088, ELF core-dump issue | Public FreeBSD advisory/research describes an out-of-bounds condition involving core-dump handling. | The target's implementation, core-dump configuration, and relevant process-sharing semantics are not demonstrated. | Unverified lead; do not assume it is reachable or exploitable. |
| IPMI syscall 622 claim | The PS4 research README attributes a reported issue to a private/pending disclosure and lists prior firmware versions. | No public target-14.00 symbol, syscall table, implementation, or reproducible artifact was supplied in the reviewed material. | Unverified private-disclosure lead; do not present as public proof. |
| CVE-2026-49415, execve TOCTOU | Real upstream FreeBSD advisory exists. | The reviewed project has not established the same vulnerable exec/credential ordering and required process-access path in Orbis. | Not established for PS4. |
| MP4 parser issue | Research README describes a media-player/SHAREfactory crash/overflow lead. | No matching module hash, root-cause analysis, 14.00 reproduction, or demonstrated transition to kernel privilege is supplied here. | Unverified media-parser lead, not a KEX. |

## Important corrections to the supplied research summary

1. **“Disclosed after firmware release/freeze” is not applicability evidence.** It can support a hypothesis that Sony did not backport a later fix, but only comparison against the actual Orbis implementation can support that inference.
2. **“All supported versions of FreeBSD” does not mean FreeBSD 9 or Orbis.** The advisories list the supported release branches where the vendor confirmed and fixed the bug. An older fork can contain the bug, a different implementation, or neither.
3. **A shared subsystem is not proof of a shared vulnerable code path.** SysV semaphore, tty, and POSIX shared-memory interfaces existing in an ancestor OS is not enough. The specific data structures, locking, validation, and configuration must match.
4. **A kernel out-of-bounds access is not automatically arbitrary kernel read/write.** Turning a memory-safety defect into reliable privilege escalation is a separate and difficult step; the reviewed notes do not demonstrate that step on FW 14.00.
5. **The stage-two script does not prove a browser primitive or kernel R/W.** In this repository it contains unresolved base-address/gadget assumptions and placeholder paths. Function names and log strings are not runtime evidence.
6. **Gadget offsets need a traceable target binary.** A credible verification record should identify the exact module and firmware, provide a cryptographic hash, document extraction/disassembly commands, and distinguish complete instruction sequences from partial byte matches.
7. **Syscall numbers and interface availability must be checked against Orbis.** A number copied from upstream FreeBSD or another PS4 version cannot be assumed to map to the same handler on FW 14.00.
8. **The repository README and the candidate notes are claims by the research authors, not independent validation.** They are useful leads, but confidence labels such as “VERY HIGH” should not be repeated as established target applicability without primary evidence.

## Recommended research order

1. **Evidence/provenance pass:** preserve immutable advisory URLs, correction commits, and exact version scopes for each candidate.
2. **Target implementation pass:** for each candidate, record whether the relevant syscall/ioctl and vulnerable code path can be established in an authenticated FW 14.00 kernel image or an appropriately sourced matching code base. If target material is unavailable, mark the item blocked rather than infer from FreeBSD 9.
3. **Reachability pass:** establish whether the required interface is enabled and accessible from a realistic unprivileged PS4 process. Do not infer browser sandbox reachability from general userland availability.
4. **Non-destructive reproduction pass:** use an appropriately controlled test environment and a minimal test that establishes the underlying defect without attempting to turn it into a privilege-escalation payload.
5. **Exploitability assessment:** only after the defect and target applicability are independently demonstrated should the project assess whether it yields a useful primitive. A crash alone is not proof.
6. **Chain integration:** treat WebKit entry, sandbox boundaries, kernel privilege escalation, and payload loading as separate milestones with separate acceptance criteria.

## Acceptance criteria for changing status

A candidate should not be marked **CONFIRMED FOR FW 14.00** until the record includes:

- Exact firmware/build and target component identity.
- Primary source or authenticated target binary provenance, including a hash where applicable.
- Specific code path or instruction-level evidence supporting applicability.
- Reproducible observations with test conditions and limitations.
- Independent evidence distinguishing a crash from controlled memory corruption and distinguishing memory corruption from privilege escalation.

An end-to-end jailbreak claim additionally requires a documented run on actual FW 14.00 hardware (or an explicitly justified equivalent environment), with the full chain and payload outcome recorded.

## Bottom line

The semaphore advisories are the most concrete public kernel research leads in the reviewed notes because their upstream root causes and security impact are documented. They are **not yet confirmed PS4 exploits**. The correct next milestone is target-specific applicability evidence, not assuming that a newly disclosed FreeBSD bug transfers unchanged to Orbis.
