#!/usr/bin/env python3
"""Rebrand the decoded SA-MP-Android APK tree: app name + launcher icon.

Usage:  python3 patch_apk.py <decoded_dir>
Env:    LABEL      app name          (default "Shonar Bangla RP")
        ART        artwork png       (default artwork/icon.png)
        ICON_BG    adaptive bg color (default "#000000")
"""
import os, re, sys, glob

WORK  = sys.argv[1] if len(sys.argv) > 1 else 'work'
ART   = os.environ.get('ART', 'artwork/icon.png')
LABEL = os.environ.get('LABEL', 'Shonar Bangla RP')
ICON_BG = os.environ.get('ICON_BG', '#000000')

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
    if ref and ref.startswith('@'):
        return ref.split('/', 1)[1]
    return None


# ---------------------------------------------------------------- manifest
manp = os.path.join(WORK, 'AndroidManifest.xml')
man = rd(manp)
m = re.search(r'<application\b[^>]*>', man)
apptag = m.group(0) if m else ''
banner('MANIFEST <application>')
print(apptag[:800])
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
# force a literal label on <application> and any activity that carries one
new_man = re.sub(r'(<application\b[^>]*?)android:label="[^"]*"',
                 r'\1android:label="' + LABEL + '"', man, count=1)
if 'android:label=' not in apptag:
    new_man = new_man.replace(apptag, apptag[:-1] + ' android:label="' + LABEL + '">', 1)
# launcher activity label
new_man = re.sub(r'(<activity\b[^>]*?)android:label="[^"]*"',
                 r'\1android:label="' + LABEL + '"', new_man)
if new_man != man:
    wr(manp, new_man)
    print('manifest label updated')
else:
    print('WARN: no label change applied')

# also nuke the string resources so anything reading @string/app_name matches
for sp in glob.glob(os.path.join(WORK, 'res', 'values*', 'strings.xml')):
    t = rd(sp)
    t2 = t.replace('SA-MP Android', LABEL).replace('SA-MP  Android', LABEL)
    # explicit app_name
    t2 = re.sub(r'(<string name="app_name"[^>]*>)[^<]*(</string>)',
                r'\1' + LABEL + r'\2', t2)
    if t2 != t:
        wr(sp, t2)
        print('strings updated:', os.path.relpath(sp, WORK))

# ---------------------------------------------------------------- icon files
banner('ICON RASTERS')
print('icon resource names to replace:', sorted(names))
targets = []
for d in glob.glob(os.path.join(WORK, 'res', 'mipmap*')) + \
         glob.glob(os.path.join(WORK, 'res', 'drawable*')):
    for f in glob.glob(os.path.join(d, '*')):
        b = os.path.basename(f)
        if '.' not in b:
            continue
        stem, ext = b.rsplit('.', 1)
        ext = ext.lower()
        if stem in names and ext in ('png', 'webp', 'jpg', 'jpeg'):
            targets.append(f)
for f in sorted(targets):
    print('  ', os.path.relpath(f, WORK))

if Image is None:
    banner('PIL MISSING')
    print('Pillow not installed -> cannot resize icons. (pip install pillow)')
else:
    art = Image.open(ART).convert('RGBA')
    for f in targets:
        stem, ext = os.path.basename(f).rsplit('.', 1)
        ext = ext.lower()
        img = Image.open(f)
        w, h = img.size
        # adaptive foregrounds live in mipmap-* with a bigger canvas
        out = art.resize((w, h), Image.LANCZOS)
        if ext == 'webp':
            out.save(f, 'WEBP', quality=95)
        elif ext in ('jpg', 'jpeg'):
            out.convert('RGB').save(f, 'JPEG', quality=95)
        else:
            out.save(f, 'PNG')
        print('  wrote', os.path.relpath(f, WORK), f'{w}x{h}', ext)

# ---------------------------------------------------------------- adaptive icon
banner('ADAPTIVE ICON (mipmap-anydpi-v26)')
adaptive = []
for d in glob.glob(os.path.join(WORK, 'res', 'mipmap-anydpi*')):
    adaptive += [f for f in glob.glob(os.path.join(d, '*.xml'))
                 if os.path.basename(f).rsplit('.', 1)[0] in names]
print('adaptive xml:', [os.path.relpath(f, WORK) for f in adaptive])

fg_names, bg_refs = set(), set()
for f in adaptive:
    t = rd(f)
    print('---', os.path.relpath(f, WORK))
    print(t.strip()[:500])
    for tag, store in (('foreground', fg_names), ('background', bg_refs)):
        mm = re.search(r'<' + tag + r'\b[^>]*android:drawable="([^"]+)"', t)
        if mm:
            store.add(mm.group(1))
print('foreground refs:', fg_names)
print('background refs:', bg_refs)

# black background color for the adaptive layer
if bg_refs:
    for c in glob.glob(os.path.join(WORK, 'res', 'values*', 'colors.xml')):
        t = rd(c)
        for ref in bg_refs:
            if ref.startswith('@color/'):
                nm = ref.split('/', 1)[1]
                if f'<color name="{nm}"' in t:
                    t = re.sub(r'(<color name="' + re.escape(nm) + r'"[^>]*>)[^<]*(</color>)',
                               r'\1' + ICON_BG + r'\2', t)
                    print('color', nm, '->', ICON_BG)
        wr(c, t)

# foreground raster replacement (safe zone: art at 66% of canvas, centered)
if Image is not None:
    fg_bases = {base_of(r) for r in fg_names}
    fg_bases.discard(None)
    print('foreground bases:', fg_bases)
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
            side = int(min(w, h) * 0.66)
            art_s = art.resize((side, side), Image.LANCZOS)
            canvas.paste(art_s, ((w - side) // 2, (h - side) // 2), art_s)
            if ext == 'webp':
                canvas.save(f, 'WEBP', quality=95)
            else:
                canvas.save(f, 'PNG')
            print('  fg wrote', os.path.relpath(f, WORK), f'{w}x{h}')

banner('DONE')
