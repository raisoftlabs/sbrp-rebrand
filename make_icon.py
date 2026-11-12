#!/usr/bin/env python3
"""Shonar Bangla RP launcher icons - Bangladeshi professional theme.

Pure python (no Pillow) so it also runs on the phone.

Renders into artwork/:
  icon.png        squircle  -> legacy ic_launcher
  icon_round.png  circle    -> legacy ic_launcher_round
  icon_fg.png     transparent sun+ring -> adaptive foreground layer

Palette (Bangladesh flag, professional tones):
  bottle green  #0E825C -> #003424   (flag field, gradient)
  flag red      #F42A41              (the sun)
  sonar gold    #E9B949              (premium ring, "Sonar Bangla")
"""
import math
import os
import struct
import zlib

SIZE = 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'artwork')

GREEN_TOP = (18, 134, 95)
GREEN_BOT = (0, 52, 36)
RED = (244, 42, 65)
RED_HI = (255, 122, 133)
GOLD = (233, 185, 73)


def clamp(v, lo=0.0, hi=1.0):
    return lo if v < lo else (hi if v > hi else v)


def smoothstep(e0, e1, x):
    t = clamp((x - e0) / (e1 - e0))
    return t * t * (3.0 - 2.0 * t)


def mix(a, b, t):
    return (a[0] + (b[0] - a[0]) * t,
            a[1] + (b[1] - a[1]) * t,
            a[2] + (b[2] - a[2]) * t)


def save_png(path, w, h, px):
    rows = bytearray()
    for y in range(h):
        rows.append(0)
        base = y * w
        for x in range(w):
            p = px[base + x]
            rows += bytes((int(p[0]), int(p[1]), int(p[2]), int(p[3])))

    def chunk(t, data):
        return struct.pack('>I', len(data)) + t + data + \
            struct.pack('>I', zlib.crc32(t + data) & 0xffffffff)

    out = b'\x89PNG\r\n\x1a\n'
    out += chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
    out += chunk(b'IDAT', zlib.compress(bytes(rows), 9))
    out += chunk(b'IEND', b'')
    open(path, 'wb').write(out)


def render(shape, sun_radius, bg_on, sun_on):
    """shape: 'squircle' | 'circle' | 'none'. Returns flat RGBA list."""
    cx = cy = SIZE / 2.0
    sun_r = sun_radius * SIZE
    ring_w = 0.0155 * SIZE
    ring_r = sun_r + ring_w * 0.62
    rad = 0.235 * SIZE                      # squircle corner radius
    inv2s2 = 1.0 / (2.0 * (0.46 * SIZE) ** 2)   # gloss falloff
    gx, gy = 0.31 * SIZE, 0.25 * SIZE           # gloss centre
    px = [None] * (SIZE * SIZE)

    for y in range(SIZE):
        ty = y / SIZE
        for x in range(SIZE):
            tx = x / SIZE

            if bg_on:
                # diagonal green gradient
                t = 0.55 * ty + 0.45 * tx
                col = (GREEN_TOP[0] + (GREEN_BOT[0] - GREEN_TOP[0]) * t,
                       GREEN_TOP[1] + (GREEN_BOT[1] - GREEN_TOP[1]) * t,
                       GREEN_TOP[2] + (GREEN_BOT[2] - GREEN_TOP[2]) * t)
                # soft specular gloss, upper-left
                dx, dy = x - gx, y - gy
                g = math.exp(-(dx * dx + dy * dy) * inv2s2) * 0.30
                col = mix(col, (255, 255, 255), g)
                # vignette for depth
                vx, vy = (x - cx) / (0.78 * SIZE), (y - cy) / (0.78 * SIZE)
                v = smoothstep(0.52, 1.10, math.sqrt(vx * vx + vy * vy)) * 0.26
                col = mix(col, (0, 18, 12), v)
                a = 255.0
            else:
                col = (0.0, 0.0, 0.0)
                a = 0.0

            if sun_on:
                d = math.hypot(x - cx, y - cy)
                # the flag sun
                sc = 1.0 - smoothstep(sun_r - 1.0, sun_r + 1.0, d)
                if sc > 0.0:
                    sun = mix(RED, RED_HI, smoothstep(sun_r * 0.62, sun_r * 0.02, d) * 0.55)
                    col = mix(col, sun, sc)
                # gold premium ring
                rc = 1.0 - smoothstep(ring_w * 0.5, ring_w * 0.5 + 1.0, abs(d - ring_r))
                if rc > 0.0:
                    col = mix(col, GOLD, rc)
                if not bg_on:
                    # foreground layer: alpha follows the drawn mark
                    a = 255.0 * max(sc, rc)

            if shape != 'none':
                if shape == 'circle':
                    sd = math.hypot(x - cx, y - cy) - SIZE * 0.5
                else:  # squircle / rounded rect
                    hx = abs(x - cx) - (SIZE * 0.5 - rad)
                    hy = abs(y - cy) - (SIZE * 0.5 - rad)
                    qx = hx if hx > 0.0 else 0.0
                    qy = hy if hy > 0.0 else 0.0
                    sd = math.hypot(qx, qy) + (min(max(hx, hy), 0.0)) - rad
                a *= 1.0 - smoothstep(-1.0, 1.0, sd)

            px[y * SIZE + x] = (col[0], col[1], col[2], a)
    return px


def main():
    import sys
    only = sys.argv[1] if len(sys.argv) > 1 else 'all'
    os.makedirs(OUT, exist_ok=True)

    if only in ('all', 'legacy'):
        print('rendering icon.png (squircle)...')
        px = render('squircle', 0.300, True, True)
        save_png(os.path.join(OUT, 'icon.png'), SIZE, SIZE, px)

        print('rendering icon_round.png (circle)...')
        px = render('circle', 0.300, True, True)
        save_png(os.path.join(OUT, 'icon_round.png'), SIZE, SIZE, px)

    if only in ('all', 'fg'):
        print('rendering icon_fg.png (adaptive foreground)...')
        px = render('none', 0.375, False, True)
        save_png(os.path.join(OUT, 'icon_fg.png'), SIZE, SIZE, px)

    for f in ('icon.png', 'icon_round.png', 'icon_fg.png'):
        p = os.path.join(OUT, f)
        if os.path.exists(p):
            print(f'  {f}: {os.path.getsize(p):,} bytes')


if __name__ == '__main__':
    main()
