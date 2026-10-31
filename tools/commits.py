"""The year, eaten: the contribution graph with the octopus walking through it.

Every day of the last year is a halftone dot, sized by GitHub's own quartile for
that day. The octopus, drawn small after the automaton above it, walks the year
one week at a time at an even glide, bobbing as it goes: its head rides along the top, its
tentacles hang down over that week's column, and every dot in the column is
eaten. Eaten dots grow back in the order they went, and the walk starts again.

Real data, typeset as data: the count in the caption is GitHub's own total, and
the dots are its own levels. Nothing here is a badge service. The nightly
workflow fetches the calendar with its GITHUB_TOKEN; run by hand, it asks the
gh CLI, which reads its own credentials, so no token passes through this file.

    python tools/commits.py           # fetch and keep data/contributions.json
    python tools/page.py              # draw it into the page

Needs fonttools and uharfbuzz for the outlined captions (see typeset.py).
"""
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

from dance import ASSETS, FACT, FACT_BOLD, THEMES, TRACK, Sheet

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "contributions.json"
USER = "nihanbayrak"

QUERY = """query { user(login: "%s") { contributionsCollection { contributionCalendar {
  totalContributions weeks { contributionDays { date contributionCount contributionLevel } } } } } }""" % USER

LEVELS = {"NONE": 0, "FIRST_QUARTILE": 1, "SECOND_QUARTILE": 2,
          "THIRD_QUARTILE": 3, "FOURTH_QUARTILE": 4}
RADIUS = [1.2, 2.3, 3.2, 4.1, 5.0]       # halftone: the dot grows with the day

LAYOUTS = {
    "wide": dict(W=800, weeks=53),
    "narrow": dict(W=380, weeks=26),     # the last six months; a year would be specks
}
PITCH = 13                               # one day, one cell
GRID_TOP = 74                            # room above for the octopus's head
STEP = 0.22                              # seconds per week of walking
EMPTY = 0.35                             # share of the loop an eaten dot stays gone


# ---------------------------------------------------------------- data

def fetch():
    """The calendar from GitHub. Returns None if it cannot be had."""
    token = os.environ.get("GITHUB_TOKEN")
    try:
        if token:
            req = urllib.request.Request(
                "https://api.github.com/graphql",
                data=json.dumps({"query": QUERY}).encode(),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json",
                         "User-Agent": "profile-commits"})
            with urllib.request.urlopen(req, timeout=30) as r:
                body = json.load(r)
        else:
            out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"],
                                 capture_output=True, text=True, timeout=60, check=True)
            body = json.loads(out.stdout)
        cal = body["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    except (urllib.error.URLError, subprocess.SubprocessError, OSError, KeyError,
            TypeError, json.JSONDecodeError) as e:
        print(f"  could not fetch the calendar ({type(e).__name__}); keeping the last one")
        return None
    return {
        "total": cal["totalContributions"],
        "weeks": [[(d["date"], d["contributionCount"], LEVELS[d["contributionLevel"]])
                   for d in w["contributionDays"]] for w in cal["weeks"]],
    }


# ---------------------------------------------------------------- the octopus

def octopus(ink, lens, reach):
    """The automaton, small. Origin at the centre of the collar; tentacles hang `reach` px."""
    head = (f'<g fill="none" stroke="{ink}" stroke-width="1.3" stroke-linecap="round">'
            f'<path d="M-16 0 C-17 -27 17 -27 16 0 Z"/>'                 # the dome
            f'<path d="M0 -20 C-9 -16 -10 -5 -9 0 M0 -20 C9 -16 10 -5 9 0 M0 -20 V0"/>'  # cage
            f'<path d="M-16 -7 H16"/>'                                    # the band
            f'<path d="M0 -20 V-26"/><circle cx="0" cy="-27.5" r="1.6"/>'  # finial
            f'<path d="M-15 0 H15 V3.5 H-15 Z"/>'                         # collar
            f'</g>'
            f'<circle cx="-6.5" cy="-3.2" r="3" fill="{lens}"/>'           # the lenses carry
            f'<circle cx="6.5" cy="-3.2" r="3" fill="{lens}"/>')            # the one accent

    def tentacles(sway):
        paths = []
        for i, x0 in enumerate((-12, -7, -2.5, 2.5, 7, 12)):
            side = -1 if x0 < 0 else 1
            x1 = x0 * 1.55 + sway * (1 if i % 2 else -1)
            curl = side * 4
            paths.append(f'M{x0} 4 C{x0 + sway} {reach * .35:.0f} {x1 - sway} {reach * .7:.0f} '
                         f'{x1} {reach - 4} q{curl} 3 {curl * .4:.1f} 6')
        return " ".join(paths)

    # The arms morph between two sways and back, smoothly: one path, its shape animated.
    a, b = tentacles(3), tentacles(-3)
    arms = (f'<path d="{a}" fill="none" stroke="{ink}" stroke-width="1.2" stroke-linecap="round">'
            f'<animate attributeName="d" values="{a};{b};{a}" dur="1.3s" repeatCount="indefinite" '
            f'calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/></path>')
    return f'<g class="ob">{head}{arms}</g>'


