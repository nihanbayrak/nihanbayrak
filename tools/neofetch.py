"""The profile card: her portrait in signs beside a neofetch readout, moving.

Left, the portrait from data/portrait.json (tools/portrait.py), re-inked as an eight-frame
flipbook. Right, key and value pairs joined by leader dots, the way a terminal system-info
tool prints a machine. Under it, three mottos type themselves out in turn. Uptime counts from the day
the GitHub account opened. Every animation rule lives in tools/motion.py.

One deep green, painted by the card itself, so it is the same on GitHub's light and dark
themes. All type is outlines — JetBrains Mono, and Fraunces italic for the mottos — since
a README image cannot load a font. Each glyph is drawn once and placed with <use>.

    python tools/neofetch.py     # writes assets/card.svg and assets/card-narrow.svg

Design: docs/superpowers/specs/2026-11-22-living-card-design.md
"""
import json
from datetime import date
from pathlib import Path

import motion
import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

GROUND, MID, PALE = "#0B3B2E", "#4FA383", "#D3F2E4"
ROLES = {"text": PALE, "key": MID, "dots": MID, "value": PALE}
RULE = "─"
INFO_COLS, KEY_COLS = 66, 20      # values start at column 22
ART_SIZE, ART_LEAD = 8.6, 9.2
INFO_SIZE, INFO_LEAD = 11, 16
VOICE_SIZE = 19
ALT = "Nihan Bayrak as a moving terminal readout: her portrait drawn in signs beside her details. Berlin."
MOTTOS = [
    "Engineering with an editor's eye.",
    "I speak Python, fashion and three human languages.",
    "Where the model meets the moodboard.",
]


# ---------------------------------------------------------------- content

def uptime(since, today):
    y, m, d = today.year - since.year, today.month - since.month, today.day - since.day
    if d < 0:
        m -= 1
        prev = date(today.year, today.month, 1).toordinal() - 1
        d += date.fromordinal(prev).day
    if m < 0:
        y, m = y - 1, m + 12
    plural = lambda n, w: f"{n} {w}{'' if n == 1 else 's'}"
    return f"{plural(y, 'year')}, {plural(m, 'month')}, {plural(d, 'day')}"


def readout(stats, today):
    """Lines of the readout. A pair is ('pair', key, value). Her words, her keys; keep them.
    uptime is the one live line the nightly redraw updates."""
    return [
        ("title", "nihan@bayrak"),
        ("section", "Profile"),
        ("pair", "role", "AI specialist"),
        ("pair", "dayJob", "AI tools for consumer brands"),
        ("pair", "city", "Berlin"),
        ("pair", "spokenLanguages", "TR, EN, DE"),
        ("pair", "uptime", uptime(date.fromisoformat(stats["created"]), today)),
        ("blank",),
        ("pair", "tools.languages", "Python, TypeScript, SQL"),
        ("pair", "tools.ide", "Claude Code, Xcode, Codex, VS Code, Langdock"),
        ("pair", "tools.shell", "zsh"),
        ("blank",),
        ("pair", "interests.creative", "3D modeling and printing"),
        ("pair", "interests.offScreen", "Modeling, sailing, creating gifts"),
        ("blank",),
        ("section", "Projects"),
        ("pair", "evals", "Copyright risk in image prompts"),
        ("pair", "agents", "Roundtrip · TestFlight feedback triage"),
        ("pair", "product", "Conscious Eyes · iOS label scanner"),
        ("blank",),
        ("section", "Contact"),
        ("pair", "linkedIn", "nihan-bayrak"),
        ("pair", "website", "consciouseyes.app"),
    ]


def spans(line):
    """A readout line as [(text, role)], INFO_COLS columns or fewer."""
    kind = line[0]
    if kind == "title":
        return [(line[1] + " ", "text"), (RULE * (INFO_COLS - len(line[1]) - 1), "dots")]
    if kind == "section":
        return [(RULE + " ", "dots"), (line[1], "text"), (" " + RULE * (INFO_COLS - len(line[1]) - 3), "dots")]
    if kind == "blank":
        return []
    if kind == "pair":
        key, value = line[1], line[2]
        return [(key, "key"), (" " + "." * (KEY_COLS - len(key)), "dots"), (" " + value, "value")]
    raise ValueError(kind)


# ---------------------------------------------------------------- drawing

