#!/usr/bin/env python3
"""Patch the Bangladeshi theme + branding/code fixes in a FULL smali decode.

Use when the pipeline decodes WITHOUT `-s` (i.e. smali is present). Does three
things:

  1. COLOURS   - replaces the 8-hex-digit colour literals (const/const-wide)
                 with the BD professional palette (same map as patch_dex.py).
  2. URLS      - repoints remote endpoints:
                   * in-app updater  -> our own rebrand repo
                   * recommended servers list -> our own hosted servers.json
                 (the th1nk.top game-data endpoints are LEFT ALONE on purpose:
                  they host the GTA SA game files the client must download.)
  3. CODE      - removes the RAKSAMP tab from the bottom-bar enum array.

Usage:  python3 patch_smali.py <decoded_dir>
"""
import glob
import os
import re
import sys

WORK = sys.argv[1] if len(sys.argv) > 1 else 'work'

OUR_REPO = os.environ.get('OUR_REPO', 'raisoftlabs/sbrp-rebrand')
OUR_BRANCH = os.environ.get('OUR_BRANCH', 'main')

# ---------------------------------------------------------------- 1. colours
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

# ---------------------------------------------------------------- 2. urls
URLS = {
    # in-app update checker -> our rebrand repo (needs semver tags + an
    # `app-arm64-v8a-release.apk` asset on the release, see the workflow).
    'https://api.github.com/repos/SA-MP-Android/App/releases?per_page=100':
        'https://api.github.com/repos/%s/releases?per_page=100' % OUR_REPO,
    'https://api.github.com/repos/SA-MP-Android/App/releases/latest':
        'https://api.github.com/repos/%s/releases/latest' % OUR_REPO,
    # recommended-server list -> our own file (so the SBRP entry shows up).
    'https://sa-mp.th1nk.top/data/servers.json':
        'https://raw.githubusercontent.com/%s/%s/data/servers.json' % (OUR_REPO, OUR_BRANCH),
}

# ---------------------------------------------------------------- 3. code
# (marker in file, old snippet, new snippet) - applied only to the FIRST file
# that contains `marker`, so we never touch unrelated classes.
CODE = [
    # bottom-bar tab enum: drop the RakSamp entry from the values() array.
    # Home=0 Servers=1 Resources=2 RakSamp=3 Settings=4  ->  drop v3.
    ('const-string v6, "RakSamp"',
     'filled-new-array {v0, v1, v2, v3, v4}, [L',
     'filled-new-array {v0, v1, v2, v4}, [L'),
]


def patch_urls(files):
    hits = {u: 0 for u in URLS}
    changed = 0
    for f in files:
        t = open(f, encoding='utf-8', errors='replace').read()
        o = t
        for a, b in URLS.items():
            if a in t:
                hits[a] += t.count(a)
                t = t.replace(a, b)
        if t != o:
            open(f, 'w', encoding='utf-8').write(t)
            changed += 1
    print('URL rewrites: %d literals in %d files' % (sum(hits.values()), changed))
    for a, n in hits.items():
        if n:
            print('  %s\n    -> %s  x%d' % (a, URLS[a], n))


def patch_code(files):
    for marker, old, new in CODE:
        target = None
        for f in files:
            if marker in open(f, encoding='utf-8', errors='replace').read():
                target = f
                break
        if not target:
            print('CODE: marker not found (skip): %s' % marker)
            continue
        t = open(target, encoding='utf-8', errors='replace').read()
        if old not in t:
            print('CODE: snippet not found in %s (skip)' % os.path.relpath(target, WORK))
            continue
        open(target, 'w', encoding='utf-8').write(t.replace(old, new, 1))
        print('CODE: %s -> dropped RakSamp tab' % os.path.relpath(target, WORK))


def main():
    files = glob.glob(os.path.join(WORK, 'smali*', '**', '*.smali'), recursive=True)
    if not files:
        raise SystemExit('no smali found under %s/ (did you decode with -s?)' % WORK)
    print('smali files scanned:', len(files))

    print('\n--- 1. theme colours ---')
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
    print('changed: %d files | literals replaced: %d' % (changed, sum(hits.values())))
    for a, n in hits.items():
        if n:
            print('  %s -> %s  x%d' % (a, COLOURS[a], n))

    print('\n--- 2. remote endpoints ---')
    patch_urls(files)

    print('\n--- 3. code patches ---')
    patch_code(files)


if __name__ == '__main__':
    main()
