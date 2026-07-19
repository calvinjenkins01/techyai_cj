"""Generate branded carousel slide decks for TikTok photo posts + Instagram.

Terminal aesthetic matching the X autoposter's "terminal" card style.
Output: 1080x1350 (4:5) PNGs — works on both TikTok photo mode and IG.

Usage:
    python make_slides.py decks/claude-5-things.json out/
"""

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
S = 2  # supersampling
GREEN = (86, 240, 145)
DIM = (140, 165, 175)
BG_TOP = (8, 10, 14)
BG_BOTTOM = (13, 20, 24)
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BRAND = "techyai_cj"


def _font(size):
    if Path(MONO).exists():
        return ImageFont.truetype(MONO, size)
    return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
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


def _fit(draw, text, max_width, max_lines, start, floor):
    for size in range(start * S, floor * S, -4 * S):
        font = _font(size)
        lines = _wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return lines, font, size
    font = _font(floor * S)
    return _wrap(draw, text, font, max_width)[:max_lines], font, floor * S


def _canvas():
    w, h = W * S, H * S
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM)))
    for y in range(0, h, 8 * S):
        draw.line([(0, y), (w, y)], fill=(16, 20, 26))
    return img, ImageDraw.Draw(img, "RGBA")


def _terminal_frame(draw, title):
    w, h = W * S, H * S
    x0, y0, x1, y1 = 50 * S, 60 * S, w - 50 * S, h - 60 * S
    draw.rounded_rectangle([x0, y0, x1, y1], radius=26 * S,
                           fill=(14, 17, 22, 240), outline=(70, 85, 95), width=3 * S)
    draw.rounded_rectangle([x0, y0, x1, y0 + 70 * S], radius=26 * S, fill=(24, 29, 36))
    draw.rectangle([x0, y0 + 36 * S, x1, y0 + 70 * S], fill=(24, 29, 36))
    for i, color in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        cx = x0 + (36 + i * 46) * S
        draw.ellipse([cx, y0 + 22 * S, cx + 24 * S, y0 + 46 * S], fill=color)
    tfont = _font(26 * S)
    draw.text(((x0 + x1) / 2 - draw.textlength(title, font=tfont) / 2, y0 + 20 * S),
              title, font=tfont, fill=(150, 160, 170))
    return x0, y0, x1, y1


def _footer(draw, x0, x1, y1, page, total):
    ffont = _font(28 * S)
    draw.text((x0 + 50 * S, y1 - 70 * S), f"@{BRAND}", font=ffont, fill=DIM)
    page_text = f"{page}/{total}"
    draw.text((x1 - 50 * S - draw.textlength(page_text, font=ffont), y1 - 70 * S),
              page_text, font=ffont, fill=DIM)


def render_slide(slide, page, total, out_path):
    img, draw = _canvas()
    x0, y0, x1, y1 = _terminal_frame(draw, slide.get("window", f"{BRAND} — daily briefing"))
    m = x0 + 50 * S
    max_w = x1 - m - 50 * S
    kind = slide["kind"]

    if kind == "hook":
        draw.text((m, y0 + 120 * S), "$ " + slide.get("cmd", "claude --explain"),
                  font=_font(30 * S), fill=(120, 200, 160))
        lines, font, size = _fit(draw, slide["text"], max_w, 5, start=88, floor=48)
        line_h = int(size * 1.25)
        y = y0 + 210 * S
        for i, line in enumerate(lines):
            prefix = "> " if i == 0 else "  "
            draw.text((m, y), prefix + line, font=font, fill=GREEN)
            y += line_h
        if slide.get("sub"):
            y += 30 * S
            sfont = _font(32 * S)
            for line in _wrap(draw, slide["sub"], sfont, max_w)[:3]:
                draw.text((m, y), line, font=sfont, fill=DIM)
                y += 46 * S
        draw.text((m, y + 40 * S), "swipe →", font=_font(34 * S), fill=(255, 189, 46))

    elif kind == "point":
        num = slide.get("num", page - 1)
        draw.text((m, y0 + 110 * S), f"$ fact {num}/{slide.get('of', total - 2)}",
                  font=_font(30 * S), fill=(120, 200, 160))
        draw.text((m, y0 + 170 * S), f"{num:02d}", font=_font(120 * S), fill=(40, 90, 65))
        lines, font, size = _fit(draw, slide["text"], max_w, 6, start=64, floor=40)
        line_h = int(size * 1.3)
        y = y0 + 330 * S
        for line in lines:
            draw.text((m, y), line, font=font, fill=(235, 240, 238))
            y += line_h
        if slide.get("sub"):
            y += 26 * S
            sfont = _font(30 * S)
            for line in _wrap(draw, slide["sub"], sfont, max_w)[:10]:
                draw.text((m, y), line, font=sfont, fill=DIM)
                y += 44 * S

    elif kind == "cta":
        lines, font, size = _fit(draw, slide["text"], max_w, 4, start=72, floor=44)
        line_h = int(size * 1.28)
        y = y0 + 240 * S
        for line in lines:
            draw.text((m, y), line, font=font, fill=GREEN)
            y += line_h
        if slide.get("sub"):
            y += 34 * S
            sfont = _font(34 * S)
            for line in _wrap(draw, slide["sub"], sfont, max_w)[:3]:
                draw.text((m, y), line, font=sfont, fill=(235, 240, 238))
                y += 50 * S
        # Blinking cursor.
        draw.rectangle([m, y + 30 * S, m + 24 * S, y + 68 * S], fill=GREEN)

    _footer(draw, x0, x1, y1, page, total)
    img.resize((W, H), Image.LANCZOS).save(out_path, "PNG")
    return out_path


def render_deck(deck_path, out_dir):
    deck = json.loads(Path(deck_path).read_text())
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    slides = deck["slides"]
    paths = []
    for i, slide in enumerate(slides, start=1):
        path = out / f"{deck['name']}-{i:02d}.png"
        render_slide(slide, i, len(slides), str(path))
        paths.append(str(path))
        print(f"rendered {path}")
    return paths


if __name__ == "__main__":
    render_deck(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "out")
