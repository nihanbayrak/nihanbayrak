"""Renders the profile's visuals.

Direction B — editorial. Warm paper, near-black type, one oxblood mark, and
motion that stages the reading order: the rule draws, the name rises, the facts
tick in. Nihan chose this over the engraved-broadside and aperture directions.

A README cannot be interactive — no JS, and pointer events never reach an image.
Motion is what survives, so every piece animates on load.
"""
import json
import math
import os
import tomllib
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

import sort3d as S3
import typeset as T

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
DATA = ROOT / "data"

GROUND = "#F5F1E8"   # warm off-white paper
INK = "#1A1611"      # near-black, warm
DIM = "#7A7266"      # secondary
ACC = "#8B2027"      # oxblood, used once per piece

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

        # Current practice, not archaeology: forks, archived repos and anything
        # untouched for two years say nothing about what she writes now.
        cutoff = (datetime.now(timezone.utc) - timedelta(days=730)).isoformat()
        langs = {}
        for r in repos:
            if r.get("fork") or r.get("archived") or not r.get("language"):
                continue
            if r.get("pushed_at", "") < cutoff:
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


# ---------------------------------------------------------------- banner

def banner(cfg):
    W, H = 1280, 400
    x, right = 96, 1184
    b = [ground(W, H)]

    # the one oxblood mark
    b.append(f'<rect x="{x}" y="86" width="34" height="3" fill="{ACC}" {anim("fade", .6, .05)}/>')
    b.append(f'<g {anim("fade", .7, .15)}>'
             + smallcaps(cfg["eyebrow"], size=12.5, x=x + 52, y=92, fill=DIM, tracking=0.26) + '</g>')

    b.append(f'<g {anim("rise", 1.0, .3)}>'
             + T.text(cfg["name"], "display", 128, x, 214, INK) + '</g>')
    b.append(f'<g {anim("rise", 1.0, .46)}>'
             + T.text(cfg["line"], "display_med", 30, x, 262, DIM) + '</g>')

    b.append(rule(x, 300, right, delay=.55))

    items = [(cfg["cells"][0][0], cfg["cells"][0][1]), (cfg["cells"][1][0], cfg["cells"][1][1]),
             (cfg["cells"][2][0], cfg["cells"][2][1]), ("Stack", cfg["chiefly"])]
    cw = (right - x) / len(items)
    for i, (label, value) in enumerate(items):
        cx = x + i * cw
        size = T.fit(value.upper(), "fact_bold", 14, cw - 26, tracking=0.05)
        b.append(f'<g {anim("tick", .6, .72 + i * .08)}>'
                 + smallcaps(label, size=10, x=cx, y=330, fill=DIM, tracking=0.24)
                 + smallcaps(value, face="fact_bold", size=size, x=cx, y=352, fill=INK,
                             tracking=0.05) + '</g>')
    return svg(W, H, "".join(b))


# ---------------------------------------------------------------- ledger

def ledger(stats, cfg):
    W, H = 1280, 190
    x, right = 96, 1184
    b = [ground(W, H, seed=13)]

    b.append(f'<g {anim("fade", .6, .05)}>'
             + smallcaps("The Ledger", face="fact_bold", size=11.5, x=x, y=44, fill=ACC,
                         tracking=0.3)
             + smallcaps(f"github.com/{USER}", size=10.5, x=right, y=44, fill=DIM,
                         tracking=0.18, anchor="end") + '</g>')
    b.append(rule(x, 60, right, delay=.15))

    figures = [
        ("Public repositories", str(stats["repos"])),
        ("Contributions, this year", str(stats.get("contributions", "\u2014"))),
        ("Followers", str(stats["followers"])),
        ("On GitHub since", stats["since"]),
        ("Chiefly", cfg["chiefly"]),
    ]
    cw = (right - x) / len(figures)
    for i, (label, value) in enumerate(figures):
        cx = x + i * cw
        size = T.fit(value, "display", 52, cw - 28)
        b.append(f'<g {anim("tick", .6, .3 + i * .09)}>'
                 + smallcaps(label, size=10, x=cx, y=94, fill=DIM, tracking=0.24)
                 + T.text(value, "display", size, cx, 142, INK) + '</g>')

    b.append(rule(x, 158, right, delay=.8, opacity=0.14))
    b.append(f'<g {anim("fade", .6, .95)}>'
             + smallcaps(cfg["ledger_note"], size=10, x=x, y=176, fill=DIM, tracking=0.16)
             + '</g>')
    return svg(W, H, "".join(b), seed=13)


