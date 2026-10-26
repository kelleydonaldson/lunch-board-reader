#!/usr/bin/env python3
"""Render the six HELD-OUT Lunch Board Reader test graphics (invented data only).

Built 2026-10-26 from the owner's held-out work order. The answer key
(heldout-key.json / heldout-key.md in this folder) was written FIRST;
these graphics must match it, never the other way around. Siblings of
the main kit: same canvas, title block and line helpers as
../sample-cases-2026-10-23/make_sample_cases.py, plus one hostile
treatment per case (geometry / typography / resolution / cancellation
/ joint post / typo'd time).
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io, os, random
import numpy as np

OUT = os.path.dirname(os.path.abspath(__file__))
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DISPLAY_B = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Black.ttf"
DISPLAY_BI = "/usr/share/fonts/truetype/noto/NotoSerifDisplay-BlackItalic.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

def canvas(w=900, h=1100, bg=(250, 246, 238)):
    return Image.new("RGB", (w, h), bg)

def title_block(d, w, truck, sub, color=(20, 33, 61), font=SERIF_B):
    d.rectangle([0, 0, w, 170], fill=color)
    f = F(font, 52)
    tw = d.textlength(truck, font=f)
    d.text(((w - tw) / 2, 34), truck, font=f, fill=(255, 255, 255))
    f2 = F(SANS, 30)
    tw2 = d.textlength(sub, font=f2)
    d.text(((w - tw2) / 2, 108), sub, font=f2, fill=(232, 197, 110))

def line(d, y, text, size=36, bold=False, color=(30, 30, 30), x=70, font=None):
    path = font or (SANS_B if bold else SANS)
    d.text((x, y), text, font=F(path, size), fill=color)
    return y + size + 22

def save(img, name):
    img.save(os.path.join(OUT, name))
    print(name, img.size)

# ---- H1: weekly schedule, then 'photographed' (skew/shadow/vignette) ------
card = canvas(); d = ImageDraw.Draw(card)
title_block(d, 900, "Sample Grill Wagon", "This week's stops - Nov 2 to Nov 6")
y = 220
rows = [
    ("MONDAY",    "11 AM - 2 PM", "Lakeside Sample Park", "88 Shore Dr"),
    ("TUESDAY",   "11 AM - 2 PM", "Sampleton Post Office", "12 Postal Way"),
    ("WEDNESDAY", "4 PM - 8 PM",  "Sample Bowling Alley", "300 Strike Ln"),
    ("THURSDAY",  "11 AM - 2 PM", "Westside Sample Market", "415 Sunset Blvd"),
    ("FRIDAY",    "11 AM - 3 PM", "Sampleton Fire Station", "7 Engine Ct"),
]
for day, time, place, addr in rows:
    y = line(d, y, day, size=34, bold=True, color=(20, 33, 61))
    y = line(d, y, f"{time}  -  {place}", size=32)
    y = line(d, y, addr, size=30, color=(90, 90, 90))
    y += 18

# photo treatment: warm 'table' background, soft drop shadow, perspective.
W, H = 1280, 1420
photo = Image.new("RGB", (W, H), (126, 99, 76))
pd = ImageDraw.Draw(photo)
random.seed(11)
for _ in range(2600):  # faint tabletop grain
    gx, gy = random.randint(0, W - 1), random.randint(0, H - 1)
    shade = random.randint(-9, 9)
    pd.point((gx, gy), fill=(126 + shade, 99 + shade, 76 + shade))
quad = [(150, 120), (1150, 55), (1200, 1310), (70, 1360)]  # TL TR BR BL
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)
sd.polygon([(x + 26, y + 34) for x, y in quad], fill=(0, 0, 0, 130))
photo = Image.alpha_composite(photo.convert("RGBA"),
                              shadow.filter(ImageFilter.GaussianBlur(18)))

def persp_coeffs(pa, pb):
    """Coefficients mapping output (pb) points back to input (pa) points."""
    matrix = []
    for p1, p2 in zip(pa, pb):
        matrix.append([p1[0], p1[1], 1, 0, 0, 0, -p2[0] * p1[0], -p2[0] * p1[1]])
        matrix.append([0, 0, 0, p1[0], p1[1], 1, -p2[1] * p1[0], -p2[1] * p1[1]])
    A = np.array(matrix, dtype=float)
    B = np.array(pb, dtype=float).reshape(8)
    return np.linalg.solve(A, B)

src = [(0, 0), (900, 0), (900, 1100), (0, 1100)]
warped = card.transform((W, H), Image.PERSPECTIVE, persp_coeffs(quad, src),
                        Image.BICUBIC)
mask = Image.new("L", (900, 1100), 255).transform(
    (W, H), Image.PERSPECTIVE, persp_coeffs(quad, src), Image.BICUBIC)
photo.paste(warped, (0, 0), mask)
# vignette: darken toward the corners
vig = Image.radial_gradient("L").resize((W, H))
vig = vig.point(lambda v: 255 - int((255 - v) * 0.42))
photo = Image.composite(photo, Image.new("RGBA", (W, H), (18, 12, 6, 255)), vig)
save(photo.convert("RGB"), "h1-skewed-photo.png")

# ---- H2: decorative display font on a busy patterned background ------------
img = canvas(h=980, bg=(252, 243, 226)); d = ImageDraw.Draw(img)
# busy background: two-tone polka dots
for gy in range(12, 980, 58):
    for gx in range(12, 900, 58):
        off = 29 if (gy // 58) % 2 else 0
        col = (244, 205, 150) if ((gx + gy) // 58) % 2 else (238, 183, 178)
        d.ellipse([gx + off, gy, gx + off + 21, gy + 21], fill=col)
# busy border: checkerboard strips on all four edges
for bx in range(0, 900, 30):
    for by, bh in ((0, 30), (950, 30)):
        col = (94, 41, 92) if (bx // 30) % 2 == 0 else (240, 201, 110)
        d.rectangle([bx, by, bx + 30, by + bh], fill=col)
for by in range(30, 950, 30):
    for bx, bw in ((0, 30), (870, 30)):
        col = (94, 41, 92) if (by // 30) % 2 == 0 else (240, 201, 110)
        d.rectangle([bx, by, bx + bw, by + 30], fill=col)
# title band
d.rectangle([30, 30, 870, 220], fill=(94, 41, 92))
f = F(DISPLAY_B, 54)
t = "Sample Dumpling Cart"
d.text(((900 - d.textlength(t, font=f)) / 2, 62), t, font=f, fill=(255, 246, 226))
f2 = F(DISPLAY_BI, 32)
t2 = "Wednesday Nov 4 - two stops!"
d.text(((900 - d.textlength(t2, font=f2)) / 2, 140), t2, font=f2, fill=(240, 201, 110))
# stops, all in the decorative face
y = 290
y = line(d, y, "LUNCH", size=40, color=(94, 41, 92), x=80, font=DISPLAY_B)
y = line(d, y, "11 AM - 1 PM", size=38, color=(30, 30, 30), x=80, font=DISPLAY_B)
y = line(d, y, "Sampleton Bookstore", size=38, color=(30, 30, 30), x=80, font=DISPLAY_B)
y = line(d, y, "64 Novel St", size=34, color=(90, 60, 60), x=80, font=DISPLAY_B)
y += 44
y = line(d, y, "DINNER", size=40, color=(94, 41, 92), x=80, font=DISPLAY_B)
y = line(d, y, "5 PM - 9 PM", size=38, color=(30, 30, 30), x=80, font=DISPLAY_B)
y = line(d, y, "Sample Vineyard", size=38, color=(30, 30, 30), x=80, font=DISPLAY_B)
y = line(d, y, "900 Grapevine Rd", size=34, color=(90, 60, 60), x=80, font=DISPLAY_B)
save(img, "h2-decorative-font.png")

# ---- H3: low-res screenshot (downscale + JPEG artifacts, facts legible) ----
big = canvas(w=920, h=1160); d = ImageDraw.Draw(big)
title_block(d, 920, "Sample Slice Truck", "Thursday Nov 5 - two stops!")
y = 260
y = line(d, y, "LUNCH", size=46, bold=True, color=(20, 33, 61), x=60)
y = line(d, y, "11 AM - 2 PM  -  Northgate Sample Mall", size=42, x=60)
y = line(d, y, "1200 Retail Row", size=40, color=(90, 90, 90), x=60)
y += 40
y = line(d, y, "DINNER", size=46, bold=True, color=(20, 33, 61), x=60)
y = line(d, y, "4 PM - 7 PM  -  Sampleton Skate Park", size=42, x=60)
y = line(d, y, "33 Wheel Way", size=40, color=(90, 90, 90), x=60)
small = big.resize((460, 580), Image.LANCZOS)
buf = io.BytesIO()
small.save(buf, format="JPEG", quality=42)   # bake in compression artifacts
buf.seek(0)
save(Image.open(buf).convert("RGB"), "h3-low-res.png")

# ---- H4: three-stop day, middle stop struck through + CANCELED stamp -------
img = canvas(h=1020); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Curry Cart", "Friday Nov 6 - three stops")
y = 230
y = line(d, y, "11 AM - 1 PM  -  Sampleton City Hall", size=33, bold=True)
y = line(d, y, "1 Civic Plaza", size=30, color=(90, 90, 90))
y += 34
mid_top = y
y = line(d, y, "2 PM - 4 PM  -  Sample Farmers Market", size=33, bold=True)
y = line(d, y, "250 Harvest Ave", size=30, color=(90, 90, 90))
mid_bot = y
# strikethrough: two heavy lines across the whole middle block
for yy in (mid_top + 24, mid_top + 82):
    d.line([(55, yy), (845, yy - 12)], fill=(178, 30, 30), width=7)
# CANCELED stamp, rotated, across the middle block
stamp = Image.new("RGBA", (520, 130), (0, 0, 0, 0))
sd = ImageDraw.Draw(stamp)
sf = F(SANS_B, 64)
st = "CANCELED"
tw = sd.textlength(st, font=sf)
sd.rectangle([6, 6, 514, 124], outline=(178, 30, 30, 235), width=6)
sd.text(((520 - tw) / 2, 30), st, font=sf, fill=(178, 30, 30, 235))
stamp = stamp.rotate(-14, expand=True)
img.paste(stamp, (190, mid_top - 16), stamp)
y += 34
y = line(d, y, "5 PM - 8 PM  -  Sample Community Theater", size=33, bold=True)
y = line(d, y, "77 Stage Door Ln", size=30, color=(90, 90, 90))
save(img, "h4-canceled-stop.png")

# ---- H5: two-truck collab, joint header, per-stop truck labels -------------
img = canvas(h=860); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 900, 170], fill=(20, 33, 61))
hdr = "Sample Smoke Co. × Sample Taco Cart"
size = 46
while d.textlength(hdr, font=F(SERIF_B, size)) > 850 and size > 20:
    size -= 1
fh = F(SERIF_B, size)
d.text(((900 - d.textlength(hdr, font=fh)) / 2, 44), hdr, font=fh, fill=(255, 255, 255))
f2 = F(SANS, 30)
t2 = "Saturday Nov 7 - popping up together!"
d.text(((900 - d.textlength(t2, font=f2)) / 2, 112), t2, font=f2, fill=(232, 197, 110))
y = 240
y = line(d, y, "Sample Smoke Co.", size=36, bold=True, color=(20, 33, 61))
y = line(d, y, "11 AM - 2 PM  -  Riverside Sample Lot", size=33)
y = line(d, y, "100 River Bend Rd", size=30, color=(90, 90, 90))
y += 40
y = line(d, y, "Sample Taco Cart", size=36, bold=True, color=(20, 33, 61))
y = line(d, y, "4 PM - 7 PM  -  Sample Fairgrounds", size=33)
y = line(d, y, "900 Fairgrounds Rd", size=30, color=(90, 90, 90))
save(img, "h5-two-truck-collab.png")

# ---- H6: typo'd end time, printed exactly '11 AM - 2' ----------------------
img = canvas(h=700); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Waffle Wagon", "Tuesday Nov 3")
y = 230
y = line(d, y, "11 AM - 2", size=40, bold=True)
y = line(d, y, "Sampleton Depot", size=34, bold=True)
y = line(d, y, "19 Rail Spur", size=32, color=(90, 90, 90))
save(img, "h6-typo-time.png")
