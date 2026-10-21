// ============================================================
// WebKit ROP Gadgets — PS4 Firmware 14.00
// Source: libSceNKWebKit.sprx.decrypted
// Found using Python byte pattern search
// Status: unverified candidate offsets; partial entries are explicitly marked below
// ============================================================
//
// Usage: Include this file before jordy_stage2_1400.js
//        Gadgets are offsets from WebKit module base.
//        Final address = webkit_base + offset
//
// Byte patterns used for verification:
//   POP_R*_RET gadgets: 41 5X c3 (where X = register encoding)
//   POP_R13_R14_R15_RET: 41 5d 41 5e 41 5f c3
//   Standard POP+RET: 5X c3 (X = register encoding)
//   RET: c3
//   LEAVE_RET: c9 c3
//
// Notes:
//   - POP_R10 and POP_R11 are partial matches (not clean c3 terminator)
//     They may clobber additional registers. Verify before using in chain.
//   - POP_R13 is actually: pop r13; pop r14; pop r15; ret
//     Requires 3 stack slots (r13 value + r14 pad + r15 pad)
//   - All offsets confirmed identical to 13.04 (WebKit not updated in 14.00)
// ============================================================

const webkit_gadgets_1400 = {
    // ── Core gadgets (verified clean) ──
    wk_RET          : 0x4032,       // c3
    wk_LEAVE_RET    : 0x1c2f7,      // c9 c3
    wk_POP_RAX_RET  : 0x14504,      // 58 c3
    wk_POP_RBX_RET  : 0xb9e8,       // 5b c3
    wk_POP_RCX_RET  : 0x1fade,      // 59 c3
    wk_POP_RDI_RET  : 0x60480,      // 5f c3
    wk_POP_RDX_RET  : 0x1305ba,     // 5a c3
    wk_POP_RSI_RET  : 0x7245e,      // 5e c3
    wk_POP_RBP_RET  : 0x40b6,       // 5d c3
    wk_POP_RSP_RET  : 0x73017,      // 5c c3 (stack pivot!)

    // ── Extended registers (verified) ──
    wk_POP_R8_RET   : 0x230cbe1,    // 41 58 c3
    wk_POP_R9_RET   : 0x9df883,     // 41 59 c3 (pop r9; ret)
    wk_POP_R12_RET  : 0x242ab15,    // 41 5c c3

    // ── Extended registers (partial — verify before use) ──
    wk_POP_R10_RET  : 0x2dc33b5,    // 41 5a 41 ... (not followed by clean ret)
    wk_POP_R11_RET  : 0x19c9ba,     // 41 5b 41 ... (not followed by clean ret)

    // ── Multi-pop gadgets ──
    wk_POP_R13_RET  : 0x6047b,      // 41 5d 41 5e 41 5f c3 (pops r13, r14, r15)
    wk_POP_R14_RET  : 0xa9e91,      // 41 5e c3
    wk_POP_R15_RET  : 0x6047f,      // 41 5f c3
};

// ============================================================
// IMPORTANT OBSERVATION:
// The listed offsets are claimed to match FW 13.04; this has NOT been independently verified against a matching FW 14.00 binary.
// Do not infer that WebKit was unchanged without matching-binary hashes and reproducible comparison.
// The "stability improvements" in 14.00 were kernel-only patches.
//
// This means:
//   1. WebKit entry vectors from 13.04 require separate 14.00 verification
//   2. vtable offsets, GOT layout, and JIT behavior remain unverified
//   3. Do not assume only kernel offsets changed
//
// Missing gadget for 14.00 (search in dump):
//   JMP_RSI (ff e6) — was 0x0cda83 in 13.04
//   MOV_RDI_RAX_CALL_RSI — needed for some ROP patterns
//   XCHG_RAX_RSP_RET — alternative stack pivot
// ============================================================
