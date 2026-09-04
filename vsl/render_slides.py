#!/usr/bin/env python3
"""
render_slides.py — SecondBloom "Second Bloom Method" VSL silent slideshow renderer.
UPPERCASE slides (plum bg, rose/blush/white text) -> 1920x1080 PNGs -> ~5:00 MP4.
Requires: ImageMagick (convert), FFmpeg.
"""
import os, subprocess

BASE = os.path.dirname(os.path.abspath(__file__))
SLIDES_DIR = os.path.join(BASE, "slides")
OUT_MP4 = os.path.join(BASE, "vsl-slideshow.mp4")
FONT = "DejaVu-Sans-Bold"
BG = "#241019"
ROSE = "#ff7b9c"    # emphasis
BLUSH = "#ffc2d1"   # mechanism
WHITE = "#ffffff"   # body

SLIDES = [
    ("YOU'VE SEEN THE VIDEOS", "white"),
    ("THE ONES WITH 4.17 BILLION VIEWS", "white"),
    ('"SECOND PUBERTY"', "rose"),
    ("PERIMENOPAUSE", "white"),
    ("MILLIONS OF WOMEN. SAME STORY.", "white"),
    ("HOT FLASHES AT 2 AM", "white"),
    ("BRAIN FOG AT 3 PM", "white"),
    ("MOODS WITH NO NAME", "white"),
    ("WEIGHT THAT WON'T BUDGE", "white"),
    ("AND THE COMMENT SECTION?", "rose"),
    ('"I THOUGHT I WAS LOSING MY MIND"', "white"),
    ('"MY DOCTOR SAYS IT\'S NORMAL"', "white"),
    ('"WHAT DO I DO?"', "rose"),
    ("THAT'S THE QUESTION NOBODY ANSWERS", "rose"),
    ("THE AWARENESS IS HERE", "white"),
    ("THE MANUAL ISN'T", "rose"),
    ("SO LET ME ASK YOU SOMETHING", "white"),
    ("DO YOU WAKE UP SOAKED?", "white"),
    ("DO YOU FORGET WORDS MID-SENTENCE?", "white"),
    ("DO YOU CRY AT DOG COMMERCIALS?", "white"),
    ("IF YOU'RE 35 TO 55...", "rose"),
    ("THIS ISN'T IN YOUR HEAD", "rose"),
    ("IT'S YOUR HORMONES", "white"),
    ("CHANGING YOUR OPERATING SYSTEM", "white"),
    ("AND HERE'S WHAT NO ONE TELLS YOU", "rose"),
    ("PERIMENOPAUSE STARTS 8 TO 10 YEARS EARLY", "white"),
    ("FOR MOST WOMEN: THE LATE 30s", "white"),
    ("TOO YOUNG? NO.", "rose"),
    ("YOU'RE EXACTLY ON SCHEDULE", "white"),
    ('BUT THE DOCTOR SAYS "IT\'S NORMAL"', "white"),
    ('THE BLOODWORK COMES BACK "FINE"', "white"),
    ("AND YOU LEAVE FEELING CRAZY", "white"),
    ("WITH 34 SYMPTOMS AND ZERO PLAN", "rose"),
    ("SO YOU TRY THE INTERNET", "white"),
    ("SUPPLEMENTS. CREAMS. PROTOCOLS.", "white"),
    ("EVERY INFLUENCER HAS A DIFFERENT ANSWER", "white"),
    ("AND NONE OF THEM KNOW YOUR BODY", "white"),
    ("THIS IS THE TRAP", "rose"),
    ("AWARENESS WITHOUT A ROADMAP", "white"),
    ("IS JUST ANXIETY WITH A HASHTAG", "rose"),
    ("WHAT ACTUALLY WORKS?", "rose"),
    ("A SEQUENCE", "rose"),
    ("THE RIGHT ORDER OF OPERATIONS", "white"),
    ("BASED ON THE RESEARCH", "white"),
    ("AND ON WHAT THOUSANDS OF WOMEN REPORT BACK", "white"),
    ("I CALL IT THE SECOND BLOOM METHOD", "rose"),
    ("FIVE STAGES. ONE JOB EACH. 30 MINUTES A DAY.", "blush"),
    ("STAGE ONE: B — BASELINE", "blush"),
    ("THE 7-DAY SECOND PUBERTY CENSUS", "blush"),
    ("34 SYMPTOMS. ONE TRACKER.", "blush"),
    ("IN A WEEK? YOU KNOW EXACTLY WHAT YOUR BODY IS DOING", "blush"),
    ("THE MOST USEFUL DOCUMENT YOU'LL EVER HAND A DOCTOR", "rose"),
    ("STAGE TWO: L — LIGHTS OUT", "blush"),
    ("THE COOL SLEEP SYSTEM", "blush"),
    ("END THE 2 AM FURNACE", "blush"),
    ("LAYERED BEDDING. 12-STEP WIND-DOWN.", "blush"),
    ("60-SECOND COOL-DOWN SCRIPTS", "blush"),
    ("SLEEP LIKE YOU DID IN YOUR 20s", "rose"),
    ("STAGE THREE: O — OPTIMIZE", "blush"),
    ("THE HORMONE FOOD MAP", "blush"),
    ("WHICH FOODS HELP. WHICH \"HEALTHY\" FOODS HURT.", "blush"),
    ("THE SUPPLEMENT CHEAT-SHEET", "blush"),
    ("EVIDENCE VS. EXPENSIVE PEE", "rose"),
    ("PLUS THE 10-MINUTE STRENGTH & BONE BUILDER", "blush"),
    ("NO GYM. NO EQUIPMENT. BONES THAT LAST.", "blush"),
    ("STAGE FOUR: O — OPEN UP", "blush"),
    ("THE MOOD & BRAIN-FOG TOOLKIT", "blush"),
    ("90-SECOND RESETS FOR PANIC", "blush"),
    ("WORKAROUNDS FOR THE 3 PM WALL", "blush"),
    ("TURN CHAOS INTO DATA", "blush"),
    ("STAGE FIVE: M — MASTER", "blush"),
    ("THE DOCTOR VISIT SCRIPTS", "blush"),
    ("WORD FOR WORD. WHAT TO SAY.", "blush"),
    ("WHAT TO SAY WHEN THEY DISMISS YOU", "rose"),
    ("THE PLAIN-ENGLISH HRT GUIDE", "blush"),
    ("THE PARTNER CONVERSATION", "blush"),
    ("AND YOUR 90-DAY THRIVE PLAN", "blush"),
    ("EIGHT DONE-FOR-YOU TOOLS", "rose"),
    ("CENSUS. SLEEP SYSTEM. RESCUE KIT. FOOD MAP.", "white"),
    ("STRENGTH BUILDER. MOOD TOOLKIT. DOCTOR SCRIPTS.", "white"),
    ("ALL PRINTABLE. ALL PLAIN ENGLISH. ALL YOURS.", "white"),
    ("WOMEN ARE ALREADY BLOOMING", "rose"),
    ('"MY DOCTOR APOLOGIZED AFTER I BROUGHT IN THE TRACKER" — RACHEL, 44', "white"),
    ('"EIGHT MONTHS OF \'YOU\'RE FINE\' ENDED IN ONE VISIT" — SIMONE, 39', "white"),
    ('"WE BOTH GOT OUR MARRIAGE BACK" — KAREN, 51', "white"),
    ("THE FULL SYSTEM IS $79", "white"),
    ("TODAY, LAUNCH PRICING: $19", "rose"),
    ("LESS THAN ONE NIGHT OF DELIVERY FOOD", "white"),
    ("ONE PAYMENT. LIFETIME ACCESS. NO UPSALES.", "white"),
    ("AND YOU'RE COVERED", "rose"),
    ("60 DAYS. FULL REFUND. KEEP EVERYTHING.", "white"),
    ("THE RISK IS OURS. NOT YOURS.", "rose"),
    ("YOU SURVIVED YOUR FIRST PUBERTY", "rose"),
    ("YOU'RE GOING TO BLOOM THROUGH THIS ONE", "rose"),
    ("YOU JUST NEED THE RIGHT MAP", "white"),
    ("CLICK THE BUTTON", "white"),
    ("START THE CENSUS TONIGHT", "white"),
    ("AND GET YOUR 2 AM SELF BACK", "white"),
    ("SECOND BLOOM", "rose"),
    ("THE CHANGE, MANAGED", "blush"),
    ("SECONDBLOOM.VERCEL.APP — $19", "white"),
]

