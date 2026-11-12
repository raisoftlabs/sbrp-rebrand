#!/usr/bin/env python3
"""Shonar Bangla RP rebrand: app name, Bangladeshi icon set, green theme resources.

Usage:  python3 patch_apk.py <decoded_dir>

Env:
  LABEL      app name                    (default "Shonar Bangla RP")
  ART        legacy squircle artwork     (default artwork/icon.png)
  ART_ROUND  legacy round artwork        (default artwork/icon_round.png)
  ART_FG     adaptive foreground artwork (default artwork/icon_fg.png)
  FG_RATIO   foreground scale on canvas  (default 0.66)
"""
import glob
import os
import re
import sys

WORK = sys.argv[1] if len(sys.argv) > 1 else 'work'
LABEL = os.environ.get('LABEL', 'Shonar Bangla RP')
ART = os.environ.get('ART', 'artwork/icon.png')
ART_ROUND = os.environ.get('ART_ROUND', 'artwork/icon_round.png')
ART_FG = os.environ.get('ART_FG', 'artwork/icon_fg.png')
FG_RATIO = float(os.environ.get('FG_RATIO', '0.66'))

# Bangladeshi professional theme
BG_TOP = '#0E825C'      # bottle green (flag field, light end)
BG_BOT = '#003424'      # deep green (flag field, dark end)
WINDOW_LIGHT = '#F2F8F4'  # green-tinted white window background
WINDOW_DARK = '#0A1512'   # green-tinted near black

try:
    from PIL import Image
except Exception:
    Image = None


def rd(p):
    return open(p, encoding='utf-8', errors='replace').read()


def wr(p, s):
    open(p, 'w', encoding='utf-8').write(s)


def banner(t):
    print('\n' + '=' * 8 + ' ' + t + ' ' + '=' * 8)


def base_of(ref):
    return ref.split('/', 1)[1] if ref and ref.startswith('@') else None


# ---------------------------------------------------------------- manifest
manp = os.path.join(WORK, 'AndroidManifest.xml')
man = rd(manp)
m = re.search(r'<application\b[^>]*>', man)
apptag = m.group(0) if m else ''
banner('MANIFEST <application>')
print(apptag[:600])
icon_ref = re.search(r'android:icon="([^"]+)"', apptag)
round_ref = re.search(r'android:roundIcon="([^"]+)"', apptag)
print('icon ref      =', icon_ref and icon_ref.group(1))
print('roundIcon ref =', round_ref and round_ref.group(1))

names = set()
for r in (icon_ref, round_ref):
    b = base_of(r and r.group(1))
    if b:
        names.add(b)
names |= {'ic_launcher', 'ic_launcher_round'}

# ---------------------------------------------------------------- label
banner('APP LABEL -> ' + LABEL)
new_man = re.sub(r'(<application\b[^>]*?)android:label="[^"]*"',
                 r'\1android:label="' + LABEL + '"', man, count=1)
if 'android:label=' not in apptag:
    new_man = new_man.replace(apptag, apptag[:-1] + ' android:label="' + LABEL + '">', 1)
new_man = re.sub(r'(<activity\b[^>]*?)android:label="[^"]*"',
                 r'\1android:label="' + LABEL + '"', new_man)
if new_man != man:
    wr(manp, new_man)
    print('manifest label updated')
else:
    print('WARN: no label change applied')

for sp in glob.glob(os.path.join(WORK, 'res', 'values*', 'strings.xml')):
    t = rd(sp)
    t2 = t.replace('SA-MP Android', LABEL).replace('SA-MP  Android', LABEL)
    t2 = re.sub(r'(<string name="app_name"[^>]*>)[^<]*(</string>)', r'\1' + LABEL + r'\2', t2)
    if t2 != t:
        wr(sp, t2)
        print('strings updated:', os.path.relpath(sp, WORK))

# ---------------------------------------------------------------- adaptive icon
banner('ADAPTIVE ICON')
adaptive, fg_refs, bg_refs = [], set(), set()
for d in glob.glob(os.path.join(WORK, 'res', 'mipmap-anydpi*')):
    for f in glob.glob(os.path.join(d, '*.xml')):
        if os.path.basename(f).rsplit('.', 1)[0] not in names:
            continue
        adaptive.append(f)
        t = rd(f)
        for tag, store in (('foreground', fg_refs), ('background', bg_refs)):
            mm = re.search(r'<' + tag + r'\b[^>]*android:drawable="([^"]+)"', t)
            if mm:
                store.add(mm.group(1))
print('adaptive xml :', [os.path.relpath(f, WORK) for f in adaptive])
print('foreground   :', fg_refs)
print('background   :', bg_refs)

fg_bases = {b for b in (base_of(r) for r in fg_refs) if b}

# green gradient background layer
VECTOR = ('<?xml version="1.0" encoding="utf-8"?>\n'
          '<vector xmlns:android="http://schemas.android.com/apk/res/android"\n'
          '    xmlns:aapt="http://schemas.android.com/aapt"\n'
          '    android:width="108dp" android:height="108dp"\n'
          '    android:viewportWidth="108" android:viewportHeight="108">\n'
          '  <path android:pathData="M0,0h108v108h-108z">\n'
          '    <aapt:attr name="android:fillColor">\n'
          '      <gradient android:type="linear"\n'
          '          android:startX="0" android:startY="0"\n'
          '          android:endX="108" android:endY="108">\n'
          '        <item android:offset="0" android:color="' + BG_TOP + '"/>\n'
          '        <item android:offset="1" android:color="' + BG_BOT + '"/>\n'
          '      </gradient>\n'
          '    </aapt:attr>\n'
          '  </path>\n'
          '</vector>\n')

