#!/usr/bin/env python3
"""Shonar Bangla RP rebrand: app name, Bangladeshi icon set, green theme resources.

Usage:  python3 patch_apk.py <decoded_dir>

Env:
  LABEL      app name                    (default "Shonar Bangla RP")
  ART        legacy squircle artwork     (default artwork/icon.png)
  ART_ROUND  legacy round artwork        (default artwork/icon_round.png)
  ART_FG     adaptive foreground artwork (default artwork/icon_fg.png)
  FG_RATIO   foreground scale on canvas  (default 0.66; >=0.999 = full bleed)
  MASK       apply squircle/circle alpha to legacy rasters (default 1)
  SQUIRCLE   squircle corner radius frac of legacy icon   (default 0.22)
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
MASK = os.environ.get('MASK', '1').lower() not in ('0', 'false', 'no')
SQUIRCLE = float(os.environ.get('SQUIRCLE', '0.22'))

# Bangladeshi professional theme
BG_TOP = '#0E825C'      # bottle green (flag field, light end)
BG_BOT = '#003424'      # deep green (flag field, dark end)
WINDOW_LIGHT = '#F2F8F4'  # green-tinted white window background
WINDOW_DARK = '#0A1512'   # green-tinted near black

try:
    from PIL import Image, ImageDraw
except Exception:
    Image = None
    ImageDraw = None


def rd(p):
    return open(p, encoding='utf-8', errors='replace').read()


def wr(p, s):
    open(p, 'w', encoding='utf-8').write(s)


def banner(t):
    print('\n' + '=' * 8 + ' ' + t + ' ' + '=' * 8)


def base_of(ref):
    return ref.split('/', 1)[1] if ref and ref.startswith('@') else None


def _rounded_mask(im, radius_frac):
    w, h = im.size
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle(
        [0, 0, w - 1, h - 1], radius=int(min(w, h) * radius_frac), fill=255)
    out = im.copy()
    out.putalpha(m)
    return out


def _circle_mask(im):
    w, h = im.size
    m = Image.new('L', (w, h), 0)
    ImageDraw.Draw(m).ellipse([0, 0, w - 1, h - 1], fill=255)
    out = im.copy()
    out.putalpha(m)
    return out


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

# ---------------------------------------------------------------- credits / about
banner('CREDITS / ABOUT PANEL')
CREDIT_EN = {
    'launcher_about_description': (
        'Shonar Bangla RP is a community rebrand of SA-MP Android \u2014 the '
        'excellent open-source SA-MP client for Android built by the '
        'SA-MP-Android developer (th1nk). All credit for the original app '
        'belongs to him: huge respect and heartfelt thanks for his hard work. '
        'Original project: github.com/SA-MP-Android'),
    'launcher_about_github': 'Original Developer \u00b7 GitHub',
    'launcher_about_telegram': 'Original Developer \u00b7 Telegram',
}
CREDIT_BN = {
    'launcher_about_description': (
        '\u09b6\u09cb\u09a8\u09be\u09b0 \u09ac\u09be\u0982\u09b2\u09be '
        '\u0986\u09b0\u09aa\u09bf \u2014 \u098f\u09b8\u098f\u09ae\u09aa\u09bf '
        '\u0985\u09cd\u09af\u09be\u09a8\u09cd\u09a1\u09cd\u09b0\u09df\u09c7\u09a1\u09c7\u09b0 '
        '\u098f\u0995\u099f\u09bf \u0995\u09ae\u09bf\u0989\u09a8\u09bf\u099f\u09bf '
        '\u09b0\u09bf\u09ac\u09cd\u09b0\u09cd\u09af\u09be\u09a8\u09cd\u09a1\u0964 '
        '\u09ae\u09c2\u09b2 \u0985\u09cd\u09af\u09be\u09aa\u099f\u09bf '
        '\u09a4\u09c8\u09b0\u09bf \u0995\u09b0\u09c7\u099b\u09c7\u09a8 '
        'SA-MP-Android \u09a1\u09c7\u09ad\u09c7\u09b2\u09aa\u09be\u09b0 '
        '(\u09a5\u09bf\u0982\u0995)\u0964 \u09a4\u09be\u0981\u09b0 '
        '\u0995\u09a0\u09cb\u09b0 \u09aa\u09b0\u09bf\u09b6\u09cd\u09b0\u09ae\u09c7\u09b0 '
        '\u099c\u09a8\u09cd\u09af \u0986\u09a8\u09cd\u09a4\u09b0\u09bf\u0995 '
        '\u0995\u09c3\u09a4\u099c\u09cd\u099e\u09a4\u09be \u0993 '
        '\u09b6\u09cd\u09b0\u09a6\u09cd\u09a7\u09be\u0964 '
        '\u09ae\u09c2\u09b2 \u09aa\u09cd\u09b0\u099c\u09c7\u0995\u09cd\u099f: '
        'github.com/SA-MP-Android'),
    'launcher_about_github': '\u09ae\u09c2\u09b2 \u09a1\u09c7\u09ad\u09c7\u09b2\u09aa\u09be\u09b0 \u00b7 GitHub',
    'launcher_about_telegram': '\u09ae\u09c2\u09b2 \u09a1\u09c7\u09ad\u09c7\u09b2\u09aa\u09be\u09b0 \u00b7 Telegram',
}


def esc_xml(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def apply_credit(path, table):
    t = rd(path)
    o = t
    for name, val in table.items():
        pat = r'(<string name="%s"[^>]*>)[^<]*(</string>)' % re.escape(name)
        t = re.sub(pat, lambda m: m.group(1) + esc_xml(val) + m.group(2), t)
    if t != o:
        wr(path, t)
        print('credits ->', os.path.relpath(path, WORK))
    return t != o


apply_credit(os.path.join(WORK, 'res', 'values', 'strings.xml'), CREDIT_EN)
for bn in glob.glob(os.path.join(WORK, 'res', 'values-bn', 'strings.xml')):
    t = rd(bn)
    if '</resources>' not in t:
        continue
    block = ''.join(
        '    <string name="%s">%s</string>\n' % (n, esc_xml(v))
        for n, v in CREDIT_BN.items()
        if ('name="%s"' % n) not in t)
    if block:
        wr(bn, t.replace('</resources>', block + '</resources>', 1))
        print('credits (bn) ->', os.path.relpath(bn, WORK))

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
        if MASK:
            out = _circle_mask(out) if stem.endswith('round') else _rounded_mask(out, SQUIRCLE)
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
            if FG_RATIO >= 0.999:
                canvas = art_fg.resize((w, h), Image.LANCZOS).convert('RGBA')
            else:
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

# ---------------------------------------------------------------- splash icon
banner('SPLASH ICON')
for st in glob.glob(os.path.join(WORK, 'res', 'values*', 'styles.xml')):
    t = rd(st)
    t2 = t.replace('@android:drawable/sym_def_app_icon', '@mipmap/ic_launcher')
    if t2 != t:
        wr(st, t2)
        print('splash icon -> @mipmap/ic_launcher  (%s)' % os.path.relpath(st, WORK))

# ---------------------------------------------------------------- bangla UI
banner('BANGLA UI STRINGS')
# Native Bangla (Unicode) for the most-visible UI strings. The stock app ships
# values-bn with only framework strings, so every launcher_* label fell back to
# English even on a Bangla locale. This fills the important ones in.
BN_UI = {
    # tabs
    'launcher_tab_home': 'হোম',
    'launcher_tab_servers': 'সার্ভার',
    'launcher_tab_resources': 'রিসোর্স',
    'launcher_tab_settings': 'সেটিংস',
    'launcher_tab_raksamp': 'রাকস্যাম্প',
    # home
    'launcher_home_title': LABEL,
    'launcher_home_heading': 'গেম লঞ্চার',
    'launcher_home_active_server': 'নির্বাচিত সার্ভার',
    'launcher_home_choose_server': 'একটি সার্ভার বেছে নিন',
    'launcher_home_manage_servers': 'সার্ভার ব্যবস্থাপনা',
    'launcher_home_no_server_title': 'কোনো সংরক্ষিত সার্ভার নেই',
    'launcher_home_no_server_description': 'সংযোগ কনফিগার করতে ও গেম চালু করতে একটি সার্ভার যোগ করুন।',
    'launcher_home_resources_ready': 'রিসোর্স প্রস্তুত',
    'launcher_home_resources_not_checked': 'রিসোর্স পরীক্ষা করা হয়নি',
    'launcher_home_resources_checking': 'রিসোর্স পরীক্ষা করা হচ্ছে',
    'launcher_home_resources_checking_description': 'প্রয়োজনীয় গেম ফাইল পরীক্ষা করা হচ্ছে',
    'launcher_home_resources_complete': 'প্রয়োজনীয় গেম ফাইল পাওয়া গেছে',
    'launcher_home_resources_not_ready': 'রিসোর্স অনুপলব্ধ',
    'launcher_home_resources_check_description': 'গেম ফাইল পরীক্ষা করতে রিসোর্স ব্যবস্থাপনা খুলুন',
    'launcher_home_resources_error_description': 'ফলাফল দেখতে রিসোর্স ব্যবস্থাপনা খুলুন',
    'launcher_home_select_prompt': 'কোনো সার্ভার নির্বাচিত হয়নি',
    'launcher_home_select_description': 'সংযোগ করতে একটি সংরক্ষিত সার্ভার নির্বাচন করুন।',
    'launcher_home_server_library': 'সার্ভার ব্যবস্থাপনা',
    'launcher_home_switch_server': 'সার্ভার পরিবর্তন',
    'launcher_home_welcome': 'ডাকনাম: %1$s',
    # actions
    'launcher_action_add_server': 'সার্ভার যোগ করুন',
    'launcher_action_back': 'পেছনে',
    'launcher_action_cancel': 'বাতিল',
    'launcher_action_check_resources': 'রিসোর্স পরীক্ষা করুন',
    'launcher_action_clear_filters': 'ফিল্টার মুছুন',
    'launcher_action_clear_search': 'সার্চ মুছুন',
    'launcher_action_close': 'বন্ধ করুন',
    'launcher_action_copy': 'কপি করুন',
    'launcher_action_delete': 'মুছুন',
    'launcher_action_download': 'ডাউনলোড',
    'launcher_action_enter_game': 'গেমে প্রবেশ করুন',
    'launcher_action_extract': 'এক্সট্রাক্ট করুন',
    'launcher_action_favorite': 'প্রিয়তে যোগ করুন',
    'launcher_action_fetch_sources': 'সোর্স আনুন',
    'launcher_action_hide_details': 'বিস্তারিত লুকান',
    'launcher_action_import_local_zip': 'লোকাল জিপ ইমপোর্ট করুন',
    'launcher_action_launch': 'চালু করুন',
    'launcher_action_more': 'আরও',
    'launcher_action_players': 'খেলোয়াড়',
    'launcher_action_refresh': 'রিফ্রেশ',
    'launcher_action_remove': 'সরান',
    'launcher_action_restore_default': 'ডিফল্টে ফিরিয়ে নিন',
    'launcher_action_retry': 'আবার চেষ্টা করুন',
    'launcher_action_rules': 'নিয়মাবলী',
    'launcher_action_save': 'সংরক্ষণ করুন',
    'launcher_action_show_details': 'বিস্তারিত দেখান',
    'launcher_action_unfavorite': 'প্রিয় থেকে সরান',
    'launcher_action_view_chat_log': 'চ্যাট লগ দেখুন',
    'launcher_action_view_launcher_log': 'লঞ্চার লগ দেখুন',
    'launcher_action_view_samp_log': 'স্যাম্প লগ দেখুন',
    # servers
    'launcher_servers_description': 'একটি সার্ভার নির্বাচন করে খেলা শুরু করুন।',
    'launcher_servers_empty_title': 'কোনো সার্ভার নেই',
    'launcher_servers_empty_message': 'শুরু করতে একটি সার্ভার যোগ করুন।',
    'launcher_servers_search_label': 'সার্ভার খুঁজুন',
    'launcher_servers_filter_all': 'সব',
    'launcher_servers_filter_favorites': 'প্রিয়',
    'launcher_servers_tab_saved': 'সংরক্ষিত',
    'launcher_servers_tab_recommended': 'প্রস্তাবিত',
    'launcher_servers_density_compact': 'সংক্ষিপ্ত',
    'launcher_servers_density_comfortable': 'আরামদায়ক',
    'launcher_recommended_header_title': 'প্রস্তাবিত সার্ভার',
    'launcher_recommended_empty_title': 'কিছু পাওয়া যায়নি',
    'launcher_recommended_added': 'সার্ভার যোগ করা হয়েছে',
    'launcher_label_server_host': 'সার্ভার ঠিকানা',
    'launcher_label_server_port': 'পোর্ট',
    'launcher_label_server_password': 'পাসওয়ার্ড',
    'launcher_label_nickname': 'ডাকনাম',
    'launcher_add_server_title': 'সার্ভার যোগ করুন',
    'launcher_add_server_default_port_help': 'ডিফল্ট পোর্ট ৭৭৭৭',
    'launcher_server_players_label': 'খেলোয়াড়',
    'launcher_server_ping_label': 'পিং',
    # settings
    'launcher_settings_intro': 'অ্যাপটি আপনার পছন্দমতো সাজিয়ে নিন।',
    'launcher_settings_general_title': 'সাধারণ',
    'launcher_settings_appearance_title': 'অ্যাপিয়ারেন্স',
    'launcher_settings_ingame_title': 'ইন-গেম',
    'launcher_settings_notifications_title': 'নোটিফিকেশন',
    'launcher_settings_debug_title': 'ডিবাগ',
    'launcher_settings_about_title': 'সম্পর্কে',
    'launcher_settings_section_client': 'ক্লায়েন্ট',
    'launcher_settings_section_display': 'ডিসপ্লে',
    'launcher_settings_section_experience': 'অভিজ্ঞতা',
    'launcher_settings_section_input': 'ইনপুট',
    'launcher_settings_section_language': 'ভাষা',
    'launcher_settings_section_tools': 'টুলস',
    'launcher_settings_section_updates': 'আপডেট',
    'launcher_label_language': 'ভাষা',
    'launcher_label_theme_mode': 'থিম মোড',
    'launcher_label_theme_color': 'থিম রঙ',
    'launcher_label_dynamic_color': 'মনেট ডায়নামিক রঙ',
    'launcher_label_font_size': 'ফন্ট সাইজ: %1$dsp',
    'launcher_label_client_version': 'স্যাম্প ক্লায়েন্ট ভার্সন',
    'launcher_label_client_version_name': 'ক্লায়েন্ট ভার্সনের নাম',
    'launcher_label_nickname': 'ডাকনাম',
    'launcher_label_show_fps': 'FPS দেখান',
    'launcher_label_show_chat_timestamp': 'চ্যাটে সময় দেখান',
    'launcher_label_native_keyboard': 'নেটিভ কীবোর্ড ব্যবহার করুন',
    'launcher_label_bottom_bar': 'নিচের নেভিগেশন',
    'launcher_label_fps_limit': 'ফ্রেম রেট সীমা',
    # about
    'launcher_about_check_update': 'আপডেট দেখুন',
    'launcher_about_checking_update': 'আপডেট দেখা হচ্ছে…',
    'launcher_about_up_to_date': 'আপনি সর্বশেষ ভার্সনে আছেন',
    'launcher_about_update_available': 'নতুন আপডেট পাওয়া গেছে',
    'launcher_about_update_failed': 'আপডেট দেখা ব্যর্থ হয়েছে',
    'launcher_about_version_value': 'ভার্সন %1$s',
    # resources
    'launcher_resources_check_title': 'রিসোর্স পরীক্ষা',
    'launcher_resources_official_list': 'অফিসিয়াল তালিকা',
    'launcher_resources_not_ready': 'রিসোর্স প্রস্তুত নয়',
    'launcher_resources_section_game': 'গেম',
    'launcher_resources_section_cleo': 'ক্লিও',
    'launcher_resources_section_monet': 'মনেট',
    # logs
    'launcher_log_refresh': 'রিফ্রেশ',
    'launcher_log_clear': 'মুছুন',
    'launcher_log_copied': 'কপি হয়েছে',
    'launcher_log_cleared': 'মুছে ফেলা হয়েছে',
}

bn_paths = glob.glob(os.path.join(WORK, 'res', 'values-bn', 'strings.xml'))
if not bn_paths:
    print('WARN: no values-bn/strings.xml found')
for bn in bn_paths:
    t = rd(bn)
    if '</resources>' not in t:
        print('WARN: %s has no </resources>' % bn)
        continue
    block = []
    for name, val in BN_UI.items():
        pat = r'(<string name="%s"[^>]*>)[^<]*(</string>)' % re.escape(name)
        if re.search(pat, t):
            t = re.sub(pat, lambda m: m.group(1) + esc_xml(val) + m.group(2), t)
        else:
            block.append('    <string name="%s">%s</string>\n' % (name, esc_xml(val)))
    if block:
        t = t.replace('</resources>', ''.join(block) + '</resources>', 1)
    wr(bn, t)
    print('bangla UI ->', os.path.relpath(bn, WORK), '| strings:', len(BN_UI))

banner('DONE')
