"""Render a branded header card image for each post using Pillow (no image API needed).

The card is drawn at 2x resolution and downscaled for crisp, anti-aliased text.
"""

import math
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH, HEIGHT = 1600, 900
SCALE = 2  # supersampling factor

# Palette — tweak these to rebrand.
BG_TOP = (13, 15, 32)
BG_BOTTOM = (44, 24, 74)
GLOW_COLOR = (124, 77, 255)
ACCENT = (255, 176, 92)
HEADLINE_COLOR = (250, 250, 255)
SUB_COLOR = (196, 197, 216)
CHIP_BG = (255, 255, 255, 26)

BRAND = "AI PULSE"
TAG = "AI NEWS"

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


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    """Word-wrap text to a pixel width."""
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


def _fit_headline(draw, text: str, max_width: int, max_lines: int) -> tuple[list[str], object, int]:
    """Shrink the headline font until it fits within max_lines."""
    for size in range(96 * SCALE, 40 * SCALE, -4 * SCALE):
        font = _font(size)
        lines = _wrap(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return lines, font, size
    font = _font(40 * SCALE)
    return _wrap(draw, text, font, max_width)[:max_lines], font, 40 * SCALE


def render_card(headline: str, subheadline: str, out_path: str) -> str:
    w, h = WIDTH * SCALE, HEIGHT * SCALE
    margin = 90 * SCALE
    img = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(img)

    # Diagonal gradient background.
    for y in range(h):
        t = y / h
        color = tuple(int(a + (b - a) * t) for a, b in zip(BG_TOP, BG_BOTTOM))
        draw.line([(0, y), (w, y)], fill=color)

    # Soft glow orbs (drawn on an overlay, blurred, composited).
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse([w * 0.68, -h * 0.35, w * 1.15, h * 0.45], fill=GLOW_COLOR)
    glow_draw.ellipse([-w * 0.15, h * 0.75, w * 0.25, h * 1.3], fill=(200, 110, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(180 * SCALE))
    img = Image.blend(img, Image.composite(glow, img, glow.convert("L")), 0.35)
    draw = ImageDraw.Draw(img, "RGBA")

    # Subtle dot grid, upper right area.
    dot_gap = 46 * SCALE
    for gx in range(int(w * 0.62), w - 30 * SCALE, dot_gap):
        for gy in range(40 * SCALE, int(h * 0.42), dot_gap):
            draw.ellipse(
                [gx, gy, gx + 5 * SCALE, gy + 5 * SCALE], fill=(255, 255, 255, 28)
            )

    # Brand, top left.
    brand_font = _font(42 * SCALE)
    draw.text((margin, 66 * SCALE), BRAND, font=brand_font, fill=ACCENT)
    brand_w = draw.textlength(BRAND, font=brand_font)
    draw.line(
        [(margin, 128 * SCALE), (margin + brand_w, 128 * SCALE)],
        fill=ACCENT,
        width=5 * SCALE,
    )

    # Tag chip + date, top right.
    chip_font = _font(30 * SCALE)
    date_text = time.strftime("%b %d, %Y").upper()
    tag_w = draw.textlength(TAG, font=chip_font)
    chip_x1 = w - margin
    chip_x0 = chip_x1 - tag_w - 56 * SCALE
    draw.rounded_rectangle(
        [chip_x0, 62 * SCALE, chip_x1, 122 * SCALE],
        radius=30 * SCALE,
        fill=CHIP_BG,
        outline=(255, 255, 255, 70),
        width=2 * SCALE,
    )
    draw.text(
        (chip_x0 + 28 * SCALE, 74 * SCALE), TAG, font=chip_font, fill=(255, 255, 255)
    )
    date_w = draw.textlength(date_text, font=chip_font)
    draw.text(
        (chip_x1 - date_w, 138 * SCALE),
        date_text,
        font=chip_font,
        fill=(160, 161, 185),
    )

    # Headline, auto-sized, vertically centered in the middle band.
    max_text_width = int(w * 0.82)
    lines, headline_font, size = _fit_headline(draw, headline, max_text_width, max_lines=3)
    line_height = int(size * 1.22)
    sub_font = _font(40 * SCALE)
    sub_lines = _wrap(draw, subheadline, sub_font, max_text_width)[:2]
    block_height = len(lines) * line_height + 40 * SCALE + len(sub_lines) * int(56 * SCALE)
    y = (h - block_height) // 2 + 30 * SCALE

    for line in lines:
        # Soft shadow for depth.
        draw.text((margin + 3 * SCALE, y + 4 * SCALE), line, font=headline_font, fill=(0, 0, 0, 110))
        draw.text((margin, y), line, font=headline_font, fill=HEADLINE_COLOR)
        y += line_height

    y += 34 * SCALE
    for line in sub_lines:
        draw.text((margin, y), line, font=sub_font, fill=SUB_COLOR)
        y += int(56 * SCALE)

    # Bottom accent bar.
    bar = math.floor(10 * SCALE)
    for x in range(0, w, 4):
        t = x / w
        color = tuple(
            int(a + (b - a) * t) for a, b in zip(ACCENT, GLOW_COLOR)
        )
        draw.rectangle([x, h - bar, x + 4, h], fill=color)

    img = img.resize((WIDTH, HEIGHT), Image.LANCZOS)
    img.save(out_path, "PNG")
    return out_path
