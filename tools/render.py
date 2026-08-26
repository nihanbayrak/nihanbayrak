"""Renders the profile's visuals.

Era tag: 19c-engraved-broadside — ruled information cells, a table pretending to
be a poster (the Quiet Fear broadside), with the keyhole aperture as the header's
compositional device.
Palette: the Wibar draw — cornflower ground, oxblood ink, cream structure.
"""
import json
import math
import os
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

import typeset as T

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

GROUND = "#8FA8DC"   # cornflower
INK = "#8B2027"      # oxblood
CREAM = "#F2EBD8"    # cream

USER = "nihanbayrak"


# ---------------------------------------------------------------- data

def _api(path, query=None):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-render"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    if query:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query}).encode(),
            headers={**headers, "Content-Type": "application/json"},
        )
    else:
        req = urllib.request.Request(f"https://api.github.com{path}", headers=headers)

    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def collect():
    """Live numbers, with the last good snapshot as the fallback."""
    cache = DATA / "stats.json"
    try:
        user = _api(f"/users/{USER}")
        repos, page = [], 1
        while page <= 4:
            batch = _api(f"/users/{USER}/repos?per_page=100&page={page}&type=owner")
            if not batch:
                break
            repos.extend(batch)
            page += 1

        langs = {}
        for r in repos:
            if r.get("fork") or not r.get("language"):
                continue
            langs[r["language"]] = langs.get(r["language"], 0) + 1

        stats = {
            "repos": user["public_repos"],
            "followers": user["followers"],
            "since": user["created_at"][:4],
            "langs": sorted(langs.items(), key=lambda kv: -kv[1])[:5],
            "stars": sum(r.get("stargazers_count", 0) for r in repos),
        }

        gql = """{ user(login: "%s") { contributionsCollection {
              totalCommitContributions restrictedContributionsCount
              contributionCalendar { totalContributions } } } }""" % USER
        try:
            c = _api(None, gql)["data"]["user"]["contributionsCollection"]
            stats["commits"] = (c["totalCommitContributions"]
                                + c["restrictedContributionsCount"])
            stats["contributions"] = c["contributionCalendar"]["totalContributions"]
        except (urllib.error.URLError, KeyError, TypeError):
            pass

        cache.write_text(json.dumps(stats, indent=2) + "\n")
        return stats
    except (urllib.error.URLError, KeyError, TimeoutError) as e:
        print(f"  live fetch failed ({e}); using cached snapshot")
        return json.loads(cache.read_text())


# ---------------------------------------------------------------- primitives

def texture(seed=7):
    """Paper grain and a halftone dot screen. Nothing ships flat."""
    return f'''<defs>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="4" seed="{seed}"/>
      <feColorMatrix type="saturate" values="0"/>
    </filter>
    <pattern id="halftone" width="6" height="6" patternUnits="userSpaceOnUse"
             patternTransform="rotate(22)">
      <circle cx="1.5" cy="1.5" r="0.85" fill="{INK}"/>
    </pattern>
    <radialGradient id="lamp" cx="42%" cy="34%" r="72%">
      <stop offset="0%" stop-color="#FFF8E6"/>
      <stop offset="62%" stop-color="{CREAM}"/>
      <stop offset="100%" stop-color="#DCCEAE"/>
    </radialGradient>
  </defs>'''


def ground(w, h, fill=GROUND, dots=0.05):
    """Printed ground: flat colour, dot screen, grain. Never white."""
    return (
        f'<rect width="{w}" height="{h}" fill="{fill}"/>'
        f'<rect width="{w}" height="{h}" fill="url(#halftone)" opacity="{dots}"/>'
        f'<rect width="{w}" height="{h}" filter="url(#grain)" opacity="0.14"'
        f' style="mix-blend-mode:multiply"/>'
    )


def smallcaps(s, face="fact", **kw):
    return T.text(s.upper(), face, tracking=kw.pop("tracking", 0.16), **kw)


def rule(x1, y, x2, w=1, color=INK, opacity=0.55):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}"'
            f' stroke-width="{w}" opacity="{opacity}"/>')


def dingbat(x, y, r=5, color=INK, opacity=0.7):
    """A printer's lozenge. Typographic furniture, not decoration."""
    return (f'<path d="M{x} {y-r}L{x+r*0.62} {y}L{x} {y+r}L{x-r*0.62} {y}Z"'
            f' fill="{color}" opacity="{opacity}"/>')


def svg(w, h, body, seed=7):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" role="img">{texture(seed)}{body}</svg>')


# ---------------------------------------------------------------- banner

