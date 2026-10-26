#!/usr/bin/env python3
"""Render the eight Lunch Board Reader sample test graphics (invented data only).

Cases 1-6 from the 2026-10-22 build plan; cases 7-8 added 2026-10-26
from the revised build brief (s6).

Each PNG mimics a food-truck schedule graphic / event flyer. The matching
answer key lives in answer-key.md / answer-key.json in this same folder.
"""
from PIL import Image, ImageDraw, ImageFont
import os, random

OUT = os.path.dirname(os.path.abspath(__file__))
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(path, size):
    return ImageFont.truetype(path, size)

def canvas(w=900, h=1100, bg=(250, 246, 238)):
    return Image.new("RGB", (w, h), bg)

def title_block(d, w, truck, sub, color=(20, 33, 61)):
    d.rectangle([0, 0, w, 170], fill=color)
    f = F(SERIF_B, 52)
    tw = d.textlength(truck, font=f)
    d.text(((w - tw) / 2, 34), truck, font=f, fill=(255, 255, 255))
    f2 = F(SANS, 30)
    tw2 = d.textlength(sub, font=f2)
    d.text(((w - tw2) / 2, 108), sub, font=f2, fill=(232, 197, 110))

def line(d, y, text, size=36, bold=False, color=(30, 30, 30), x=70):
    d.text((x, y), text, font=F(SANS_B if bold else SANS, size), fill=color)
    return y + size + 22

def save(img, name):
    img.save(os.path.join(OUT, name))
    print(name, img.size)

# ---- Case 1: clean weekly schedule, 5 weekdays, one stop each -------------
img = canvas(); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Smoke Co.", "This week's stops - Oct 26 to Oct 30")
y = 220
rows = [
    ("MONDAY",    "11 AM - 2 PM", "Riverside Sample Lot", "100 River Bend Rd"),
    ("TUESDAY",   "11 AM - 2 PM", "Sampleton Hardware", "220 Main St"),
    ("WEDNESDAY", "4 PM - 7 PM",  "Sample Community Center", "35 Center Ave"),
    ("THURSDAY",  "11 AM - 2 PM", "Northgate Sample Plaza", "780 Northgate Dr"),
    ("FRIDAY",    "11 AM - 3 PM", "Sampleton High School lot", "15 Schoolhouse Ln"),
]
for day, time, place, addr in rows:
    y = line(d, y, day, size=34, bold=True, color=(20, 33, 61))
    y = line(d, y, f"{time}  -  {place}", size=32)
    y = line(d, y, addr, size=30, color=(90, 90, 90))
    y += 18
save(img, "case1-weekly-schedule.png")

# ---- Case 2: two-stop day --------------------------------------------------
img = canvas(h=800); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Taco Cart", "Wednesday Oct 28 - two stops!")
y = 230
y = line(d, y, "LUNCH", size=34, bold=True, color=(20, 33, 61))
y = line(d, y, "11 AM - 1 PM  -  Downtown Sample Square", size=32)
y = line(d, y, "10 Court Sq", size=30, color=(90, 90, 90))
y += 30
y = line(d, y, "DINNER", size=34, bold=True, color=(20, 33, 61))
y = line(d, y, "5 PM - 8 PM  -  Sample Brewing Co.", size=32)
y = line(d, y, "410 Ale House Way", size=30, color=(90, 90, 90))
save(img, "case2-two-stop-day.png")

# ---- Case 3: event flyer, address only in the image ------------------------
img = canvas(h=850); d = ImageDraw.Draw(img)
title_block(d, 900, "Sampleton Fall Fest", "Saturday Oct 31 - 5 PM to 9 PM", color=(94, 48, 16))
y = 230
y = line(d, y, "Find the Sample Noodle Wagon at the fest!", size=34, bold=True)
y = line(d, y, "Serving all evening at:", size=32)
y = line(d, y, "Sample Fairgrounds", size=34, bold=True)
y = line(d, y, "900 Fairgrounds Rd", size=32, color=(90, 90, 90))
y = line(d, y, "Live music - Costume contest - Local vendors", size=28)
save(img, "case3-event-flyer.png")

# ---- Case 4: smudged end time (must be flagged, never guessed) -------------
img = canvas(h=800); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Burger Bus", "Friday Oct 30")
y = 230
y = line(d, y, "Serving lunch and dinner at:", size=32)
y = line(d, y, "Sample Auto Parts, 640 Mechanic St", size=34, bold=True)
f = F(SANS_B, 40)
d.text((70, y), "Hours: 11 AM - ", font=f, fill=(30, 30, 30))
x_end = 70 + d.textlength("Hours: 11 AM - ", font=f)
d.text((x_end, y), "7 PM", font=f, fill=(30, 30, 30))
# coffee-stain smudge over the end time
random.seed(4)
for _ in range(260):
    cx = random.gauss(x_end + 45, 34); cy = random.gauss(y + 22, 15)
    r = random.randint(4, 13)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(101, 67, 33))
save(img, "case4-smudged-time.png")

# ---- Case 5: place name, no street address ---------------------------------
img = canvas(h=750); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Coffee Cart", "Tuesday Oct 27")
y = 230
y = line(d, y, "7 AM - 10 AM", size=36, bold=True)
y = line(d, y, "Find us at the old mill pavilion", size=34)
y = line(d, y, "down by the river - see you there!", size=30, color=(90, 90, 90))
save(img, "case5-no-address.png")

# ---- Case 6: out-of-town stop ----------------------------------------------
img = canvas(h=750); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Smoke Co.", "Saturday Oct 31 - road trip!")
y = 230
y = line(d, y, "11 AM - 3 PM", size=36, bold=True)
y = line(d, y, "Henderson Sample Market", size=34, bold=True)
y = line(d, y, "55 Market St, Henderson, KY", size=32, color=(90, 90, 90))
save(img, "case6-out-of-town.png")

# ---- Case 7: private / employees-only stop (omit it + PRIVATE_STOP flag) ---
img = canvas(h=900); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Burger Bus", "Wednesday + Thursday this week")
y = 230
y = line(d, y, "WEDNESDAY", size=34, bold=True, color=(20, 33, 61))
y = line(d, y, "11 AM - 1 PM  -  Sample Manufacturing", size=32)
y = line(d, y, "- employees only", size=30, color=(90, 90, 90))
y += 30
y = line(d, y, "THURSDAY", size=34, bold=True, color=(20, 33, 61))
y = line(d, y, "11 AM - 2 PM  -  Sample Public Library", size=32)
y = line(d, y, "5 Book Ln", size=30, color=(90, 90, 90))
save(img, "case7-private-stop.png")

# ---- Case 8: Sunday post naming Monday (week ambiguous -> WEEK_UNCLEAR) ----
img = canvas(h=700); d = ImageDraw.Draw(img)
title_block(d, 900, "Sample Taco Cart", "Next stop")
y = 260
text8 = "Monday \u2014 11 AM\u20132 PM \u2014 Downtown Sample Square, 10 Court Sq"
size8 = 30
while d.textlength(text8, font=F(SANS, size8)) > 760 and size8 > 16:
    size8 -= 1
d.text((70, y), text8, font=F(SANS, size8), fill=(30, 30, 30))
save(img, "case8-sunday-post.png")