# ---------------------------------------------------------------- drawing

def build(cal, layout, ink, structure):
    W, n = layout["W"], layout["weeks"]
    weeks = cal["weeks"][-n:]
    left = (W - n * PITCH) / 2
    grid_bottom = GRID_TOP + 7 * PITCH
    reach = grid_bottom - GRID_TOP + 10

    walk = (n + 2) * STEP                       # enter, a step per week, leave
    T = walk / (0.94 - EMPTY)                   # long enough that every eaten dot is back by the next pass
    pct = lambda t: f"{100 * t / T:.3f}%"

    sh = Sheet(ink, structure)
    style = [f"""
.ob {{ animation: bob 1.3s ease-in-out infinite alternate; }}
@keyframes bob {{ from {{ transform: translateY(-2px); }} to {{ transform: translateY(3px); }} }}
.d {{ transform-box: fill-box; transform-origin: center;
      animation: eat {T:.2f}s ease-out infinite both; }}
@keyframes eat {{
  0%, {100 * EMPTY:.1f}% {{ transform: scale(0); }}
  {100 * EMPTY + 8:.1f}%, 100% {{ transform: none; }}
}}"""]

    # The walk: off the left edge, a week at a time at an even glide, off the right edge.
    frames = [f"0% {{ transform: translate({left - 40:.1f}px, {GRID_TOP - 12}px); }}"]
    for c in range(n):
        cx = left + c * PITCH + PITCH / 2
        frames.append(f"{pct((c + 1) * STEP)} {{ transform: translate({cx:.1f}px, {GRID_TOP - 12}px); }}")
    frames.append(f"{pct((n + 1) * STEP)}, 100% {{ transform: translate({W + 40}px, {GRID_TOP - 12}px); }}")
    style.append(f"""
.o {{ animation: walk {T:.2f}s linear infinite; }}
@keyframes walk {{ {" ".join(frames)} }}
@media (prefers-reduced-motion: reduce) {{
  .o, .d, .ob {{ animation: none; }}
  .o {{ transform: translate({left + (n - 1) * PITCH + PITCH / 2:.1f}px, {GRID_TOP - 12}px); }}   /* parked on today */
}}""")

    # Every day gets a socket; days with work get a dot that can be eaten.
    sockets, dots = [], []
    for c, week in enumerate(weeks):
        eaten_at = (c + 1) * STEP
        for d, count, level in week:
            wd = date.fromisoformat(d).isoweekday() % 7          # Sunday on top, like GitHub
            x = left + c * PITCH + PITCH / 2
            y = GRID_TOP + wd * PITCH + PITCH / 2
            sockets.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{RADIUS[0]}"/>')
            if level:
                fill = structure if level == 4 else ink
                dots.append(f'<circle class="d" cx="{x:.1f}" cy="{y:.1f}" r="{RADIUS[level]}" fill="{fill}" '
                            f'style="animation-delay:{eaten_at - T:.2f}s"/>')
    sh.marks.append(f'<g fill="{ink}" opacity=".28">{"".join(sockets)}</g>')
    sh.marks.append("".join(dots))
    sh.marks.append(f'<g class="o">{octopus(ink, structure, reach)}</g>')

    # Months under the grid, at the first week each one starts in.
    f = 10
    ly = grid_bottom + 20
    last_x = -99
    for c, week in enumerate(weeks):
        first = date.fromisoformat(week[0][0])
        if (first.day <= 7 or c == 0) and c * PITCH - last_x > 34:
            label = first.strftime("%b").upper()
            sh.text(label, FACT, f, left + c * PITCH, ly, ink, TRACK)
            last_x = c * PITCH
    total = f'{cal["total"]:,}'
    cy = ly + 22
    w = sh.text(total, FACT_BOLD, f + 1, left, cy, structure, TRACK)
    sh.text("CONTRIBUTIONS IN THE LAST YEAR, EATEN AND GROWN BACK", FACT, f, left + w + 7, cy, ink, TRACK)
    H = cy + 24

    alt = (f'Contribution graph: {cal["total"]} contributions in the last year. A small brass '
           f'octopus walks across it week by week and eats each day\'s dot; the dots grow back.')
    return sh.svg(W, H, alt, title="The year, eaten", style="".join(style))


def main():
    """Fetch the calendar and keep it; page.py draws it into the page."""
    cal = fetch()
    if cal:
        DATA.write_text(json.dumps(cal, separators=(",", ":")) + "\n")
        print(f"  contributions.json  {cal['total']} in the last year")


if __name__ == "__main__":
    main()