def render():
    os.makedirs(SLIDES_DIR, exist_ok=True)
    colors = {"white": WHITE, "rose": ROSE, "blush": BLUSH}
    for i, (text, color) in enumerate(SLIDES, 1):
        # wrap long lines
        words = text.split()
        lines, cur = [], ""
        for w in words:
            if len(cur) + len(w) + 1 > 26:
                lines.append(cur); cur = w
            else:
                cur = (cur + " " + w).strip()
        if cur: lines.append(cur)
        joined = "\n".join(lines)
        pts = 84 if max(len(l) for l in lines) <= 18 else 72
        out = os.path.join(SLIDES_DIR, f"slide_{i:03d}.png")
        subprocess.run([
            "convert", "-size", "1920x1080", "xc:" + BG,
            "-gravity", "center",
            "-font", FONT, "-pointsize", str(pts), "-fill", colors[color],
            "-annotate", "+0+0", joined,
            "-bordercolor", BG, "-border", "0",
            out,
        ], check=True)
    print(f"rendered {len(SLIDES)} slides")

    # build MP4: scale per-slide duration to hit ~5:00 total (300s / n slides)
    dur = round(300.0 / len(SLIDES), 2)
    with open(os.path.join(BASE, "slides.txt"), "w") as f:
        for i in range(1, len(SLIDES) + 1):
            f.write(f"file 'slides/slide_{i:03d}.png'\n")
            f.write(f"duration {dur}\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", os.path.join(BASE, "slides.txt"),
        "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "20",
        "-movflags", "+faststart", OUT_MP4,
    ], check=True, capture_output=True)
    print("mp4 written:", OUT_MP4)

if __name__ == "__main__":
    render()
