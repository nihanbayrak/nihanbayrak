"""Renders the profile's one visual.

The page used to be six generated pieces — a banner, a live ledger and six work
cards, all drawn from the GitHub API and redrawn nightly. Nihan cut them on
27 Aug: one object, and the words do the rest. What is left is the octopus.

Nothing here reads the API any more, so the render is deterministic and the
nightly schedule was dropped with it. The Action still runs on a push that
touches `tools/` or `data/`, which is what catches a broken render.

GitHub renders README images inside <img>, which blocks webfont loading, so type
still has to arrive as outlines — see typeset.py. That constraint outlives
everything else on this page.
"""
from pathlib import Path

import engrave
import model3d
import typeset as T

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

GROUND = "#F5F1E8"   # warm off-white paper
INK = "#1A1611"      # near-black, warm
DIM = "#7A7266"      # secondary
ACC = "#8B2027"      # oxblood, used once per piece


# ---------------------------------------------------------------- primitives

KEYFRAMES = """
  @keyframes rise { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
  @keyframes fade { from { opacity:0 } to { opacity:1 } }
  @keyframes draw { from { stroke-dashoffset:1400 } to { stroke-dashoffset:0 } }
  @keyframes tick { from { opacity:0; transform:translateY(9px) } to { opacity:1; transform:none } }
"""

EASE = "cubic-bezier(.2,.7,.2,1)"


def anim(name, dur, delay):
    return f'style="animation:{name} {dur}s {EASE} {delay:.2f}s both"'


def texture(seed=7, style="", defs=""):
    """Paper grain. Nothing ships flat."""
    return (f'<style>{KEYFRAMES}{style}</style>'
            f'<defs><filter id="grain{seed}" x="0" y="0" width="100%" height="100%">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" seed="{seed}"/>'
            f'<feColorMatrix type="saturate" values="0"/></filter>{defs}</defs>')


def ground(w, h, seed=7):
    return (f'<rect width="{w}" height="{h}" fill="{GROUND}"/>'
            f'<rect width="{w}" height="{h}" filter="url(#grain{seed})" opacity="0.05"'
            f' style="mix-blend-mode:multiply"/>')


def smallcaps(s, face="fact", **kw):
    return T.text(s.upper(), face, tracking=kw.pop("tracking", 0.22), **kw)


def rule(x1, y, x2, delay=0.0, color=INK, opacity=0.2, dur=1.5):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" stroke-width="1"'
            f' opacity="{opacity}" stroke-dasharray="1400"'
            f' style="animation:draw {dur}s {EASE} {delay:.2f}s both"/>')


def svg(w, h, body, seed=7, style="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">{texture(seed, style, defs)}{body}</svg>')


# ---------------------------------------------------------------- the object

def object_plate():
    """The octopus, turning. The only image on the page, and the only thing that loops."""
    W, H = 440, 500
    x, right = 30, 410

    v, f, accent = model3d.load_obj(DATA / "nautilia-octopus.obj")
    # the box carries the aspect of the whole revolution, arms at full spread --
    # square it off and the object floats in a quarter of the plate
    plate = engrave.Engraver(v, f, accent, (48, 78, 344, 313))

    b = [ground(W, H, seed=5)]
    b.append(f'<g {anim("fade", .6, .05)}>'
             + smallcaps("The Object", size=10, x=x, y=44, fill=DIM, tracking=0.24)
             + smallcaps("Nautilia", size=10, x=right, y=44, fill=DIM,
                         tracking=0.18, anchor="end") + '</g>')
    b.append(rule(x, 60, right, delay=.15, dur=1.1))

    b.append(f'<g {anim("fade", 1.2, .4)}>' + plate.plate() + '</g>')

    b.append(rule(x, 410, right, delay=.6, opacity=0.14, dur=1.0))
    b.append(f'<g {anim("rise", .7, .72)}>'
             + T.text("An octopus, turning", "display", 27, x, 441, INK) + '</g>')
    for i, line in enumerate(("Rasterised from the mesh, then cut as line work",
                              f"{engrave.FRAMES} plates · one turn every five seconds")):
        size = T.fit(line.upper(), "fact", 9.5, right - x, tracking=0.16)
        b.append(f'<g {anim("tick", .55, .82 + i * .06)}>'
                 + smallcaps(line, size=size, x=x, y=461 + i * 15, fill=DIM,
                             tracking=0.16) + '</g>')
    return svg(W, H, "".join(b), seed=5, style=engrave.STYLE)


# ---------------------------------------------------------------- main

def main():
    ASSETS.mkdir(exist_ok=True)
    content = object_plate()
    (ASSETS / "object.svg").write_text(content)
    print(f"  object.svg {len(content)/1024:9.1f} KB")


if __name__ == "__main__":
    main()
