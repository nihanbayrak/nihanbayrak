"""Three directions for the banner, so she can judge them side by side.

A GitHub README cannot be interactive — no JS, and pointer events never reach an
image. Motion is the part that does survive: CSS animation inside an SVG runs
normally when the SVG is rendered through <img>.

`phase` shifts every animation-delay negative, which freezes the piece partway
through so a still frame can show the movement.
"""
import typeset as T

W, H = 1280, 400


PAUSED = False   # set True to freeze every animation at its `phase` offset


def anim(name, dur, delay, phase, easing="cubic-bezier(.2,.7,.2,1)"):
    """A negative delay starts the animation partway in. Pausing on top of that
    freezes it there exactly, which is the only reliable way to capture a frame —
    seeking a finished animation via getAnimations() does not rewind it."""
    css = f"animation:{name} {dur}s {easing} {delay - phase:.3f}s both;"
    return css + "animation-play-state:paused;" if PAUSED else css


def keyframes():
    return """
    @keyframes rise   { from { opacity:0; transform:translateY(16px) } to { opacity:1; transform:none } }
    @keyframes fade   { from { opacity:0 } to { opacity:1 } }
    @keyframes draw   { from { stroke-dashoffset:1400 } to { stroke-dashoffset:0 } }
    @keyframes iris   { from { transform:scale(.05); opacity:0 } to { transform:scale(1); opacity:1 } }
    @keyframes bloom  { 0%,100% { opacity:.30 } 50% { opacity:.62 } }
    @keyframes sweep  { from { transform:translateX(-380px) } to { transform:translateX(1400px) } }
    @keyframes tick   { from { opacity:0; transform:translateY(9px) } to { opacity:1; transform:none } }
    """


# ------------------------------------------------------------------ A

def instrument(cfg, stats, phase=99):
    """Dark, precise, mono. Reads as an engineer who ships."""
    GROUND, INK, DIM, WARM = "#141210", "#F2EBD8", "#8C8578", "#C86B4A"
    b = [f'<style>{keyframes()}</style>',
         f'<rect width="{W}" height="{H}" fill="{GROUND}"/>']

    # measured grid, the way an instrument face is ruled
    b.append(f'<g stroke="{INK}" stroke-width="1" opacity="0.055">' + "".join(
        f'<line x1="{x}" y1="0" x2="{x}" y2="{H}"/>' for x in range(0, W, 40)) + "".join(
        f'<line x1="0" y1="{y}" x2="{W}" y2="{y}"/>' for y in range(0, H, 40)) + '</g>')

    # a slow lamp travelling across the face — the one ambient move
    b.append(f'<g style="{anim("sweep", 14, 0, phase, "linear")};animation-iteration-count:infinite">'
             f'<rect x="0" y="0" width="300" height="{H}" fill="url(#gsweep)" opacity="0.5"/></g>')
    b.append(f'<defs><linearGradient id="gsweep"><stop offset="0%" stop-color="{WARM}" stop-opacity="0"/>'
             f'<stop offset="50%" stop-color="{WARM}" stop-opacity="0.10"/>'
             f'<stop offset="100%" stop-color="{WARM}" stop-opacity="0"/></linearGradient></defs>')

    x = 84
    b.append(f'<g style="{anim("fade", .7, .05, phase)}">'
             + T.text(cfg["eyebrow"].upper(), "mono", 12.5, x, 96, WARM, tracking=0.22) + '</g>')

    b.append(f'<line x1="{x}" y1="118" x2="{W-84}" y2="118" stroke="{INK}" stroke-width="1"'
             f' opacity="0.22" stroke-dasharray="1400" style="{anim("draw", 1.5, .15, phase)}"/>')

    b.append(f'<g style="{anim("rise", .9, .3, phase)}">'
             + T.text(cfg["name"], "display", 104, x, 214, INK) + '</g>')
    b.append(f'<g style="{anim("rise", .9, .45, phase)}">'
             + T.text(cfg["line"], "display_med", 27, x, 258, DIM) + '</g>')

    # data ticks, staggered like a readout settling
    figures = [("REPOS", str(stats["repos"])), ("CONTRIB", str(stats.get("contributions", "0"))),
               ("FOLLOWERS", str(stats["followers"])), ("SINCE", stats["since"]),
               ("STACK", cfg["chiefly"].replace(" · ", "/"))]
    cw = (W - 168) / len(figures)
    for i, (label, value) in enumerate(figures):
        cx = x + i * cw
        d = 0.66 + i * 0.09
        b.append(f'<g style="{anim("tick", .6, d, phase)}">'
                 + T.text(label, "mono", 10, cx, 316, DIM, tracking=0.2)
                 + T.text(value, "mono_bold", T.fit(value, "mono_bold", 26, cw - 26), cx, 350, INK)
                 + '</g>')
        if i:
            b.append(f'<line x1="{cx-18}" y1="298" x2="{cx-18}" y2="356" stroke="{INK}"'
                     f' stroke-width="1" opacity="0.13" style="{anim("fade", .5, d, phase)}"/>')

    b.append(f'<circle cx="{W-84}" cy="90" r="4.5" fill="{WARM}"'
             f' style="{anim("bloom", 3.2, 0, phase, "ease-in-out")};animation-iteration-count:infinite"/>')
    return _wrap(b)


# ------------------------------------------------------------------ B

