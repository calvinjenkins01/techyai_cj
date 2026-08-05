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


def grain(img, amount=10):
    px = img.load()
    for y in range(H):
        for x in range(W):
            n = random.randint(-amount, amount)
            r, g, b = px[x, y]
            px[x, y] = (max(0, min(255, r + n)), max(0, min(255, g + n)),
                        max(0, min(255, b + n)))
    return img


def render(slide, deck_dir):
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
    avail = H - PAD * 2 - 60 - text_h - (GAP_BLOCK * 2 if slide.get("image") else 0)

    pic = None
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

    stack_h = text_h + ((pic.height + GAP_BLOCK * 2) if pic else 0)
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
