#!/usr/bin/env python3
"""Draw a red circle on a screenshot, for step-by-step instructions.

    annotate.py in.png out.png x y radius [x y radius ...]

Coordinates are fractions of the image, not pixels, so a re-capture at another
window size does not move every annotation.
"""
import sys
from PIL import Image, ImageDraw


def main(argv):
    src, dst = argv[1], argv[2]
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size

    rest = argv[3:]
    for i in range(0, len(rest), 3):
        fx, fy, fr = (float(v) for v in rest[i:i + 3])
        cx, cy, r = fx * w, fy * h, fr * w
        # Two rings: a dark one under a red one, so the mark reads on a light
        # panel and on a dark one without choosing a theme.
        d.ellipse([cx - r - 2, cy - r - 2, cx + r + 2, cy + r + 2],
                  outline=(20, 20, 20), width=7)
        d.ellipse([cx - r, cy - r, cx + r, cy + r],
                  outline=(220, 50, 40), width=4)
    im.save(dst)
    print("annotated", dst, im.size)


if __name__ == "__main__":
    main(sys.argv)
