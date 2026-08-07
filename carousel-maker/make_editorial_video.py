"""Animate the icon panel on editorial slides into looping MP4s.

Instagram carousels accept video slides. TikTok photo posts do not, so keep the
PNGs from make_editorial.py for TikTok and use these for Instagram.

The static part of the slide is rendered once. Only the panel region is
repainted per frame, which is why this finishes in seconds rather than minutes.

Usage:
    python make_editorial_video.py decks/some-deck.json out/
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw
from imageio_ffmpeg import get_ffmpeg_exe

import make_editorial as ME

FPS = 24
SECONDS = 2.5


def animate(slide, deck_dir, out_path):
    # base frame with the panel drawn but the glyph left off
    base = ME.render(slide, deck_dir, draw_glyph=False)
    x0, y0, x1, y1 = ME.LAST_PANEL
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

    frames = []
    total = int(FPS * SECONDS)
    for i in range(total):
        t = i / total
        img = base.copy()
        d = ImageDraw.Draw(img)
        ME.glyph(d, cx, cy, slide["icon"], ME.GREEN, s=1.0, t=t)
        # regrain just the panel so the noise is not frozen where the art moves
        box = (x0, y0, x1, y1)
        patch = img.crop(box)
        noise = Image.effect_noise(patch.size, 11).convert("RGB")
        img.paste(ImageChops.add(patch, noise, scale=1, offset=-128), box)
        frames.append(img)

    with tempfile.TemporaryDirectory() as td:
        for i, f in enumerate(frames):
            f.save(f"{td}/f{i:04d}.png")
        subprocess.run([get_ffmpeg_exe(), "-y", "-framerate", str(FPS),
                        "-i", f"{td}/f%04d.png", "-c:v", "libx264",
                        "-pix_fmt", "yuv420p", "-crf", "18", str(out_path)],
                       check=True, capture_output=True)
    print("rendered", out_path)


def main():
    deck_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "out")
    out_dir.mkdir(parents=True, exist_ok=True)
    deck = json.loads(deck_path.read_text())
    for i, slide in enumerate(deck["slides"], 1):
        if not slide.get("icon"):
            continue
        animate(slide, deck_path.parent, out_dir / f"{deck['name']}-{i:02d}.mp4")


if __name__ == "__main__":
    main()
