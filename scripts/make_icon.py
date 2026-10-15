"""Render assets/icon.png (256x256): slate tile, amber rounded square + play node.

Run: uv run --with pillow python scripts/make_icon.py. Our own mark, no third-party pixels.
"""

from pathlib import Path

from PIL import Image, ImageDraw

S = 256
img = Image.new("RGBA", (S, S), (2, 6, 23, 255))  # slate-950
d = ImageDraw.Draw(img)
d.rounded_rectangle(
    [44, 44, 212, 212], radius=48, outline=(245, 158, 11, 255), width=14
)  # amber-500
d.polygon([(108, 92), (108, 164), (172, 128)], fill=(245, 158, 11, 255))  # play node = demos run
d.ellipse([188, 52, 208, 72], fill=(52, 211, 153, 255))  # emerald status dot
out = Path(__file__).resolve().parents[1] / "assets" / "icon.png"
out.parent.mkdir(parents=True, exist_ok=True)
img.save(out)
print(f"wrote {out} {img.size}")
