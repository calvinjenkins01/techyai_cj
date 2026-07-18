"""Render a branded header card image for each post using Pillow (no image API needed)."""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 900
TOP_COLOR = (16, 18, 35)
BOTTOM_COLOR = (55, 30, 90)
ACCENT = (255, 176, 92)
BRAND = "AI PULSE"

FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def _font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    for path in FONT_PATHS:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def render_card(headline: str, subheadline: str, out_path: str) -> str:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        t = y / HEIGHT
        color = tuple(int(a + (b - a) * t) for a, b in zip(TOP_COLOR, BOTTOM_COLOR))
        draw.line([(0, y), (WIDTH, y)], fill=color)

    draw.text((90, 70), BRAND, font=_font(40), fill=ACCENT)
    draw.line([(90, 130), (290, 130)], fill=ACCENT, width=4)

    y = 240
    for line in textwrap.wrap(headline, width=24)[:4]:
        draw.text((90, y), line, font=_font(92), fill=(255, 255, 255))
        y += 112

    y += 30
    for line in textwrap.wrap(subheadline, width=52)[:2]:
        draw.text((90, y), line, font=_font(44), fill=(205, 205, 220))
        y += 60

    img.save(out_path, "PNG")
    return out_path
