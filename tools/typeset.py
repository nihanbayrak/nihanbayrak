"""Text to SVG outlines.

GitHub renders README images inside <img>, which blocks webfont loading. Any
typeface we care about therefore has to arrive as path data. Harfbuzz does the
shaping so kerning and ligatures survive the trip.
"""
from functools import lru_cache
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

FONTS = Path(__file__).parent / "fonts"

FACES = {
    "mono": ("JetBrainsMono.ttf", {"wght": 400}),
    "mono_bold": ("JetBrainsMono.ttf", {"wght": 700}),
    "mono_light": ("JetBrainsMono.ttf", {"wght": 200}),
    # Fraunces italic Light at the optical size it is set at — the typed mottos
    "voice": ("Fraunces-Italic.ttf", {"wght": 300, "opsz": 19}),
}


@lru_cache(maxsize=None)
def _load(face):
    filename, axes = FACES[face]
    path = FONTS / filename
    tt = instancer.instantiateVariableFont(TTFont(path), axes, inplace=False)

    # Harfbuzz needs the instanced bytes, not the original file.
    from io import BytesIO
    buf = BytesIO()
    tt.save(buf)
    data = buf.getvalue()

    hbface = hb.Face(data)
    hbfont = hb.Font(hbface)
    upem = hbface.upem
    hbfont.scale = (upem, upem)
    return tt, tt.getGlyphSet(), hbfont, upem


def shape(text, face, tracking=0.0):
    """Return (list of (glyph_name, x_offset_in_units), advance_width_in_units)."""
    _, _, hbfont, upem = _load(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})

    tt, _, _, _ = _load(face)
    order = tt.getGlyphOrder()
    track_units = tracking * upem

    placed, cursor = [], 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        placed.append((order[info.codepoint], cursor + pos.x_offset))
        cursor += pos.x_advance + track_units
    return placed, cursor - (track_units if placed else 0)


def measure(text, face, size, tracking=0.0):
    _, width = shape(text, face, tracking)
    _, _, _, upem = _load(face)
    return width * size / upem


def advances(text, face, size):
    """Right edge in px of each character of `text`, one entry per character.

    A character inside a ligature or cluster shares the right edge of the glyph that
    covers it, so a reveal stepped to these edges never shows part of a glyph.
    """
    _, _, hbfont, upem = _load(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hbfont, buf, {"kern": True, "liga": True})

    ends, cursor = {}, 0.0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        cursor += pos.x_advance
        ends[info.cluster] = cursor
    starts = sorted(ends)
    out, k = [], 0
    for i in range(len(text)):
        while k + 1 < len(starts) and starts[k + 1] <= i:
            k += 1
        out.append(ends[starts[k]] * size / upem)
    return out


def path_data(text, face, tracking=0.0):
    """Combined outline for a text run, in font units, baseline at y=0, y up."""
    _, glyphset, _, _ = _load(face)
    placed, _ = shape(text, face, tracking)

    parts = []
    for name, x in placed:
        pen = SVGPathPen(glyphset, ntos=lambda v: str(int(round(v))))
        glyphset[name].draw(pen)
        d = pen.getCommands()
        if not d:
            continue
        parts.append(f'<path transform="translate({x:.0f} 0)" d="{d}"/>')
    return "".join(parts)


def text(content, face, size, x, y, fill, tracking=0.0, anchor="start", opacity=None):
    """An SVG <g> of outlines, positioned like you'd position real text."""
    _, _, _, upem = _load(face)
    scale = size / upem
    width = measure(content, face, size, tracking)

    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width

    op = f' opacity="{opacity}"' if opacity is not None else ""
    inner = path_data(content, face, tracking)
    return (
        f'<g transform="translate({x:.2f} {y:.2f}) scale({scale:.6f} {-scale:.6f})" '
        f'fill="{fill}"{op}>{inner}</g>'
    )


def wrap(content, face, size, max_width, tracking=0.0):
    """Greedy line breaking against real measured widths."""
    lines, cur = [], ""
    for word in content.split():
        trial = f"{cur} {word}".strip()
        if cur and measure(trial, face, size, tracking) > max_width:
            lines.append(cur)
            cur = word
        else:
            cur = trial
    if cur:
        lines.append(cur)
    return lines


def fit(content, face, size, max_width, tracking=0.0, floor=7.0):
    """Largest size at or below `size` that keeps the run inside max_width."""
    while size > floor and measure(content, face, size, tracking) > max_width:
        size -= 0.5
    return size
