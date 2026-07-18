"""Render a branded header card for each post using Pillow (no image API needed).

Four selectable styles — set STYLE (or pass style=) to pick:
  "midnight"  - dark purple gradient, glow, news chip
  "editorial" - light magazine look, big serif headline
  "terminal"  - dark hacker/terminal window, monospace neon text
  "poster"    - loud electric gradient, huge tilted-feel type

Cards are drawn at 2x resolution and downscaled for crisp text.
"""

import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1600, 900
SCALE = 2

STYLE = "midnight"  # default style used by main.py
BRAND = "AI PULSE"
TAG = "AI NEWS"

SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def _font(path: str, size: int):
    if Path(path).exists():
        return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _wrap(draw, text: str, font, max_width: int) -> list[str]:
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit(draw, text, font_path, max_width, max_lines, start=96, floor=42):
    for size in range(start * SCALE, floor * SCALE, -4 * SCALE):
        font = _font(font_path, size)
        lines = _wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return lines, font, size
    font = _font(font_path, floor * SCALE)
    return _wrap(draw, text, font, max_width)[:max_lines], font, floor * SCALE


def _vertical_gradient(draw, w, h, top, bottom):
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))


def _new_canvas():
    img = Image.new("RGB", (WIDTH * SCALE, HEIGHT * SCALE))
    return img, ImageDraw.Draw(img, "RGBA")


def _finish(img, out_path):
    img.resize((WIDTH, HEIGHT), Image.LANCZOS).save(out_path, "PNG")
    return out_path


# ---------------------------------------------------------------- styles