def keyhole(cx, cy, r, stem_len, top_w, bot_w):
    """One closed path: circle joined to a tapered stem. Her signature aperture."""
    dy = math.sqrt(max(r * r - top_w * top_w, 1))
    return (f"M{cx-top_w:.1f} {cy+dy:.1f} "
            f"A{r} {r} 0 1 1 {cx+top_w:.1f} {cy+dy:.1f} "
            f"L{cx+bot_w:.1f} {cy+stem_len:.1f} "
            f"L{cx-bot_w:.1f} {cy+stem_len:.1f} Z")


def banner(cfg):
    W, H = 1280, 420
    b = [ground(W, H)]

    # letterpress double border
    b.append(f'<rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none"'
             f' stroke="{INK}" stroke-width="2.5" opacity="0.75"/>')
    b.append(f'<rect x="22" y="22" width="{W-44}" height="{H-44}" fill="none"'
             f' stroke="{INK}" stroke-width="0.8" opacity="0.5"/>')

    # ---- the aperture. Cream field, one lamp behind it, the letter as an object.
    cx, cy, r = 236, 176, 92
    ap = keyhole(cx, cy, r, stem_len=182, top_w=34, bot_w=62)
    b.append(f'<clipPath id="ap"><path d="{ap}"/></clipPath>')
    b.append(f'<path d="{ap}" fill="url(#lamp)"/>')

    # engraved hatching, then the N, then the breathing lamp
    hatch = "".join(
        f'<line x1="{cx-140}" y1="{cy-180+i*7}" x2="{cx+140}" y2="{cy-158+i*7}"'
        f' stroke="{INK}" stroke-width="0.6"/>' for i in range(62))
    b.append(f'<g clip-path="url(#ap)" opacity="0.15">{hatch}</g>')
    b.append('<g clip-path="url(#ap)">'
             + T.text("N", "display", 168, cx, cy + 58, INK, anchor="middle")
             + '</g>')
    b.append(f'<g clip-path="url(#ap)"><ellipse cx="{cx-40}" cy="{cy-54}" rx="126" ry="104"'
             f' fill="#FFF8E6" opacity="0.42"><animate attributeName="opacity"'
             f' values="0.18;0.52;0.18" dur="9s" repeatCount="indefinite"/></ellipse></g>')
    b.append(f'<path d="{ap}" fill="none" stroke="{INK}" stroke-width="2.4"'
             f' stroke-linejoin="round"/>')

    # ---- the setting
    x, right = 452, W - 64
    b.append(smallcaps(cfg["eyebrow"], size=16, x=x, y=112, fill=INK, opacity=0.8))
    b.append(rule(x, 130, right))
    b.append(T.text(cfg["name"], "display", 112, x, 232, INK))
    b.append(rule(x, 258, right, opacity=0.35))
    b.append(T.text(cfg["line"], "display_med", 31, x, 296, INK, opacity=0.86))

    # ---- facts in hairline cells, each fitted to its own column
    cells = cfg["cells"]
    cw = (right - x) / len(cells)
    b.append(rule(x, 328, right, opacity=0.35))
    for i, (label, value) in enumerate(cells):
        cxx = x + i * cw
        if i:
            b.append(f'<line x1="{cxx-14}" y1="328" x2="{cxx-14}" y2="376"'
                     f' stroke="{INK}" stroke-width="0.8" opacity="0.3"/>')
        b.append(smallcaps(label, size=11, x=cxx, y=348, fill=INK, opacity=0.6,
                           tracking=0.22))
        size = T.fit(value.upper(), "fact_bold", 15, cw - 26, tracking=0.06)
        b.append(smallcaps(value, face="fact_bold", size=size, x=cxx, y=369,
                           fill=INK, tracking=0.06))
    b.append(rule(x, 378, right, opacity=0.35))

    # rotated type as a structural edge
    b.append(f'<g transform="translate({W-40} {H-56}) rotate(-90)">'
             + smallcaps("MMXXVI", size=12, x=0, y=0, fill=INK, opacity=0.55,
                         tracking=0.4) + '</g>')
    b.append(dingbat(x - 22, 121))
    return svg(W, H, "".join(b))


# ---------------------------------------------------------------- ledger

