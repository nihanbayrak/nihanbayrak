"""Throwaway mockup: card A1 in dark green, rebuilt after the scratch folder was wiped.

    python3 mockup.py OUT.html [PHOTO]

With PHOTO: cuts her out with Apple's on-device person segmentation (segment.swift) and draws
the ASCII portrait from it. Without: a noise placeholder, enough to test the animation.

Animation fixes carried over from round 5:
- Portrait frames all run one shared step-end cycle with no delay; frame k's window is
  written into its keyframes, so hand-offs share one keyframe value and exactly one frame is
  visible at every instant.
- The typed line steps to each glyph's measured right edge (VOICE_ADV, measured in Chrome at
  Fraunces italic 300, 19px), so letters appear whole and the line ends on time.
"""
import random, subprocess, sys
from html import escape
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter, ImageOps

HERE = Path(__file__).parent
W, H = 830, 420
GROUND, MID, PALE = "#0B3B2E", "#4FA383", "#D3F2E4"
N_FRAMES, FLIP, CYCLE = 8, 1.6, 18

ROWS = [
    ("title", "nihan@bayrak"),
    ("pair", "Based", "Berlin · TR, EN, DE"),
    ("pair", "Uptime", "9 years, 1 month, 27 days"),
    ("pair", "Kernel", "Evals, agents, honest interfaces"),
    ("pair", "Shell", "Claude Code, zsh"),
    ("blank",),
    ("section", "Now"),
    ("pair", "Measuring", "Can an LLM judge copyright risk?"),
    ("pair", "Designing", "Conscious Eyes: the label, at a glance"),
    ("pair", "Guarding", "Prompt-injection scans for chat logs"),
    ("blank",),
    ("section", "GitHub"),
    ("pair", "Commits", "438 · Repos 16 · Followers 29"),
]
VOICE = [
    "Engineering with an editor's eye.",
    "I speak Python, fashion and three human languages.",
    "Where the model meets the moodboard.",
]
VOICE_ADV = [
    [11.53, 22.09, 31.43, 36.94, 47.62, 56.3, 64.81, 73.1, 78.61, 89.16, 98.49, 102.37, 115.56, 121, 127.2, 137.66, 141.54, 151.22, 161.9, 165.78, 174.46, 184.5, 189.95, 196.3, 205.51, 213.75, 216.57, 224.19, 228.07, 236.52, 245.31, 253.98, 257.81],
    [6.71, 10.59, 18.06, 27.89, 36.56, 46.26, 56.18, 60.06, 71.97, 81.1, 87.3, 97.76, 106.97, 117.65, 121.57, 125.46, 130.61, 140.42, 147.77, 158.23, 163.67, 172.87, 183.55, 187.44, 197.12, 207.79, 217.91, 221.8, 228, 238.46, 246.43, 255.11, 263.78, 267.66, 277.97, 288.52, 303.71, 313.39, 324.07, 327.96, 333.53, 343.21, 353.77, 363.11, 373.73, 383.57, 392.87, 401.29, 408.91, 412.72],
    [17.4, 27.87, 36.38, 44.36, 53.03, 56.91, 63.11, 73.57, 82.25, 86.13, 101.47, 110.97, 121.09, 129.33, 134.9, 138.79, 154.13, 162.81, 171.45, 178.04, 185.65, 189.54, 195.74, 206.2, 214.87, 218.76, 234.1, 243.59, 253.09, 263.21, 273.23, 282.73, 292.41, 300.38, 310.5, 314.33],
]


