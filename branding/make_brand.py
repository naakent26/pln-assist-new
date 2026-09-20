"""PLN Assist branding generator.

Source: branding/pln_logo_src.png (official PLN mark: red bolt + blue wings on yellow).
Produces the blue/white PLN Assist asset set for every Flutter target.

Run from the branding/ directory:  python make_brand.py
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
FLUTTER = REPO / "flutter"

# --- palette -----------------------------------------------------------------
BLUE_DEEP = (11, 95, 165, 255)   # #0B5FA5  PLN corporate blue
BLUE_LIGHT = (40, 168, 224, 255)  # #28A8E0  PLN bright blue
WHITE = (255, 255, 255, 255)
INK = (16, 40, 74, 255)          # #10284A  dark navy for wordmark on light bg

FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
SOURCE_BBOX_TOL = 60
# -----------------------------------------------------------------------------


def _load_source_masks() -> tuple[np.ndarray, np.ndarray]:
    """Return (bolt_mask, wings_mask) cropped to their shared bounding box."""
    a = np.array(Image.open(HERE / "pln_logo_src.png").convert("RGB")).astype(int)

    def cm(c, tol=SOURCE_BBOX_TOL):
        return np.abs(a - np.array(c)).sum(axis=2) < tol

    bolt = cm((230, 42, 43))
    wings = cm((40, 168, 224))

    # drop anti-alias specks, keep the real shapes
    bolt = ndimage.binary_fill_holes(ndimage.binary_opening(bolt, np.ones((3, 3))))
    wings = ndimage.binary_fill_holes(ndimage.binary_opening(wings, np.ones((3, 3))))

    # a wing stroke may pass behind the bolt -> union so nothing is missing
    full = ndimage.binary_fill_holes(bolt | wings)
    ys, xs = np.nonzero(full)
    box = (ys.min(), ys.max() + 1, xs.min(), xs.max() + 1)
    return bolt[box[0]:box[1], box[2]:box[3]], wings[box[0]:box[1], box[2]:box[3]]


def _mask_to_layer(mask: np.ndarray, color: tuple[int, int, int, int]) -> Image.Image:
    """Upscale mask to 1024px tall and paint it with `color`."""
    h = mask.shape[0]
    scale = 1024 / h
    w = int(round(mask.shape[1] * scale))
    im = Image.fromarray((mask * 255).astype(np.uint8), "L").resize((w, 1024), Image.LANCZOS)
    layer = Image.new("RGBA", (w, 1024), color[:3] + (0,))
    layer.putalpha(im.point(lambda v: int(v * color[3] / 255)))
    return layer


BOLT_M, WINGS_M = _load_source_masks()


def mark(size: int, *, on_dark: bool = False, monochrome: bool = False) -> Image.Image:
    """The PLN mark (bolt over wings) rendered at `size` px tall."""
    if monochrome:
        bolt_c, wing_c = WHITE, (255, 255, 255, 170)
    elif on_dark:
        bolt_c, wing_c = WHITE, (255, 255, 255, 190)
    else:
        bolt_c, wing_c = BLUE_DEEP, BLUE_LIGHT

    base = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    # centre both layers on the same 1024x1024 canvas, preserving aspect
    for mask, color in ((WINGS_M, wing_c), (BOLT_M, bolt_c)):
        layer = _mask_to_layer(mask, color)
        base.alpha_composite(layer, ((1024 - layer.width) // 2, 0))
    return base.resize((size, size), Image.LANCZOS)


def tile(size: int, *, pad_ratio: float = 0.20, radius_ratio: float = 0.22) -> Image.Image:
    """App-icon tile: PLN blue rounded square with the white mark inside."""
    ss = 4  # supersample for crisp rounded corners
    big = size * ss
    img = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    ImageDraw.Draw(img).rounded_rectangle(
        (0, 0, big - 1, big - 1), radius=int(big * radius_ratio), fill=BLUE_DEEP
    )
    inner = int(big * (1 - 2 * pad_ratio))
    img.alpha_composite(mark(inner, monochrome=True), ((big - inner) // 2, (big - inner) // 2))
    return img.resize((size, size), Image.LANCZOS)


def lockup(width: int, text_color: tuple[int, int, int, int], *, mark_on_dark: bool) -> Image.Image:
    """Horizontal 'mark + PLN Assist' lockup, transparent background."""
    ss = 2
    W = width * ss
    mark_sz = int(W * 0.155)
    font = ImageFont.truetype(FONT_BOLD, int(W * 0.185))
    label = "PLN Assist"
    tmp = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    tb = tmp.textbbox((0, 0), label, font=font)
    text_w, text_h = tb[2] - tb[0], tb[3] - tb[1]
    gap = int(W * 0.045)
    total_w = mark_sz + gap + text_w
    H = int(max(mark_sz, text_h) * 1.25)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img.alpha_composite(
        mark(mark_sz, on_dark=mark_on_dark), (int(W * 0.012), (H - mark_sz) // 2)
    )
    ImageDraw.Draw(img).text(
        (int(W * 0.012) + mark_sz + gap - tb[0], (H - text_h) // 2 - tb[1]),
        label,
        font=font,
        fill=text_color,
    )
    out = img.crop(img.getbbox())
    return out.resize((round(out.width / ss), round(out.height / ss)), Image.LANCZOS)


def write(path: Path, img: Image.Image) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print(f"  {path.relative_to(REPO)}  {img.width}x{img.height}")


def main() -> None:
    print("PLN Assist branding ->")

    # 1. Flutter in-app assets -------------------------------------------------
    write(FLUTTER / "assets/logo.png", lockup(600, INK, mark_on_dark=False))
    write(FLUTTER / "assets/logo_light.png", lockup(600, INK, mark_on_dark=False))
    write(FLUTTER / "assets/logo_dark.png", lockup(600, WHITE, mark_on_dark=True))
    write(FLUTTER / "assets/icon.png", tile(256))

    # 2. rust/tray/installer icons (res/) --------------------------------------
    for name, sz in (("32x32.png", 32), ("64x64.png", 64), ("128x128.png", 128),
                     ("128x128@2x.png", 256), ("icon.png", 256), ("mac-icon.png", 512)):
        write(REPO / "res" / name, tile(sz))
    tile(256).save(REPO / "res/icon.ico",
                   sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"  res/icon.ico  multi-size")

    # 3. Windows runner --------------------------------------------------------
    tile(256).save(FLUTTER / "windows/runner/resources/app_icon.ico",
                   sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("  flutter/windows/runner/resources/app_icon.ico  multi-size")

    # 4. Android ---------------------------------------------------------------
    dens = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    for d, sz in dens.items():
        d0 = FLUTTER / f"android/app/src/main/res/mipmap-{d}"
        write(d0 / "ic_launcher.png", tile(sz))
        # adaptive foreground: mark only, kept inside the 66% safe zone
        fg = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        m = mark(int(sz * 0.58), monochrome=True)
        fg.alpha_composite(m, ((sz - m.width) // 2, (sz - m.height) // 2))
        write(d0 / "ic_launcher_foreground.png", fg)
        round_tile = Image.new("RGBA", (sz, sz), (0, 0, 0, 0))
        ImageDraw.Draw(round_tile).ellipse((0, 0, sz - 1, sz - 1), fill=BLUE_DEEP)
        mi = mark(int(sz * 0.58), monochrome=True)
        round_tile.alpha_composite(mi, ((sz - mi.width) // 2, (sz - mi.height) // 2))
        write(d0 / "ic_launcher_round.png", round_tile)

    # 5. iOS -------------------------------------------------------------------
    ios = FLUTTER / "ios/Runner/Assets.xcassets/AppIcon.appiconset"
    for f in sorted(ios.glob("Icon-App-*.png")):
        spec = f.stem.replace("Icon-App-", "")
        base, scale = spec.split("@")
        px = int(float(base.split("x")[0]) * int(scale[0]))
        write(f, tile(px))

    # 6. macOS -----------------------------------------------------------------
    write(FLUTTER / "macos/Runner/AppIcon.png", tile(1024))


if __name__ == "__main__":
    main()
