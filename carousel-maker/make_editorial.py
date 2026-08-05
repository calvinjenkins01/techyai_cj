"""Editorial carousel renderer.

Kallaway style slide anatomy in CJ's palette: headline in bold white caps with
an accent phrase in green serif italic, a body line, a screenshot dropped into a
glowing slot, and a closing line. Near black background, grain over everything.

Mark accent phrases with *asterisks* in any text field.

Usage:
    python make_editorial.py decks/some-deck.json out/
"""

import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1350
FDIR = "/usr/share/fonts/truetype/dejavu/"
BG = (10, 13, 16)
GREEN = (86, 240, 145)
GREEN_DIM = (38, 112, 74)
WHITE = (240, 244, 242)
GREY = (150, 162, 168)
SHEAR = 0.20

PAD = 80
HEAD_SIZE = 60
BODY_SIZE = 30
GAP_HEAD = 34
GAP_BLOCK = 44


def sans(sz, bold=True):
    return ImageFont.truetype(FDIR + ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"), sz)


def serif(sz):
    return ImageFont.truetype(FDIR + "DejaVuSerif-Bold.ttf", sz)


PUNCT = set(".,!?;:")


def tokenize(text):
    """Split on *accent* markers into (word, is_accent) tokens.

    Punctuation stranded after a closing marker gets glued back onto the word
    before it, otherwise you get "five minutes ." with a floating period.
    """
    out, accent = [], False
    for chunk in text.split("*"):
        if chunk:
            for word in chunk.split():
                if out and all(c in PUNCT for c in word):
                    prev, prev_accent = out[-1]
                    out[-1] = (prev + word, prev_accent)
                else:
                    out.append((word, accent))
        accent = not accent
    return out


def word_img(word, font, color, shear=None):
    """Render one word, optionally sheared into a fake italic. Returns (img, advance)."""
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    adv = probe.textlength(word, font=font)
    h = int(font.size * 1.7)
    extra = int(abs(shear) * h) + 6 if shear else 6
    tmp = Image.new("RGBA", (int(adv) + extra * 2, h), (0, 0, 0, 0))
    ImageDraw.Draw(tmp).text((extra, 0), word, font=font, fill=color + (255,))
    if shear:
        tmp = tmp.transform(tmp.size, Image.AFFINE,
                            (1, shear, -shear * h / 2, 0, 1, 0), resample=Image.BICUBIC)
    return tmp, adv, extra


def layout_runs(tokens, plain_font, accent_font, maxw, upper_plain):
    """Greedy wrap mixed font tokens. Returns list of lines, each a list of parts."""
    probe = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    space_plain = probe.textlength(" ", font=plain_font)
    lines, cur, curw = [], [], 0.0
    for word, is_accent in tokens:
        txt = word if is_accent else (word.upper() if upper_plain else word)
        font = accent_font if is_accent else plain_font
        w = probe.textlength(txt, font=font)
        add = w if not cur else w + space_plain
        if cur and curw + add > maxw:
            lines.append(cur)
            cur, curw = [(txt, is_accent, font, w)], w
        else:
            cur.append((txt, is_accent, font, w))
            curw += add
    if cur:
        lines.append(cur)
    return lines, space_plain


def draw_runs(img, lines, space, y, line_h, plain_color, accent_color):
    for line in lines:
        total = sum(p[3] for p in line) + space * (len(line) - 1)
        x = (W - total) / 2
        for txt, is_accent, font, w in line:
            color = accent_color if is_accent else plain_color
            tmp, adv, extra = word_img(txt, font, color, SHEAR if is_accent else None)
            img.paste(tmp, (int(x) - extra, int(y)), tmp)
            x += w + space
        y += line_h
    return y


def block_height(lines, line_h):
    return len(lines) * line_h


def glow_behind(img, box, radius=70, color=(28, 92, 60)):
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    ImageDraw.Draw(layer).rounded_rectangle(box, radius=28, fill=color)
    return ImageChops.screen(img, layer.filter(ImageFilter.GaussianBlur(radius)))


def rounded(im, radius=18):
    mask = Image.new("L", im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.size[0] - 1, im.size[1] - 1],
                                           radius=radius, fill=255)
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste(im, (0, 0), mask)
    return out


