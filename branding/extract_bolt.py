"""Extract the PLN lightning-bolt silhouette from the source logo into a clean alpha mask."""
from PIL import Image
import numpy as np
from scipy import ndimage

SRC = "pln_logo_src.png"
OUT = "bolt_mask.png"

im = Image.open(SRC).convert("RGB")
a = np.array(im).astype(int)


def color_mask(c, tol=60):
    return np.abs(a - np.array(c)).sum(axis=2) < tol


red = color_mask((230, 42, 43))
blue = color_mask((40, 168, 224))

# The bolt sits on top in red; the blue copy is the offset drop-shadow behind it.
bolt = red | blue

# keep only the largest connected blob, then fill holes so the mask is solid
lab, n = ndimage.label(bolt)
if n > 1:
    sizes = ndimage.sum(bolt, lab, range(1, n + 1))
    bolt = lab == (int(np.argmax(sizes)) + 1)

bolt = ndimage.binary_fill_holes(bolt)
# remove stray anti-aliasing specks
bolt = ndimage.binary_opening(bolt, structure=np.ones((3, 3)))
bolt = ndimage.binary_fill_holes(bolt)

ys, xs = np.nonzero(bolt)
print("bolt bbox", xs.min(), ys.min(), xs.max(), ys.max(), "px", bolt.sum())

# tight crop, RGBA alpha-only mask
crop = bolt[ys.min(): ys.max() + 1, xs.min(): xs.max() + 1]
alpha = (crop * 255).astype(np.uint8)
mask = np.zeros((*alpha.shape, 4), np.uint8)
mask[..., 3] = alpha
Image.fromarray(mask, "RGBA").save(OUT)
print("saved", OUT, Image.open(OUT).size)