def brightness(photo_path, cols, rows):
    """0..1 per cell: her face and hair, contrast-stretched inside the person mask."""
    if photo_path is None:
        return np.random.default_rng(1).random((rows, cols)) * 0.8
    photo = ImageOps.exif_transpose(Image.open(photo_path)).convert("RGB")
    photo.thumbnail((1500, 2000))
    src, mask_png = HERE / "photo.png", HERE / "mask.png"
    photo.save(src)
    subprocess.run(["swift", str(HERE / "segment.swift"), str(src), str(mask_png)], check=True)
    mask = Image.open(mask_png).convert("L").resize(photo.size)
    # face and hair, square; tuned on the 1500x2000 photo she sent, rescale for others
    sx, sy = photo.size[0] / 1500, photo.size[1] / 2000
    box = (int(300 * sx), int(120 * sy), int(1150 * sx), int(970 * sy))
    photo, mask = photo.crop(box), mask.crop(box)
    m = np.asarray(mask.resize((cols, rows), Image.BOX), dtype=float) / 255
    m = np.clip((m - 0.45) / 0.25, 0, 1)              # drops faint people in the background
    g = ImageOps.autocontrast(ImageOps.grayscale(photo), cutoff=(2, 1), mask=mask.point(lambda v: 255 if v > 140 else 0))
    g = g.filter(ImageFilter.UnsharpMask(8, 220, 1))
    return (np.asarray(g.resize((cols, rows), Image.BOX), dtype=float) / 255) ** 1.7 * m


def pct(x):
    return f"{x:.4f}%"


def flip_css(p):
    css = []
    for k in range(N_FRAMES):
        a, b = pct(100 * k / N_FRAMES), pct(100 * (k + 1) / N_FRAMES)
        if k == 0:
            kf = f"0%{{opacity:1}}{b}{{opacity:0}}100%{{opacity:0}}"
        elif k == N_FRAMES - 1:
            kf = f"0%{{opacity:0}}{a}{{opacity:1}}100%{{opacity:1}}"
        else:
            kf = f"0%{{opacity:0}}{a}{{opacity:1}}{b}{{opacity:0}}100%{{opacity:0}}"
        css.append(f"@keyframes {p}f{k}{{{kf}}}.{p}f{k}{{animation:{p}f{k} {FLIP}s step-end infinite}}")
    return "\n".join(css)


def voice(p, x, y, size):
    out = []
    for j, (text, adv) in enumerate(zip(VOICE, VOICE_ADV)):
        n, width = len(text), adv[-1] + 2
        edges = [0] + [a + 1.5 for a in adv]
        frames = [(12 * i / n, edges[i] / width) for i in range(n + 1)]                 # type
        frames += [(28 + 4 * (n - i) / n, edges[i] / width) for i in range(n, -1, -1)]  # erase
        kf = "".join(f"{pct(t)}{{transform:scaleX({s:.4f})}}" for t, s in frames) + "100%{transform:scaleX(0)}"
        delay = -CYCLE + j * CYCLE / len(VOICE)
        out.append(f"""<defs><mask id="{p}v{j}"><rect class="{p}v{j}" x="{x}" y="{y - size}" width="{width:.2f}" height="{size * 1.5}" fill="#fff"/></mask></defs>
<style>.{p}v{j}{{transform-box:fill-box;transform-origin:left;transform:scaleX(0);animation:{p}v{j} {CYCLE}s step-end {delay}s infinite}}
@keyframes {p}v{j}{{{kf}}}</style>
<text x="{x}" y="{y}" mask="url(#{p}v{j})" font-family="Fraunces" font-style="italic" font-weight="300" font-size="{size}" fill="{PALE}">{escape(text)}</text>""")
    return "\n".join(out)