def glyph(d, cx, cy, kind, color, s=1.0, t=None):
    """Simple line art, drawn to sit inside a 300px box.

    t is a 0..1 loop position. Motion is driven by sin so the loop is seamless.
    """
    import math
    ph = 0.0 if t is None else math.sin(t * 2 * math.pi)
    cy = cy + ph * 6
    def L(*pts, w=7):
        d.line([(cx + x * s, cy + y * s) for x, y in pts], fill=color, width=int(w * s))

    def R(x0, y0, x1, y1, r=12, w=7, fill=None):
        d.rounded_rectangle([cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s],
                            radius=int(r * s), outline=color, width=int(w * s), fill=fill)

    def E(x0, y0, x1, y1, w=7, fill=None):
        d.ellipse([cx + x0 * s, cy + y0 * s, cx + x1 * s, cy + y1 * s],
                  outline=color, width=int(w * s), fill=fill)

    if kind == "file":
        R(-70, -95, 70, 95, r=14)
        for i, y in enumerate((-50, -14, 22)):
            L((-42, y), (42 - i * 22, y), w=7)
        L((-42, 58), (10, 58), w=7)
    elif kind == "image":
        R(-95, -70, 95, 70, r=14)
        E(-62, -44, -30, -12, w=6)
        L((-80, 52), (-18, -8), (14, 26), (44, -6), (82, 52), w=6)
    elif kind == "chip":
        R(-62, -62, 62, 62, r=10)
        R(-26, -26, 26, 26, r=6, w=6)
        e = 0 if t is None else math.sin(t * 2 * math.pi) * 8
        for off in (-34, 0, 34):
            L((off, -95 - e), (off, -62)); L((off, 62), (off, 95 + e))
            L((-95 - e, off), (-62, off)); L((62, off), (95 + e, off))
    elif kind == "search":
        ox = 0 if t is None else math.cos(t * 2 * math.pi) * 10
        oy = 0 if t is None else math.sin(t * 2 * math.pi) * 10
        E(-90 + ox, -90 + oy, 34 + ox, 34 + oy, w=8)
        L((26 + ox, 26 + oy), (92, 92), w=10)
    elif kind == "inbox":
        R(-95, -62, 95, 62, r=12)
        L((-95, -62), (0, 16), (95, -62), w=7)
    elif kind == "wave":
        for i, h in enumerate((22, 54, 90, 46, 74, 30, 60, 18)):
            x = -84 + i * 24
            if t is not None:
                h = 18 + abs(h - 18) * (0.55 + 0.45 * math.sin((t + i * 0.11) * 2 * math.pi))
            L((x, -h), (x, h), w=9)
    elif kind == "videosearch":
        R(-95, -72, 60, 52, r=12)
        d.polygon([(cx - 30 * s, cy - 34 * s), (cx - 30 * s, cy + 14 * s),
                   (cx + 14 * s, cy - 10 * s)], fill=color)
        ox = 0 if t is None else math.cos(t * 2 * math.pi) * 9
        oy = 0 if t is None else math.sin(t * 2 * math.pi) * 9
        E(20 + ox, 10 + oy, 96 + ox, 86 + oy, w=8)
        L((86 + ox, 76 + oy), (110, 100), w=9)
    elif kind == "textimage":
        R(-95, -70, 95, 70, r=14)
        L((-46, 30), (-14, -34), (18, 30), w=8)
        L((-34, 6), (6, 6), w=8)
        L((44, -34), (44, 30), w=8)
        L((30, -34), (58, -34), w=8)
    elif kind == "tovideo":
        R(-108, -56, -18, 34, r=10)
        ax = 0 if t is None else math.sin(t * 2 * math.pi) * 7
        L((-4 + ax, -10), (34 + ax, -10), w=8)
        L((22 + ax, -24), (36 + ax, -10), (22 + ax, 4), w=8)
        R(46, -56, 118, 34, r=10)
        d.polygon([(cx + 68 * s, cy - 30 * s), (cx + 68 * s, cy + 10 * s),
                   (cx + 100 * s, cy - 10 * s)], fill=color)
    elif kind == "filmstrip":
        sl = 0 if t is None else math.sin(t * 2 * math.pi) * 6
        R(-105, -70, 105, 70, r=10)
        for x in (-105, 105):
            for yy in (-52, -18, 16, 50):
                d.rounded_rectangle([cx + (x - 16) * s, cy + (yy - 11) * s,
                                     cx + (x + 16) * s, cy + (yy + 11) * s],
                                    radius=int(4 * s), fill=color)
        for i in range(3):
            xx = -56 + i * 56 + sl
            L((xx, -34), (xx, 34), w=6)
    elif kind == "motion":
        sh = 0 if t is None else math.sin(t * 2 * math.pi) * 16
        R(28 + sh, -34, 96 + sh, 34, r=12, w=8)
        for i, a in enumerate((0.55, 0.32, 0.16)):
            off = -34 - i * 34 + sh
            d.rounded_rectangle([cx + (off - 30) * s, cy - 26 * s,
                                 cx + (off + 30) * s, cy + 26 * s],
                                radius=int(10 * s),
                                outline=tuple(int(c * a) for c in color), width=int(6 * s))
    elif kind == "clone":
        gap = 0 if t is None else math.sin(t * 2 * math.pi) * 5
        for side, sign in ((-1, -1), (1, 1)):
            base = side * 58 + sign * gap
            for i, h in enumerate((28, 62, 40, 74, 34)):
                L((base + (i - 2) * 17, -h), (base + (i - 2) * 17, h), w=8)
        L((-8, -14), (8, -14), w=6)
        L((-8, 14), (8, 14), w=6)
    elif kind == "docwave":
        R(-112, -78, -22, 78, r=12)
        for y in (-42, -12, 18):
            L((-92, y), (-42, y), w=6)
        for i, h in enumerate((22, 52, 34, 66, 30)):
            if t is not None:
                h = 18 + abs(h - 18) * (0.55 + 0.45 * math.sin((t + i * 0.13) * 2 * math.pi))
            x = 6 + i * 24
            L((x, -h), (x, h), w=8)
    elif kind == "note":
        bob = 0 if t is None else math.sin(t * 2 * math.pi) * 5
        E(-92, 30 + bob, -30, 84 + bob, w=8)
        L((-30, 57 + bob), (-30, -76 + bob), w=8)
        E(28, 6 + bob, 90, 60 + bob, w=8)
        L((90, 33 + bob), (90, -96 + bob), w=8)
        L((-30, -76 + bob), (90, -96 + bob), w=8)
        L((-30, -44 + bob), (90, -64 + bob), w=8)
    elif kind == "split":
        sp = 0 if t is None else math.sin(t * 2 * math.pi) * 12
        for i, h in enumerate((26, 58, 84, 40)):
            x = -92 + i * 22 - sp
            L((x, -h - 20), (x, h - 20), w=9)
        for i, h in enumerate((34, 70, 44, 22)):
            x = 12 + i * 22 + sp
            L((x, -h + 30), (x, h + 30), w=9)
        L((-8, -100), (-8, 100), w=4)


