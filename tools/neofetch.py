"""The profile card: a portrait in signs beside a neofetch readout of her.

Left, data/portrait.txt (tools/portrait.py). Right, key and value pairs joined by
leader dots, the way a terminal system-info tool prints a machine, with the
GitHub numbers from data/stats.json (tools/stats.py) at the foot. Uptime counts
from the day the GitHub account opened.

All type is JetBrains Mono, as outlines: a README image cannot load a font, and a
terminal card that falls back to Times is not a terminal card. Each glyph is drawn
once and placed by column. Light and dark versions, and a stacked cut for phones.

    python tools/neofetch.py     # writes assets/card-{light,dark}{,-narrow}.svg
"""
import json
from datetime import date
from pathlib import Path

import typeset

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

FACE, SIZE, LEAD = "mono", 15, 19
INFO_COLS = 60
PAD_X, PAD_Y = 22, 20
RULE = "─"

PALETTES = {
    "light": dict(bg="#f6f8fa", text="#24292f", key="#953800", value="#0a3069",
                  dots="#afb8c1", add="#1a7f37", sub="#cf222e", art="#24292f"),
    "dark": dict(bg="#161b22", text="#c9d1d9", key="#ffa657", value="#a5d6ff",
                 dots="#484f58", add="#3fb950", sub="#f85149", art="#c9d1d9"),
}


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
    """Lines of (text, role) spans. A pair is ('pair', key, value)."""
    up = uptime(date.fromisoformat(stats["created"]), today)
    net = stats["added"] - stats["deleted"]
    return [
        ("title", "nihan@bayrak"),
        ("pair", "OS", "macOS 26, iOS 27"),
        ("pair", "Uptime", up),
        ("pair", "Host", "WIN Creating Images, Berlin"),
        ("pair", "Kernel", "Harness engineer"),
        ("pair", "IDE", "Claude Code, Xcode"),
        ("pair", "Shell", "zsh"),
        ("blank",),
        ("pair", "Languages.Programming", "Python, TypeScript, JavaScript"),
        ("pair", "Languages.Computer", "HTML, CSS, SVG, JSON, YAML"),
        ("blank",),
        ("pair", "Hobbies.Software", "3D rendering, generative video"),
        ("pair", "Hobbies.Real", "Fashion, design, puzzles"),
        ("blank",),
        ("section", "Building"),
        ("pair", "Agents", "Roundtrip"),
        ("pair", "Product", "Conscious Eyes, iOS"),
        ("blank",),
        ("section", "Contact"),
        ("pair", "LinkedIn", "nihan-bayrak"),
        ("pair", "Website", "consciouseyes.app"),
        ("blank",),
        ("section", "GitHub Stats"),
        ("pairs", ("Repos", f'{stats["repos"]} {{Contributed: {stats["contributed"]}}}'),
                  ("Stars", f'{stats["stars"]:,}')),
        ("pairs", ("Commits", f'{stats["commits"]:,}'), ("Followers", f'{stats["followers"]:,}')),
        ("loc", f"{net:,}", f'{stats["added"]:,}', f'{stats["deleted"]:,}'),
    ]


def spans(line, width):
    """A readout line as [(text, role)], exactly `width` columns or less."""
    kind = line[0]
    if kind == "title":
        return [(line[1], "text"), (" ", "text"), (RULE * (width - len(line[1]) - 1), "dots")]
    if kind == "section":
        head = f"{RULE} {line[1]} "
        return [(RULE + " ", "dots"), (line[1], "text"), (" " + RULE * (width - len(head)), "dots")]
    if kind == "blank":
        return [(".", "dots")]
    if kind == "pair":
        return _pair(line[1], line[2], width)
    if kind == "pairs":
        (k1, v1), (k2, v2) = line[1], line[2]
        right = 22
        left = _pair(k1, v1, width - right - 3)
        return left + [(" | ", "dots")] + _pair(k2, v2, right, lead="")
    if kind == "loc":
        net, add, sub = line[1:]
        out = _key(". ", "Lines of Code on GitHub") + [(": ", "dots")]
        tail = [(net, "value"), (" ( ", "dots"), (f"{add}++", "add"), (", ", "dots"),
                (f"{sub}--", "sub"), (" )", "dots")]
        used = sum(len(t) for t, _ in out + tail)
        return out + [("." * max(width - used - 1, 1) + " ", "dots")] + tail
    raise ValueError(kind)


