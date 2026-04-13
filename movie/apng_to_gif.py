#!/usr/bin/env python3
"""
apng_to_gif.py — Convert an animated PNG (.png/APNG) to GIF, preserving timing.

Usage (CLI):
  python apng_to_gif.py input.png [--out out.gif] [--width 800] [--height H]
                                  [--fps 15] [--bg "#ffffff"] [--loop 0]
                                  [--no-optimize]

Install once:
  pip install pillow
"""

import argparse
import os
from typing import List, Tuple, Optional

from PIL import Image, ImageSequence, ImageColor


def round_to_gif_cs(ms: int) -> int:
    """Round milliseconds to the nearest 10 ms (GIF centiseconds)."""
    if ms <= 0:
        return 10  # avoid zero-delay frames
    return int(round(ms / 10.0)) * 10


def resize_frame(im: Image.Image, width: Optional[int], height: Optional[int]) -> Image.Image:
    if width is None and height is None:
        return im
    w, h = im.size
    if width is not None and height is not None:
        new_size = (width, height)
    elif width is not None:
        new_h = int(round(h * (width / w)))
        new_size = (width, new_h)
    else:  # height only
        new_w = int(round(w * (height / h)))
        new_size = (new_w, height)
    return im.resize(new_size, resample=Image.LANCZOS)


def flatten_rgba(im: Image.Image, bg: Optional[str]) -> Image.Image:
    """Flatten RGBA onto a solid background if bg is provided; else keep RGBA."""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    if not bg:
        return im
    rgb = ImageColor.getrgb(bg)
    bg_im = Image.new("RGBA", im.size, rgb + (255,))
    bg_im.paste(im, (0, 0), im)
    return bg_im.convert("RGB")  # no alpha if background provided


def collect_frames(
    path: str,
    width: Optional[int],
    height: Optional[int],
    bg: Optional[str],
    fps: Optional[float],
) -> Tuple[List[Image.Image], List[int]]:
    im = Image.open(path)
    n = getattr(im, "n_frames", 1)
    if n <= 1:
        raise SystemExit(f"Input appears to have only one frame. Got n_frames={n}. Is it an APNG?")

    frames: List[Image.Image] = []
    durations_ms: List[int] = []

    # If FPS is provided, use a uniform duration
    const_duration = None
    if fps and fps > 0:
        const_duration = int(round(1000.0 / fps))

    for frame in ImageSequence.Iterator(im):
        fr = frame.convert("RGBA")
        fr = resize_frame(fr, width, height)
        fr = flatten_rgba(fr, bg)

        # Duration (ms) from frame info; default 100 ms if missing
        dur = frame.info.get("duration", 100)
        dur = const_duration if const_duration is not None else dur
        dur = round_to_gif_cs(int(dur))

        frames.append(fr)
        durations_ms.append(dur)

    return frames, durations_ms


def ensure_output_path(inp: str, out: Optional[str]) -> str:
    if out:
        return out
    base, _ = os.path.splitext(inp)
    return base + ".gif"


def convert_apng_to_gif(
    input_path: str,
    out_path: Optional[str] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: Optional[float] = None,
    bg: Optional[str] = None,
    loop: int = 0,
    optimize: bool = True,
) -> str:
    """
    Convert an APNG to GIF.

    Parameters
    ----------
    input_path : str
        Path to the animated PNG.
    out_path : Optional[str]
        Output GIF path (default: input basename with .gif).
    width, height : Optional[int]
        Resize while keeping aspect if only one dimension is provided.
    fps : Optional[float]
        Force constant FPS; if None, preserve per-frame delays.
    bg : Optional[str]
        Background color (e.g., "#ffffff") to flatten transparency.
    loop : int
        0 = loop forever (default). Positive values = number of loops.
    optimize : bool
        Use Pillow GIF optimization (default True).

    Returns
    -------
    str : The output GIF path.
    """
    out_path = ensure_output_path(input_path, out_path)
    frames, durations = collect_frames(input_path, width, height, bg, fps)
    if len(frames) < 2:
        raise ValueError("Need at least two frames to make a GIF.")

    save_kwargs = dict(
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=loop,
        disposal=2,   # restore to background before next frame
        optimize=optimize,
    )
    frames[0].save(out_path, format="GIF", **save_kwargs)
    return out_path


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Convert animated PNG (APNG) to GIF.")
    p.add_argument("input", help="Input .png (APNG) file")
    p.add_argument("--out", "-o", help="Output GIF path (default: input name with .gif)")
    p.add_argument("--width", type=int, default=None, help="Resize to this width (keep aspect)")
    p.add_argument("--height", type=int, default=None, help="Resize to this height (keep aspect)")
    p.add_argument("--fps", type=float, default=None, help="Force constant FPS (e.g., 15)")
    p.add_argument("--bg", type=str, default=None, help="Background to flatten transparency (e.g., '#ffffff')")
    p.add_argument("--loop", type=int, default=0, help="GIF loop count (0 = forever)")
    p.add_argument("--no-optimize", action="store_true", help="Disable GIF optimization (larger files)")
    return p.parse_args()


def main():
    args = _parse_args()
    out = convert_apng_to_gif(
        input_path=args.input,
        out_path=args.out,
        width=args.width,
        height=args.height,
        fps=args.fps,
        bg=args.bg,
        loop=args.loop,
        optimize=not args.no_optimize,
    )
    print(f"✔ Wrote {out}")


if __name__ == "__main__":
    main()