def editorial(cfg, stats, phase=99):
    """Warm paper, near-black, one accent. Quiet authority."""
    GROUND, INK, DIM, ACC = "#F5F1E8", "#1A1611", "#7A7266", "#8B2027"
    b = [f'<style>{keyframes()}</style>',
         f'<rect width="{W}" height="{H}" fill="{GROUND}"/>']
    b.append(f'<defs><filter id="g2"><feTurbulence type="fractalNoise" baseFrequency="0.9"'
             f' numOctaves="4" seed="5"/><feColorMatrix type="saturate" values="0"/></filter></defs>')
    b.append(f'<rect width="{W}" height="{H}" filter="url(#g2)" opacity="0.05"'
             f' style="mix-blend-mode:multiply"/>')

    x = 96
    b.append(f'<rect x="{x}" y="86" width="34" height="3" fill="{ACC}"'
             f' style="{anim("fade", .6, .05, phase)}"/>')
    b.append(f'<g style="{anim("fade", .7, .15, phase)}">'
             + T.text(cfg["eyebrow"].upper(), "fact", 12.5, x + 52, 92, DIM, tracking=0.26) + '</g>')

    b.append(f'<g style="{anim("rise", 1.0, .3, phase)}">'
             + T.text(cfg["name"], "display", 128, x, 214, INK) + '</g>')
    b.append(f'<g style="{anim("rise", 1.0, .46, phase)}">'
             + T.text(cfg["line"], "display_med", 30, x, 262, DIM) + '</g>')

    b.append(f'<line x1="{x}" y1="300" x2="{W-96}" y2="300" stroke="{INK}" stroke-width="1"'
             f' opacity="0.2" stroke-dasharray="1400" style="{anim("draw", 1.6, .55, phase)}"/>')

    items = [("Practice", cfg["cells"][0][1]), ("At", cfg["cells"][1][1]),
             ("Languages", cfg["cells"][2][1]), ("Stack", cfg["chiefly"])]
    cw = (W - 192) / len(items)
    for i, (label, value) in enumerate(items):
        cx = x + i * cw
        d = 0.72 + i * 0.08
        b.append(f'<g style="{anim("tick", .6, d, phase)}">'
                 + T.text(label.upper(), "fact", 10, cx, 330, DIM, tracking=0.24)
                 + T.text(value, "fact_bold",
                          T.fit(value.upper(), "fact_bold", 14, cw - 24, tracking=0.05),
                          cx, 352, INK, tracking=0.05) + '</g>')
    return _wrap(b)


# ------------------------------------------------------------------ C

def aperture(cfg, stats, phase=99):
    """Her keyhole, stripped of ornament. Cinematic, still hers."""
    GROUND, INK, DIM, LIGHT = "#12100E", "#F2EBD8", "#8C8578", "#FFE9C4"
    b = [f'<style>{keyframes()}</style>',
         f'<rect width="{W}" height="{H}" fill="{GROUND}"/>']
    b.append(f'<defs><radialGradient id="lamp2" cx="46%" cy="38%" r="70%">'
             f'<stop offset="0%" stop-color="#FFF6E2"/><stop offset="58%" stop-color="{LIGHT}"/>'
             f'<stop offset="100%" stop-color="#C9A97A"/></radialGradient>'
             f'<radialGradient id="halo" cx="50%" cy="50%" r="50%">'
             f'<stop offset="0%" stop-color="{LIGHT}" stop-opacity="0.30"/>'
             f'<stop offset="100%" stop-color="{LIGHT}" stop-opacity="0"/></radialGradient></defs>')

    cx, cy, r = 214, 196, 92
    b.append(f'<circle cx="{cx}" cy="{cy}" r="240" fill="url(#halo)"'
             f' style="{anim("bloom", 7, 0, phase, "ease-in-out")};animation-iteration-count:infinite"/>')
    # the iris opening
    b.append(f'<g style="{anim("iris", 1.3, .1, phase)};transform-origin:{cx}px {cy}px">'
             f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#lamp2)"/>'
             + T.text("N", "display", 132, cx, cy + 44, "#171310", anchor="middle")
             + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{LIGHT}"'
             f' stroke-width="1.5" opacity="0.45"/></g>')

    x = 386
    b.append(f'<g style="{anim("fade", .8, .55, phase)}">'
             + T.text(cfg["eyebrow"].upper(), "fact", 12.5, x, 132, DIM, tracking=0.26) + '</g>')
    b.append(f'<g style="{anim("rise", 1.0, .68, phase)}">'
             + T.text(cfg["name"], "display", 116, x, 226, INK) + '</g>')
    b.append(f'<line x1="{x}" y1="252" x2="{W-96}" y2="252" stroke="{INK}" stroke-width="1"'
             f' opacity="0.18" stroke-dasharray="1400" style="{anim("draw", 1.5, .8, phase)}"/>')
    b.append(f'<g style="{anim("rise", 1.0, .9, phase)}">'
             + T.text(cfg["line"], "display_med", 28, x, 292, DIM) + '</g>')
    b.append(f'<g style="{anim("tick", .7, 1.05, phase)}">'
             + T.text(f'{cfg["chiefly"].upper()}  ·  {cfg["cells"][2][1].upper()}',
                      "fact", 12, x, 330, DIM, tracking=0.2) + '</g>')
    return _wrap(b)


def _wrap(parts):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
            f'width="{W}" height="{H}" role="img">{"".join(parts)}</svg>')


VARIANTS = {"a-instrument": instrument, "b-editorial": editorial, "c-aperture": aperture}