for ref in bg_refs:
    if ref.startswith('@drawable/'):
        nm = ref.split('/', 1)[1]
        for d in glob.glob(os.path.join(WORK, 'res', 'drawable*')):
            for f in glob.glob(os.path.join(d, nm + '.*')):
                ext = f.rsplit('.', 1)[1].lower()
                if ext == 'xml':
                    wr(f, VECTOR)
                    print('bg vector ->', BG_TOP, '->', BG_BOT, os.path.relpath(f, WORK))
                elif Image is not None and ext in ('webp', 'png'):
                    im = Image.open(f)
                    grad = Image.new('RGB', im.size)
                    px = grad.load()
                    w, h = im.size
                    for y in range(h):
                        for x in range(w):
                            t = (x + y) / (2.0 * max(1, w - 1))
                            px[x, y] = (int(14 + (0 - 14) * t),
                                        int(130 + (52 - 130) * t),
                                        int(92 + (36 - 92) * t))
                    grad.save(f, 'WEBP' if ext == 'webp' else 'PNG')
                    print('bg raster -> gradient', os.path.relpath(f, WORK), im.size)
    elif ref.startswith('@color/'):
        nm = ref.split('/', 1)[1]
        for c in glob.glob(os.path.join(WORK, 'res', 'values*', 'colors.xml')):
            t = rd(c)
            t2 = re.sub(r'(<color name="' + re.escape(nm) + r'"[^>]*>)[^<]*(</color>)',
                        r'\1' + BG_TOP + r'\2', t)
            if t2 != t:
                wr(c, t2)
                print('bg color', nm, '->', BG_TOP)

# ---------------------------------------------------------------- rasters
banner('ICON RASTERS')
if Image is None:
    print('Pillow missing -> cannot resize icons')
else:
    art = Image.open(ART).convert('RGBA')
    art_round = Image.open(ART_ROUND).convert('RGBA')
    art_fg = Image.open(ART_FG).convert('RGBA')
    print('artwork:', ART, art.size, '| round:', art_round.size, '| fg:', art_fg.size)

    targets = []
    for d in glob.glob(os.path.join(WORK, 'res', 'mipmap*')) + \
             glob.glob(os.path.join(WORK, 'res', 'drawable*')):
        for f in glob.glob(os.path.join(d, '*')):
            b = os.path.basename(f)
            if '.' not in b:
                continue
            stem, ext = b.rsplit('.', 1)
            if stem in names and ext.lower() in ('png', 'webp', 'jpg', 'jpeg'):
                targets.append(f)

    for f in sorted(targets):
        b = os.path.basename(f)
        stem, ext = b.rsplit('.', 1)
        ext = ext.lower()
        if stem in fg_bases:
            continue                      # handled below with the foreground art
        img = Image.open(f)
        w, h = img.size
        src = art_round if stem.endswith('round') else art
        out = src.resize((w, h), Image.LANCZOS)
        if ext == 'webp':
            out.save(f, 'WEBP', quality=95)
        elif ext in ('jpg', 'jpeg'):
            out.convert('RGB').save(f, 'JPEG', quality=95)
        else:
            out.save(f, 'PNG')
        print('  legacy ', os.path.relpath(f, WORK), f'{w}x{h}', ext)

    # adaptive foreground: art centred in the safe zone
    print('foreground bases:', fg_bases, 'ratio', FG_RATIO)
    for d in glob.glob(os.path.join(WORK, 'res', 'mipmap*')) + \
             glob.glob(os.path.join(WORK, 'res', 'drawable*')):
        for f in glob.glob(os.path.join(d, '*')):
            b = os.path.basename(f)
            if '.' not in b:
                continue
            stem, ext = b.rsplit('.', 1)
            ext = ext.lower()
            if stem not in fg_bases or ext not in ('png', 'webp'):
                continue
            img = Image.open(f)
            w, h = img.size
            canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
            side = int(min(w, h) * FG_RATIO)
            s = art_fg.resize((side, side), Image.LANCZOS)
            canvas.paste(s, ((w - side) // 2, (h - side) // 2), s)
            if ext == 'webp':
                canvas.save(f, 'WEBP', quality=95)
            else:
                canvas.save(f, 'PNG')
            print('  fg     ', os.path.relpath(f, WORK), f'{w}x{h}', ext)

# ---------------------------------------------------------------- theme colours
banner('THEME COLOURS')
for c in glob.glob(os.path.join(WORK, 'res', 'values*', 'colors.xml')):
    night = 'values-night' in c
    want = WINDOW_DARK if night else WINDOW_LIGHT
    t = rd(c)
    if '<color name="launcher_window_background"' not in t:
        continue
    t2 = re.sub(r'(<color name="launcher_window_background"[^>]*>)[^<]*(</color>)',
                r'\1' + want + r'\2', t)
    if t2 != t:
        wr(c, t2)
        print(os.path.relpath(c, WORK), '->', want)

banner('DONE')
