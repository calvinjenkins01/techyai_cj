"""Stitch a deck into one continuous MP4 so it can post as a normal video.

TikTok photo mode is stills only. This is the alternative: every slide held for
a few seconds in one file, using the animated version of a slide where one
exists and the still where it does not.

Usage:
    python make_deck_video.py decks/some-deck.json out/ [seconds_per_slide]
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from imageio_ffmpeg import get_ffmpeg_exe

FF = get_ffmpeg_exe()
FPS = 24


def still_clip(png, seconds, dest):
    subprocess.run([FF, "-y", "-loop", "1", "-i", str(png), "-t", str(seconds),
                    "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", str(dest)], check=True, capture_output=True)


def loop_clip(mp4, seconds, dest):
    subprocess.run([FF, "-y", "-stream_loop", "-1", "-i", str(mp4), "-t", str(seconds),
                    "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "18", str(dest)], check=True, capture_output=True)


def main():
    deck_path = Path(sys.argv[1])
    out_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "out")
    seconds = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
    deck = json.loads(deck_path.read_text())
    name = deck["name"]

    with tempfile.TemporaryDirectory() as td:
        parts = []
        for i in range(1, len(deck["slides"]) + 1):
            mp4 = out_dir / f"{name}-{i:02d}.mp4"
            png = out_dir / f"{name}-{i:02d}.png"
            part = Path(td) / f"p{i:02d}.mp4"
            if mp4.exists():
                loop_clip(mp4, seconds, part)
            elif png.exists():
                still_clip(png, seconds, part)
            else:
                print("missing slide", i)
                continue
            parts.append(part)

        listing = Path(td) / "list.txt"
        listing.write_text("".join(f"file '{p}'\n" for p in parts))
        dest = out_dir / f"{name}-FULL.mp4"
        subprocess.run([FF, "-y", "-f", "concat", "-safe", "0", "-i", str(listing),
                        "-c", "copy", str(dest)], check=True, capture_output=True)
        print("rendered", dest, f"({len(parts)} slides, {seconds}s each)")


if __name__ == "__main__":
    main()
