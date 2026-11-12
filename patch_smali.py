#!/usr/bin/env python3
"""Patch the Bangladeshi theme colours directly in a FULL smali decode.

Use when the pipeline decodes WITHOUT `-s` (i.e. smali is present). Replaces
the 8-hex-digit colour literals in `const`/`const-wide` instructions. Keeps the
same approach as patch_dex.py (which only works on a verbatim classes.dex).

Usage:  python3 patch_smali.py <decoded_dir>
"""
import glob
import os
import sys

WORK = sys.argv[1] if len(sys.argv) > 1 else 'work'

# old -> new (must stay 0x-prefixed 8 hex digits so the match is exact)
COLOURS = {
    '0xff253c57': '0xff006a4e',  # navy seed -> BD bottle green
    '0xff006a6a': '0xffb3261e',  # teal  -> flag red
    '0xff386a20': '0xffa67c00',  # green -> sonar gold
    '0xff6750a4': '0xff0b5fa5',  # purple-> professional blue
    '0xff8b5000': '0xff5b3e96',  # amber -> violet
    '0xff173b59': '0xff0b4a35',
    '0xff223e55': '0xff14503a',
    '0xff2c3c4c': '0xff1e3d31',
    '0xff2a3a49': '0xff1c3a2f',
    '0xff111c27': '0xff0a1f18',
    '0xff536373': '0xff4c6b5e',
    '0xffa9cff2': '0xffa3d9c2',
    '0xffb2c7d9': '0xffb0cbbd',
    '0xffa6b7c7': '0xffaac6b8',
    '0xffdceaf6': '0xffddf1e7',
    '0xffd8e1ea': '0xffd9ece2',
    '0xffe1eaf3': '0xffe3f2ea',
}


def main():
    files = glob.glob(os.path.join(WORK, 'smali*', '**', '*.smali'), recursive=True)
    if not files:
        raise SystemExit('no smali found under %s/ (did you decode with -s?)' % WORK)
    hits = {c: 0 for c in COLOURS}
    changed = 0
    for f in files:
        t = open(f, encoding='utf-8', errors='replace').read()
        o = t
        for a, b in COLOURS.items():
            if a in t:
                hits[a] += t.count(a)
                t = t.replace(a, b)
        if t != o:
            open(f, 'w', encoding='utf-8').write(t)
            changed += 1
    total = sum(hits.values())
    print('smali files scanned:', len(files), '| changed:', changed,
          '| literals replaced:', total)
    for a, n in hits.items():
        if n:
            print('  %s -> %s  x%d' % (a, COLOURS[a], n))


if __name__ == '__main__':
    main()
