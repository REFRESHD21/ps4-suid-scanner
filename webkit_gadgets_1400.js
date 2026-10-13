// WebKit ROP Gadgets — PS4 Firmware 14.00
// Source: libSceNKWebKit.sprx.decrypted
// Found using Python byte pattern search

const webkit_gadgets_1400 = {
    wk_RET          : 0x4032,
    wk_LEAVE_RET    : 0x1c2f7,
    wk_POP_RAX_RET  : 0x14504,
    wk_POP_RBX_RET  : 0xb9e8,
    wk_POP_RCX_RET  : 0x1fade,
    wk_POP_RDI_RET  : 0x60480,
    wk_POP_RDX_RET  : 0x1305ba,
    wk_POP_RSI_RET  : 0x7245e,
    wk_POP_RBP_RET  : 0x40b6,
    wk_POP_RSP_RET  : 0x73017,
    wk_POP_R8_RET   : 0x230cbe1,
    wk_POP_R9_RET   : 0x9df883,  // 49 59 c3
    wk_POP_R10_RET  : 0x2dc33b5, // 41 5a 41 (partial match)
    wk_POP_R11_RET  : 0x19c9ba,  // 41 5b 41 (partial match)
    wk_POP_R12_RET  : 0x242ab15, // 41 5c c3
    wk_POP_R13_RET  : 0x6047b,   // 41 5d 41 5e 41 5f c3
    wk_POP_R14_RET  : 0xa9e91,
    wk_POP_R15_RET  : 0x6047f,
};