class Mono:
    """Outlined monospace: each glyph drawn once, placed by column."""

    def __init__(self):
        self.tt, self.glyphset, _, self.upem = typeset._load("mono")
        self.cmap = self.tt.getBestCmap()
        self.adv = self.tt["hmtx"][self.cmap[ord("M")]][0]
        self.ids, self.defs = {}, []

    def ref(self, ch):
        if ch not in self.ids:
            name = self.cmap.get(ord(ch))
            gid = None
            if name and ch.strip():
                pen = typeset.SVGPathPen(self.glyphset, ntos=lambda v: str(int(round(v))))
                self.glyphset[name].draw(pen)
                if pen.getCommands():
                    gid = f"m{len(self.defs)}"
                    self.defs.append(f'<path id="{gid}" d="{pen.getCommands()}"/>')
            self.ids[ch] = gid
        return self.ids[ch]

    def line(self, x, y, size, runs, colours=ROLES):
        """runs: [(text, role)] from column 0. One group per role.

        In a key/value pair the leader dots are dimmed; the rules of the title and the
        section heads are not.
        """
        s = size / self.upem
        groups, col = {}, 0
        for text, role in runs:
            for ch in text:
                gid = self.ref(ch)
                if gid:
                    groups.setdefault(role, []).append(f'<use href="#{gid}" x="{col * self.adv}"/>')
                col += 1
        leaders = any(role == "key" for _, role in runs)
        inner = ""
        for role, uses in groups.items():
            dim = ' opacity=".6"' if leaders and role == "dots" else ""
            inner += f'<g fill="{colours[role]}"{dim}>{"".join(uses)}</g>'
        return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})">{inner}</g>'

    def width(self, cols, size):
        return cols * self.adv * size / self.upem


def portrait(m, frames, x, y, p):
    out = []
    for k, rows in enumerate(frames):
        lines = "".join(m.line(x, y + r * ART_LEAD, ART_SIZE, [(row, "art")], {"art": PALE})
                        for r, row in enumerate(rows) if row.strip())
        out.append(f'<g class="{p}f{k}">{lines}</g>')
    return "".join(out)


def mottos(x, y, size, p):
    """Each motto outlined under its own mask; the mask's rect is what motion animates."""
    defs, body, css = [], [], []
    for j, text in enumerate(MOTTOS):
        adv = typeset.advances(text, "voice", size)
        edges, width = [0] + [a + 1.5 for a in adv], adv[-1] + 2
        defs.append(f'<mask id="{p}m{j}"><rect class="{p}v{j}" x="{x}" y="{y - size:.1f}" '
                    f'width="{width:.2f}" height="{size * 1.5:.1f}" fill="#fff"/></mask>')
        body.append(f'<g mask="url(#{p}m{j})">{typeset.text(text, "voice", size, x, y, PALE)}</g>')
        css.append(motion.type_css(p, j, edges, width, x))
    return "".join(defs), "".join(body), "".join(css)


def build(stacked, today=None):
    grid = json.loads((DATA / "portrait.json").read_text())["grid"]
    stats = json.loads((DATA / "stats.json").read_text())
    info = [spans(l) for l in readout(stats, today or date.today())]
    frames = motion.frames(grid)
    m = Mono()
    p = "n" if stacked else "c"
    art_w = m.width(len(grid[0]), ART_SIZE)
    if not stacked:
        # readout and mottos on the left, her face on the right, looking into the page
        info_x, info_y = 24, 38
        voice_x, voice_size = 24, VOICE_SIZE
        voice_y = info_y + len(info) * INFO_LEAD + 22
        W, H = 830, round(voice_y + 30)
        art_x, art_y = 470, (H - len(grid) * ART_LEAD) / 2 + 6
    else:
        W = 420
        art_x, art_y = (W - art_w) / 2, 22
        info_size = (W - 40) / (INFO_COLS * 0.6)        # 66 columns across the narrow card
        info_lead = info_size * 16 / 11
        info_x = (W - m.width(INFO_COLS, info_size)) / 2
        info_y = art_y + len(grid) * ART_LEAD + 22
        voice_x = info_x
        voice_size = min(typeset.fit(t, "voice", VOICE_SIZE, W - 2 * info_x) for t in MOTTOS)
        voice_y = info_y + len(info) * info_lead + 26
        H = round(voice_y + 26)
    art = portrait(m, frames, art_x, art_y, p)
    size, lead = (info_size, info_lead) if stacked else (INFO_SIZE, INFO_LEAD)
    lines = "".join(m.line(info_x, info_y + r * lead, size, runs) for r, runs in enumerate(info) if runs)
    mask_defs, voice, voice_css = mottos(voice_x, voice_y, voice_size, p)
    style = motion.flip_css(p) + voice_css + motion.still_css(p)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
            f'role="img" aria-label="{ALT}"><title>nihan@bayrak</title>'
            f'<style>{style}</style>'
            f'<defs>{"".join(m.defs)}{mask_defs}'
            f'<filter id="{p}g"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="4"/>'
            f'<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .55 0"/></filter></defs>'
            f'<rect width="{W}" height="{H}" rx="10" fill="{GROUND}"/>{art}{lines}{voice}'
            f'<rect width="{W}" height="{H}" rx="10" filter="url(#{p}g)" opacity=".08" style="mix-blend-mode:screen"/>'
            f'</svg>')


def main():
    for stacked, name in ((False, "card.svg"), (True, "card-narrow.svg")):
        out = ASSETS / name
        out.write_text(build(stacked))
        print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