def ledger(stats, cfg):
    W, H = 1280, 208
    b = [ground(W, H, dots=0.045)]
    b.append(f'<rect x="10" y="10" width="{W-20}" height="{H-20}" fill="none"'
             f' stroke="{INK}" stroke-width="2" opacity="0.7"/>')

    b.append(smallcaps("The Ledger", face="fact_bold", size=13, x=36, y=46,
                       fill=INK, tracking=0.3))
    b.append(smallcaps(f"github.com/{USER}", size=11, x=W - 36, y=46, fill=INK,
                       opacity=0.6, tracking=0.18, anchor="end"))
    b.append(rule(36, 60, W - 36))

    figures = [
        ("Public repositories", str(stats["repos"])),
        ("Contributions, this year", str(stats.get("contributions", "\u2014"))),
        ("Followers", str(stats["followers"])),
        ("On GitHub since", stats["since"]),
        ("Principal language", stats["langs"][0][0] if stats["langs"] else "\u2014"),
    ]
    cw = (W - 72) / len(figures)
    for i, (label, value) in enumerate(figures):
        x = 36 + i * cw
        if i:
            b.append(f'<line x1="{x-16}" y1="72" x2="{x-16}" y2="158"'
                     f' stroke="{INK}" stroke-width="0.8" opacity="0.3"/>')
        b.append(smallcaps(label, size=10.5, x=x, y=92, fill=INK, opacity=0.65,
                           tracking=0.2))
        size = T.fit(value, "display", 54, cw - 30)
        b.append(T.text(value, "display", size, x, 146, INK))

    b.append(rule(36, 168, W - 36, opacity=0.35))
    b.append(smallcaps(cfg["ledger_note"], size=10.5, x=36, y=186, fill=INK,
                       opacity=0.62, tracking=0.14))
    b.append(dingbat(W - 46, 181, r=4))
    return svg(W, H, "".join(b), seed=13)


# ---------------------------------------------------------------- work cards

def card_height(item):
    """Content-driven height, so a row of cards has no dead space."""
    y = 120 + 44 * len(T.wrap(item["title"], "display", 44, 620 - 66)[:2])
    y += 14 + 27 * len(T.wrap(item["blurb"], "display_med", 21, 620 - 60)[:3])
    return int(y + 74)


def card(n, item, seed, H):
    W = 620
    b = [ground(W, H, dots=0.05)]
    b.append(f'<rect x="9" y="9" width="{W-18}" height="{H-18}" fill="none"'
             f' stroke="{INK}" stroke-width="2" opacity="0.72"/>')

    # catalogue number, reversed out of its own cell
    b.append(f'<path d="M9 9 H108 V64 H9 Z" fill="{INK}" opacity="0.92"/>')
    b.append(T.text(f"{n:02d}", "display", 42, 58, 52, CREAM, anchor="middle"))

    b.append(smallcaps(item["kind"], size=10.5, x=126, y=40, fill=INK,
                       opacity=0.7, tracking=0.24))
    b.append(smallcaps(item["status"], face="fact_bold", size=10.5, x=W - 30, y=40,
                       fill=INK, opacity=0.85, tracking=0.16, anchor="end"))
    b.append(rule(126, 64, W - 30, opacity=0.4))

    y = 120
    for line in T.wrap(item["title"], "display", 44, W - 66)[:2]:
        b.append(T.text(line, "display", 44, 30, y, INK))
        y += 44

    y += 14
    for line in T.wrap(item["blurb"], "display_med", 21, W - 60)[:3]:
        b.append(T.text(line, "display_med", 21, 30, y, INK, opacity=0.84))
        y += 27

    b.append(rule(30, H - 56, W - 30, opacity=0.35))
    stack = " \u00b7 ".join(item["stack"])
    size = T.fit(stack.upper(), "fact", 10.5, W - 84, tracking=0.18)
    b.append(smallcaps(stack, size=size, x=30, y=H - 32, fill=INK, opacity=0.72,
                       tracking=0.18))
    b.append(dingbat(W - 34, H - 37, r=4))
    return svg(W, H, "".join(b), seed=seed)


# ---------------------------------------------------------------- main

def main():
    cfg = tomllib.loads((DATA / "profile.toml").read_text())
    ASSETS.mkdir(exist_ok=True)

    print("· fetching live numbers")
    stats = collect()

    written = [("banner.svg", banner(cfg["banner"])),
               ("ledger.svg", ledger(stats, cfg["banner"]))]
    # one height for every card, so the table reads as a set
    H = max(card_height(item) for item in cfg["work"])
    for i, item in enumerate(cfg["work"], start=1):
        written.append((f"work-{i:02d}.svg", card(i, item, seed=17 + i * 3, H=H)))

    for name, content in written:
        (ASSETS / name).write_text(content)
        print(f"  {name:16} {len(content)/1024:6.1f} KB")


if __name__ == "__main__":
    main()