LAST_PANEL = None


def icon_panel(img, kind, top, height=360, t=None, draw_glyph=True):
    """A glowing panel with a glyph in it, used when there is no screenshot."""
    w = 460
    x0, x1 = (W - w) / 2, (W + w) / 2
    y0, y1 = top, top + height
    img = glow_behind(img, [x0 + 40, y0 + 40, x1 - 40, y1 - 40], radius=80)
    d = ImageDraw.Draw(img)
    global LAST_PANEL
    LAST_PANEL = (int(x0), int(y0), int(x1), int(y1))
    d.rounded_rectangle([x0, y0, x1, y1], radius=24, fill=(19, 25, 29),
                        outline=GREEN_DIM, width=3)
    if draw_glyph:
        glyph(d, (x0 + x1) / 2, (y0 + y1) / 2, kind, GREEN, s=1.0, t=t)
    return img


def grain(img, sigma=11):
    """Film grain. PIL's effect_noise is C speed, a Python pixel loop is not."""
    noise = Image.effect_noise((img.width, img.height), sigma).convert("RGB")
    return ImageChops.add(img, noise, scale=1, offset=-128)


def render(slide, deck_dir, draw_glyph=True):
    img = Image.new("RGB", (W, H), BG)

    bf_plain, bf_accent = sans(BODY_SIZE, bold=False), serif(BODY_SIZE - 2)
    maxw = W - PAD * 2

    # shrink the headline until it fits in two lines
    head_tokens = tokenize(slide["headline"])
    for head_size in (HEAD_SIZE, 54, 48, 44, 40):
        hf_plain, hf_accent = sans(head_size), serif(head_size - 4)
        head_lines, head_space = layout_runs(head_tokens, hf_plain, hf_accent, maxw, True)
        if len(head_lines) <= 2:
            break
    head_line_h = head_size + 22
    head_h = block_height(head_lines, head_line_h)

    body_lines = body_space = None
    body_h = 0
    if slide.get("body"):
        body_lines, body_space = layout_runs(tokenize(slide["body"]),
                                             bf_plain, bf_accent, maxw, False)
        body_h = block_height(body_lines, BODY_SIZE + 14)

    close_lines = close_space = None
    close_h = 0
    if slide.get("close"):
        close_lines, close_space = layout_runs(tokenize(slide["close"]),
                                               bf_plain, bf_accent, maxw, False)
        close_h = block_height(close_lines, BODY_SIZE + 14)

    # what is left for the picture once the text is placed
    text_h = head_h + (GAP_HEAD + body_h if body_h else 0) + (GAP_BLOCK + close_h if close_h else 0)
    has_visual = bool(slide.get("image") or slide.get("icon"))
    avail = H - PAD * 2 - 60 - text_h - (GAP_BLOCK * 2 if has_visual else 0)

    pic = None
    icon_h = 0
    if slide.get("icon") and not slide.get("image"):
        icon_h = min(380, max(260, avail))
    if slide.get("image"):
        p = Path(slide["image"])
        if not p.is_absolute():
            p = deck_dir / p
        box_w, box_h = W - PAD * 2, max(220, min(avail, 700))
        if p.exists():
            src = Image.open(p).convert("RGB")
            scale = min(box_w / src.width, box_h / src.height)
            pic = src.resize((int(src.width * scale), int(src.height * scale)), Image.LANCZOS)
        else:
            pic = Image.new("RGB", (box_w, int(box_h * 0.7)), (22, 28, 32))
            pd = ImageDraw.Draw(pic)
            pd.rounded_rectangle([0, 0, pic.width - 1, pic.height - 1], radius=18,
                                 outline=GREEN_DIM, width=3)
            lbl = f"screenshot: {slide['image']}"
            lf = sans(24, bold=False)
            pd.text((pic.width / 2 - pd.textlength(lbl, font=lf) / 2,
                     pic.height / 2 - 14), lbl, font=lf, fill=GREY)

    visual_h = pic.height if pic else icon_h
    stack_h = text_h + ((visual_h + GAP_BLOCK * 2) if visual_h else 0)
    y = max(PAD, (H - stack_h) / 2)

    if pic:
        px0 = (W - pic.width) / 2
        py = y + head_h + (GAP_HEAD - 10 + body_h if body_h else 0) + GAP_BLOCK
        img = glow_behind(img, [px0 + 30, py + 30, px0 + pic.width - 30, py + pic.height - 30])

    d_y = draw_runs(img, head_lines, head_space, y, head_line_h, WHITE, GREEN)
    if body_lines:
        d_y = draw_runs(img, body_lines, body_space, d_y + GAP_HEAD - 10,
                        BODY_SIZE + 14, WHITE, GREEN)
    if pic:
        px0 = (W - pic.width) / 2
        py = d_y + GAP_BLOCK
        img.paste(rounded(pic.convert("RGBA")), (int(px0), int(py)),
                  rounded(pic.convert("RGBA")))
        d_y = py + pic.height
    elif icon_h:
        py = d_y + GAP_BLOCK
        img = icon_panel(img, slide["icon"], py, icon_h, draw_glyph=draw_glyph)
        d_y = py + icon_h
    if close_lines:
        draw_runs(img, close_lines, close_space, d_y + GAP_BLOCK,
                  BODY_SIZE + 14, WHITE, GREEN)

    d = ImageDraw.Draw(img)
    hf = sans(24)
    d.text((W / 2 - d.textlength("@techyai_cj", font=hf) / 2, H - 62),
           "@techyai_cj", font=hf, fill=GREEN_DIM)

    return grain(img)


def main():
    deck_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    deck = json.loads(deck_path.read_text())
    for i, slide in enumerate(deck["slides"], 1):
        img = render(slide, deck_path.parent)
        name = out_dir / f"{deck['name']}-{i:02d}.png"
        img.save(name)
        print("rendered", name)


if __name__ == "__main__":
    main()