# ---------------------------------------------------------------- work cards

def card_height(item):
    y = 118 + 44 * len(T.wrap(item["title"], "display", 44, 620 - 60)[:2])
    y += 12 + 27 * len(T.wrap(item["blurb"], "display_med", 21, 620 - 60)[:3])
    return int(y + 70)


def card(n, item, seed, H):
    W = 620
    x, right = 30, 590
    b = [ground(W, H, seed=seed)]
    d = 0.04 + (n - 1) * 0.045         # the row of cards deals itself out

    b.append(f'<g {anim("fade", .6, d)}>'
             + T.text(f"{n:02d}", "display", 30, x, 46, ACC)
             + smallcaps(item["kind"], size=10, x=x + 44, y=42, fill=DIM, tracking=0.24)
             + smallcaps(item["status"], face="fact_bold", size=10, x=right, y=42, fill=DIM,
                         tracking=0.16, anchor="end") + '</g>')
    b.append(rule(x, 62, right, delay=d + .1, opacity=0.16, dur=1.2))

    y = 118
    for i, line in enumerate(T.wrap(item["title"], "display", 44, W - 60)[:2]):
        b.append(f'<g {anim("rise", .7, d + .18 + i * .05)}>'
                 + T.text(line, "display", 44, x, y, INK) + '</g>')
        y += 44

    y += 12
    for i, line in enumerate(T.wrap(item["blurb"], "display_med", 21, W - 60)[:3]):
        b.append(f'<g {anim("rise", .7, d + .30 + i * .04)}>'
                 + T.text(line, "display_med", 21, x, y, DIM) + '</g>')
        y += 27

    b.append(rule(x, H - 52, right, delay=d + .40, opacity=0.14, dur=1.0))
    stack = " \u00b7 ".join(item["stack"])
    size = T.fit(stack.upper(), "fact", 10, W - 60, tracking=0.2)
    b.append(f'<g {anim("tick", .55, d + .48)}>'
             + smallcaps(stack, size=size, x=x, y=H - 28, fill=DIM, tracking=0.2) + '</g>')
    return svg(W, H, "".join(b), seed=seed)


# ---------------------------------------------------------------- the object

def object_plate():
    """A sort, turning. The only 3D on the page, and the only thing that loops."""
    W, H = 440, 520
    x, right = 30, 410
    mesh = S3.build()
    cx, cy, s = S3.place(mesh, (54, 86, W - 108, 344))

    b = [ground(W, H, seed=5)]
    b.append(f'<g {anim("fade", .6, .05)}>'
             + smallcaps("The Object", size=10, x=x, y=44, fill=DIM, tracking=0.24)
             + smallcaps("Cormorant Infant", size=10, x=right, y=44, fill=DIM,
                         tracking=0.18, anchor="end") + '</g>')
    b.append(rule(x, 60, right, delay=.15, dur=1.1))

    b.append(f'<g {anim("fade", 1.1, .45)}>' + S3.plate(cx, cy, s, mesh) + '</g>')

    b.append(rule(x, 452, right, delay=.55, opacity=0.14, dur=1.0))
    b.append(f'<g {anim("rise", .7, .68)}>'
             + T.text("A piece of foundry type", "display", 27, x, 483, INK) + '</g>')
    caption = "Cast in reverse, as type is \u00b7 48 plates, one turn every four seconds"
    size = T.fit(caption.upper(), "fact", 9.5, right - x, tracking=0.16)
    b.append(f'<g {anim("tick", .55, .80)}>'
             + smallcaps(caption, size=size, x=x, y=503, fill=DIM, tracking=0.16) + '</g>')
    return svg(W, H, "".join(b), seed=5, style=S3.STYLE, defs=S3.defs())


# ---------------------------------------------------------------- main

def main():
    cfg = tomllib.loads((DATA / "profile.toml").read_text())
    ASSETS.mkdir(exist_ok=True)

    print("· fetching live numbers")
    stats = collect()

    written = [("banner.svg", banner(cfg["banner"])),
               ("object.svg", object_plate()),
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