def _key(lead, key):
    """'Languages.Programming' keeps its dot in the text colour, as a terminal would."""
    out = [(lead, "dots")] if lead else []
    parts = key.split(".")
    for i, p in enumerate(parts):
        out.append((p, "key"))
        if i < len(parts) - 1:
            out.append((".", "text"))
    return out


def _pair(key, value, width, lead=". "):
    head = _key(lead, key) + [(": ", "dots")]
    used = sum(len(t) for t, _ in head) + len(value) + 1
    return head + [("." * max(width - used, 1) + " ", "dots"), (value, "value")]


# ---------------------------------------------------------------- drawing

class Mono:
    """Outlined monospace: each glyph drawn once, placed by column."""

    def __init__(self):
        self.tt, self.glyphset, _, self.upem = typeset._load(FACE)
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

    def line(self, x, y, runs, colours):
        """runs: [(text, role)] from column 0. One group per line, one per colour."""
        s = SIZE / self.upem
        by_colour, col = {}, 0
        for text, role in runs:
            for ch in text:
                gid = self.ref(ch)
                if gid:
                    by_colour.setdefault(colours[role], []).append(f'<use xlink:href="#{gid}" x="{col * self.adv}"/>')
                col += 1
        inner = "".join(f'<g fill="{c}">{"".join(u)}</g>' for c, u in by_colour.items())
        return f'<g transform="translate({x:.1f} {y:.1f}) scale({s:.5f} {-s:.5f})">{inner}</g>'

    def cols(self, n):
        return n * self.adv * SIZE / self.upem


def build(theme, stacked, today=None):
    pal = PALETTES[theme]
    art = (DATA / "portrait.txt").read_text().rstrip("\n").split("\n")
    stats = json.loads((DATA / "stats.json").read_text())
    info = [spans(l, INFO_COLS) for l in readout(stats, today or date.today())]
    art_cols = max(len(l) for l in art)
    m = Mono()
    body = []
    if not stacked:
        info_x = PAD_X + m.cols(art_cols + 3)
        rows = max(len(art), len(info))
        art_top = PAD_Y + (rows - len(art)) * LEAD / 2
        info_top = PAD_Y + (rows - len(info)) * LEAD / 2
        for r, l in enumerate(art):
            body.append(m.line(PAD_X, art_top + r * LEAD + SIZE * .8, [(l, "art")], pal))
        for r, runs in enumerate(info):
            body.append(m.line(info_x, info_top + r * LEAD + SIZE * .8, runs, pal))
        W = round(info_x + m.cols(INFO_COLS) + PAD_X)
        H = round(PAD_Y * 2 + rows * LEAD)
    else:
        W = round(PAD_X * 2 + m.cols(INFO_COLS))
        art_x = (W - m.cols(art_cols)) / 2
        for r, l in enumerate(art):
            body.append(m.line(art_x, PAD_Y + r * LEAD + SIZE * .8, [(l, "art")], pal))
        top = PAD_Y + (len(art) + 1) * LEAD
        for r, runs in enumerate(info):
            body.append(m.line(PAD_X, top + r * LEAD + SIZE * .8, runs, pal))
        H = round(top + len(info) * LEAD + PAD_Y)
    alt = ("Nihan Bayrak, as a terminal readout: a portrait drawn in signs beside her details. "
           "Harness engineer at WIN Creating Images, Berlin. "
           f'{stats["repos"]} public repos, {stats["commits"]:,} commits, '
           f'{stats["added"] - stats["deleted"]:,} lines of code on GitHub.')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{alt}">'
            f'<title>nihan@bayrak</title><defs>{"".join(m.defs)}</defs>'
            f'<rect width="{W}" height="{H}" rx="14" fill="{pal["bg"]}"/>{"".join(body)}</svg>')


def main():
    for theme in PALETTES:
        for stacked in (False, True):
            out = ASSETS / (f"card-{theme}" + ("-narrow" if stacked else "") + ".svg")
            out.write_text(build(theme, stacked))
            print(f"  {out.name}  {out.stat().st_size / 1024:.0f} KB")


if __name__ == "__main__":
    main()
