#!/usr/bin/env python3
"""Bangladeshi re-theme for the SA-MP-Android dex (binary patch, no smali rebuild).

The app derives its whole Material-3 palette from a single seed colour
(`rememberDynamicColorScheme`, MaterialKolor) plus a hardcoded light/dark
fallback scheme. Both are plain `const-wide` colour literals inside classes.dex,
so we patch the 8-byte little-endian values in place and re-stamp the dex
header (SHA-1 signature + Adler-32 checksum) so ART accepts the file.

Usage:  python3 patch_dex.py <decoded_dir> [<base.apk>]
"""
import glob
import hashlib
import os
import struct
import sys
import zlib

# ---------------------------------------------------------------- palette
# old navy theme  ->  Bangladeshi professional
COLORS = {
    # --- default seed / "Standard" preset / fallback scheme seed
    0xff253c57: 0xff006a4e,   # navy        -> Bangladesh bottle green

    # --- extra theme presets offered in Settings > Appearance
    0xff006a6a: 0xffb3261e,   # teal        -> deep flag red
    0xff386a20: 0xffa67c00,   # green       -> sonar gold
    0xff6750a4: 0xff0b5fa5,   # purple      -> professional blue
    0xff8b5000: 0xff5b3e96,   # amber       -> violet

    # --- hardcoded fallback ColorScheme (light + dark), hy.smali
    0xff173b59: 0xff0b4a35,
    0xff223e55: 0xff14503a,
    0xff2c3c4c: 0xff1e3d31,
    0xff2a3a49: 0xff1c3a2f,
    0xff111c27: 0xff0a1f18,
    0xff536373: 0xff4c6b5e,
    0xffa9cff2: 0xffa3d9c2,
    0xffb2c7d9: 0xffb0cbbd,
    0xffa6b7c7: 0xffaac6b8,
    0xffdceaf6: 0xffddf1e7,
    0xffd8e1ea: 0xffd9ece2,
    0xffe1eaf3: 0xffe3f2ea,
}


def find_dex(work, base_apk=None):
    """Locate the dex in an apktool --no-src tree."""
    cands = []
    for pat in ('*.dex', '*/*.dex', '*/*/*.dex'):
        cands += glob.glob(os.path.join(work, pat))
    cands = [c for c in cands if 'smali' not in c]
    if cands:
        return sorted(cands, key=len)[0]
    return None


def patch_dex(path):
    d = bytearray(open(path, 'rb').read())
    if bytes(d[:4]) != b'dex\n':
        raise SystemExit(f'{path}: not a dex file')
    total = 0
    for old, new in COLORS.items():
        ob = struct.pack('<Q', old)
        nb = struct.pack('<Q', new)
        n = d.count(ob)
        if n:
            d = bytearray(bytes(d).replace(ob, nb))
            total += n
        print(f'  0x{old:08x} -> 0x{new:08x}   x{n}')
    if not total:
        raise SystemExit('no colour constants replaced - aborting')

    # re-stamp dex header: SHA-1 signature over bytes[32:], then Adler-32 checksum
    d[12:32] = hashlib.sha1(bytes(d[32:])).digest()
    struct.pack_into('<I', d, 8, zlib.adler32(bytes(d[12:])) & 0xffffffff)
    open(path, 'wb').write(bytes(d))
    print(f'  patched {total} literals, dex header re-stamped')
    return total


def main():
    work = sys.argv[1] if len(sys.argv) > 1 else 'work'
    base = sys.argv[2] if len(sys.argv) > 2 else None
    dex = find_dex(work, base)
    if not dex:
        raise SystemExit(f'no .dex found under {work}/ (apktool -s keeps it at the root)')
    print('dex:', dex, f'({os.path.getsize(dex):,} bytes)')
    patch_dex(dex)


if __name__ == '__main__':
    main()