def _style_midnight(headline, subheadline, out_path):
    w, h, m = WIDTH * SCALE, HEIGHT * SCALE, 90 * SCALE
    img, draw = _new_canvas()
    _vertical_gradient(draw, w, h, (13, 15, 32), (44, 24, 74))

    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([w * 0.68, -h * 0.35, w * 1.15, h * 0.45], fill=(124, 77, 255))
    gd.ellipse([-w * 0.15, h * 0.75, w * 0.25, h * 1.3], fill=(200, 110, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(180 * SCALE))
    img = Image.blend(img, Image.composite(glow, img, glow.convert("L")), 0.35)
    draw = ImageDraw.Draw(img, "RGBA")

    for gx in range(int(w * 0.62), w - 30 * SCALE, 46 * SCALE):
        for gy in range(40 * SCALE, int(h * 0.42), 46 * SCALE):
            draw.ellipse([gx, gy, gx + 5 * SCALE, gy + 5 * SCALE], fill=(255, 255, 255, 28))

    brand_font = _font(SANS_BOLD, 42 * SCALE)
    draw.text((m, 66 * SCALE), BRAND, font=brand_font, fill=(255, 176, 92))
    draw.line(
        [(m, 128 * SCALE), (m + draw.textlength(BRAND, font=brand_font), 128 * SCALE)],
        fill=(255, 176, 92), width=5 * SCALE,
    )

    chip_font = _font(SANS_BOLD, 30 * SCALE)
    tag_w = draw.textlength(TAG, font=chip_font)
    cx1, cx0 = w - m, w - m - tag_w - 56 * SCALE
    draw.rounded_rectangle([cx0, 62 * SCALE, cx1, 122 * SCALE], radius=30 * SCALE,
                           fill=(255, 255, 255, 26), outline=(255, 255, 255, 70), width=2 * SCALE)
    draw.text((cx0 + 28 * SCALE, 74 * SCALE), TAG, font=chip_font, fill=(255, 255, 255))
    date_text = time.strftime("%b %d, %Y").upper()
    draw.text((cx1 - draw.textlength(date_text, font=chip_font), 138 * SCALE),
              date_text, font=chip_font, fill=(160, 161, 185))

    lines, hfont, size = _fit(draw, headline, SANS_BOLD, int(w * 0.82), 3)
    line_h = int(size * 1.22)
    sub_font = _font(SANS, 40 * SCALE)
    sub_lines = _wrap(draw, subheadline, sub_font, int(w * 0.82))[:2]
    block = len(lines) * line_h + 40 * SCALE + len(sub_lines) * 56 * SCALE
    y = (h - block) // 2 + 30 * SCALE
    for line in lines:
        draw.text((m + 3 * SCALE, y + 4 * SCALE), line, font=hfont, fill=(0, 0, 0, 110))
        draw.text((m, y), line, font=hfont, fill=(250, 250, 255))
        y += line_h
    y += 34 * SCALE
    for line in sub_lines:
        draw.text((m, y), line, font=sub_font, fill=(196, 197, 216))
        y += 56 * SCALE

    for x in range(0, w, 4):
        t = x / w
        color = tuple(int(a + (b - a) * t) for a, b in zip((255, 176, 92), (124, 77, 255)))
        draw.rectangle([x, h - 10 * SCALE, x + 4, h], fill=color)
    return _finish(img, out_path)


def _style_editorial(headline, subheadline, out_path):
    w, h, m = WIDTH * SCALE, HEIGHT * SCALE, 110 * SCALE
    accent = (224, 74, 44)
    img, draw = _new_canvas()
    draw.rectangle([0, 0, w, h], fill=(247, 243, 235))

    # Left accent rule and masthead.
    draw.rectangle([0, 0, 18 * SCALE, h], fill=accent)
    brand_font = _font(SANS_BOLD, 38 * SCALE)
    draw.text((m, 80 * SCALE), BRAND, font=brand_font, fill=(20, 20, 24))
    date_text = time.strftime("%B %d, %Y")
    date_font = _font(SANS, 32 * SCALE)
    draw.text((w - m - draw.textlength(date_text, font=date_font), 84 * SCALE),
              date_text, font=date_font, fill=(120, 116, 108))
    draw.line([(m, 150 * SCALE), (w - m, 150 * SCALE)], fill=(20, 20, 24), width=3 * SCALE)

    kicker_font = _font(SANS_BOLD, 30 * SCALE)
    draw.text((m, 205 * SCALE), TAG.upper(), font=kicker_font, fill=accent)

    lines, hfont, size = _fit(draw, headline, SERIF_BOLD, w - 2 * m, 3, start=104)
    line_h = int(size * 1.16)
    y = 275 * SCALE
    for line in lines:
        draw.text((m, y), line, font=hfont, fill=(24, 22, 20))
        y += line_h

    y += 30 * SCALE
    sub_font = _font(SANS, 42 * SCALE)
    for line in _wrap(draw, subheadline, sub_font, w - 2 * m)[:2]:
        draw.text((m, y), line, font=sub_font, fill=(95, 92, 86))
        y += 58 * SCALE

    draw.line([(m, h - 110 * SCALE), (m + 220 * SCALE, h - 110 * SCALE)], fill=accent, width=8 * SCALE)
    return _finish(img, out_path)


def _style_terminal(headline, subheadline, out_path):
    w, h = WIDTH * SCALE, HEIGHT * SCALE
    green = (86, 240, 145)
    img, draw = _new_canvas()
    _vertical_gradient(draw, w, h, (8, 10, 14), (13, 20, 24))

    # Faint scanlines.
    for y in range(0, h, 8 * SCALE):
        draw.line([(0, y), (w, y)], fill=(255, 255, 255, 6))

    # Terminal window.
    tx0, ty0, tx1, ty1 = 70 * SCALE, 70 * SCALE, w - 70 * SCALE, h - 70 * SCALE
    draw.rounded_rectangle([tx0, ty0, tx1, ty1], radius=28 * SCALE,
                           fill=(14, 17, 22, 235), outline=(70, 85, 95), width=3 * SCALE)
    draw.rounded_rectangle([tx0, ty0, tx1, ty0 + 78 * SCALE], radius=28 * SCALE, fill=(24, 29, 36))
    draw.rectangle([tx0, ty0 + 40 * SCALE, tx1, ty0 + 78 * SCALE], fill=(24, 29, 36))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = tx0 + (44 + i * 52) * SCALE
        draw.ellipse([cx, ty0 + 26 * SCALE, cx + 26 * SCALE, ty0 + 52 * SCALE], fill=color)
    title_font = _font(MONO_BOLD, 28 * SCALE)
    title = f"{BRAND.lower().replace(' ', '-')} — daily briefing"
    draw.text(((tx0 + tx1) / 2 - draw.textlength(title, font=title_font) / 2, ty0 + 24 * SCALE),
              title, font=title_font, fill=(150, 160, 170))

    m = tx0 + 60 * SCALE
    cmd_font = _font(MONO_BOLD, 34 * SCALE)
    stamp = time.strftime("%Y-%m-%d")
    draw.text((m, ty0 + 130 * SCALE), f"$ ai-news --latest --date {stamp}",
              font=cmd_font, fill=(120, 200, 160))

    lines, hfont, size = _fit(draw, headline, MONO_BOLD, tx1 - m - 60 * SCALE, 4, start=72)
    line_h = int(size * 1.3)
    y = ty0 + 210 * SCALE
    for line in lines:
        draw.text((m, y), f"> {line}" if line == lines[0] else f"  {line}",
                  font=hfont, fill=green)
        y += line_h

    y += 24 * SCALE
    sub_font = _font(MONO_BOLD, 32 * SCALE)
    for line in _wrap(draw, subheadline, sub_font, tx1 - m - 60 * SCALE)[:2]:
        draw.text((m, y), line, font=sub_font, fill=(140, 165, 175))
        y += 48 * SCALE

    # Blinking cursor block.
    draw.rectangle([m, y + 20 * SCALE, m + 26 * SCALE, y + 62 * SCALE], fill=green)
    return _finish(img, out_path)


def _style_poster(headline, subheadline, out_path):
    w, h, m = WIDTH * SCALE, HEIGHT * SCALE, 100 * SCALE
    img, draw = _new_canvas()
    # Electric diagonal-feel gradient (blue -> violet -> hot pink).
    stops = [(20, 60, 255), (120, 40, 220), (255, 45, 140)]
    for y in range(h):
        t = y / h
        if t < 0.5:
            a, b, tt = stops[0], stops[1], t / 0.5
        else:
            a, b, tt = stops[1], stops[2], (t - 0.5) / 0.5
        draw.line([(0, y), (w, y)], fill=tuple(int(x + (z - x) * tt) for x, z in zip(a, b)))

    # Oversized translucent brand watermark, tucked in the top-right corner.
    # Drawn on an RGBA overlay and composited so the low alpha actually applies.
    wm_font = _font(SANS_BOLD, 200 * SCALE)
    wm_text = BRAND.split()[0]
    wm_w = draw.textlength(wm_text, font=wm_font)
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(overlay).text(
        (w - wm_w - 40 * SCALE, -30 * SCALE), wm_text, font=wm_font, fill=(255, 255, 255, 36)
    )
    img.paste(overlay, (0, 0), overlay)
    draw = ImageDraw.Draw(img, "RGBA")

    chip_font = _font(SANS_BOLD, 34 * SCALE)
    chip_text = f"{BRAND}  •  {time.strftime('%b %d').upper()}"
    chip_w = draw.textlength(chip_text, font=chip_font)
    draw.rounded_rectangle([m, 80 * SCALE, m + chip_w + 64 * SCALE, 150 * SCALE],
                           radius=36 * SCALE, fill=(0, 0, 0, 150))
    draw.text((m + 32 * SCALE, 96 * SCALE), chip_text, font=chip_font, fill=(255, 255, 255))

    lines, hfont, size = _fit(draw, headline.upper(), SANS_BOLD, w - 2 * m, 3, start=110, floor=48)
    line_h = int(size * 1.12)
    y = (h - len(lines) * line_h - 120 * SCALE) // 2 + 40 * SCALE
    for line in lines:
        draw.text((m + 6 * SCALE, y + 8 * SCALE), line, font=hfont, fill=(0, 0, 0, 160))
        draw.text((m, y), line, font=hfont, fill=(255, 255, 255))
        y += line_h

    y += 30 * SCALE
    sub_font = _font(SANS_BOLD, 40 * SCALE)
    sub = _wrap(draw, subheadline, sub_font, w - 2 * m)[:2]
    for line in sub:
        lw = draw.textlength(line, font=sub_font)
        draw.rectangle([m, y, m + lw + 40 * SCALE, y + 62 * SCALE], fill=(0, 0, 0, 170))
        draw.text((m + 20 * SCALE, y + 6 * SCALE), line, font=sub_font, fill=(255, 230, 90))
        y += 78 * SCALE
    return _finish(img, out_path)


STYLES = {
    "midnight": _style_midnight,
    "editorial": _style_editorial,
    "terminal": _style_terminal,
    "poster": _style_poster,
}


def render_card(headline: str, subheadline: str, out_path: str, style: str = STYLE) -> str:
    return STYLES[style](headline, subheadline, out_path)