def card(b, p="c"):
    random.seed(11)
    ramp = " .,:;i1tfLCG08@"
    rows, cols = b.shape
    s = [f"""<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" style="display:block;border-radius:6px">
<defs><filter id="{p}grain"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/>
<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter></defs><rect width="{W}" height="{H}" fill="{GROUND}"/>""",
         f"<style>{flip_css(p)}</style>"]
    for k in range(N_FRAMES):
        jitter = np.random.default_rng(k).uniform(-0.09, 0.09, b.shape)
        v = np.where(b > 0.02, np.clip(b + jitter, 0, 1), 0)
        band = range(r0 := random.randrange(8, rows - 8), r0 + 3) if k in (3, 6) else range(0)
        shift = random.choice((-3, -2, 2, 3))
        s.append(f'<g class="{p}f{k}" font-family="JetBrains Mono" font-size="8.6" fill="{PALE}">')
        for r in range(rows):
            chars = [ramp[min(len(ramp) - 1, int(v[r, c] * (len(ramp) - 1) + 0.5))] for c in range(cols)]
            if r in band:
                chars = chars[-shift:] + chars[:-shift]
            s.append(f'<text x="20" y="{22 + r * 9.2}" xml:space="preserve">{escape("".join(chars))}</text>')
        s.append("</g>")
    x0, width, lh = 384, 52, 22
    s.append('<g font-family="JetBrains Mono" font-size="12">')
    for j, row in enumerate(ROWS):
        y = 40 + j * lh
        if row[0] == "title":
            s.append(f'<text x="{x0}" y="{y}" fill="{PALE}">{row[1]} <tspan fill="{MID}">{"─" * (width - len(row[1]) - 1)}</tspan></text>')
        elif row[0] == "section":
            s.append(f'<text x="{x0}" y="{y}" fill="{MID}">─ <tspan fill="{PALE}">{row[1]}</tspan> {"─" * (width - len(row[1]) - 3)}</text>')
        elif row[0] == "pair":
            s.append(f'<text x="{x0}" y="{y}" fill="{MID}">{row[1]}<tspan opacity=".6"> {"." * (12 - len(row[1]))}</tspan>'
                     f'<tspan fill="{PALE}"> {escape(row[2])}</tspan></text>')
    s.append("</g>")
    s.append(voice(p, x0, 372, 19))
    s.append(f'<rect width="{W}" height="{H}" filter="url(#{p}grain)" opacity=".08" style="mix-blend-mode:screen"/></svg>')
    return "\n".join(s)


def page(b):
    graph = "".join(f'<span style="width:9px;height:9px;border-radius:2px;background:{["#eff2f5","#aceebb","#4ac26b","#2da44e","#116329"][min(4, int(((i * 7919) % 23) / 5))] if (i * 31) % 3 else "#eff2f5"}"></span>' for i in range(7 * 53))
    return f"""<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@1,9..144,300&family=JetBrains+Mono&display=swap">
<h2>A1 in dark green: new lines</h2>
<p class="subtitle">Deep viridian ground, one green in three depths. It sits beside GitHub's green contribution graph instead of fighting it.
Fixed: the portrait no longer blinks out between frames, and the italic line now types whole letters and finishes on time.</p>
<div class="mockup"><div class="mockup-header">github.com/nihanbayrak · README card</div><div class="mockup-body" style="padding:0">{card(b, "c")}</div></div>
<div class="mockup" style="margin-top:20px"><div class="mockup-header">On GitHub's white page, next to its graph</div>
<div class="mockup-body" style="background:#fff;padding:18px">
<div style="border:1px solid #d1d9e0;border-radius:6px;padding:14px"><div style="font:12px system-ui;color:#59636e;margin-bottom:8px">nihanbayrak / README.md</div>{card(b, "d")}</div>
<div style="margin-top:14px;border:1px solid #d1d9e0;border-radius:6px;padding:12px"><div style="font:13px system-ui;color:#1f2328;margin-bottom:8px">339 contributions in the last year</div>
<div style="display:grid;grid-auto-flow:column;grid-template-rows:repeat(7,9px);gap:3px">{graph}</div></div>
</div></div>"""


if __name__ == "__main__":
    out = Path(sys.argv[1])
    photo = sys.argv[2] if len(sys.argv) > 2 else None
    out.write_text(page(brightness(photo, 66, 42)))
    print(out, out.stat().st_size // 1024, "KB")
