"""Plays both cards in a real browser and fails if the animation misbehaves.

    /opt/anaconda3/bin/python tools/check_live.py [--webkit] [--seconds 8]

A local check, not part of the nightly job: it needs Playwright and the Mac's Chrome.
Headless, so the page is never throttled the way a hidden browser tab is.

Each card is loaded twice:
  * inline, so the page can read the SVG's DOM: on every animation frame exactly one
    portrait frame is at opacity 1, and at most one motto's mask is open;
  * as an <img>, the way GitHub shows it: a screenshot every ~250 ms, none of them with
    the face gone (ink in the portrait area below 30% of the median).
"""
import argparse
import io
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
CARDS = (("card.svg", "c", 830), ("card-narrow.svg", "n", 420))

WATCH = """([p, ms]) => new Promise(done => {
  const frames = [...Array(8)].map((_, k) => document.querySelector(`.${p}f${k}`));
  const masks = [0, 1, 2].map(j => document.querySelector(`rect.${p}v${j}`));
  const f = {}, v = {}, t0 = performance.now();
  (function tick() {
    const nf = frames.filter(e => getComputedStyle(e).opacity === '1').length;
    const nv = masks.filter(e => new DOMMatrix(getComputedStyle(e).transform).a > 0.001).length;
    f[nf] = (f[nf] || 0) + 1; v[nv] = (v[nv] || 0) + 1;
    if (performance.now() - t0 < ms) requestAnimationFrame(tick); else done([f, v]);
  })();
})"""


def check(browser, name, prefix, width, seconds, tmp):
    svg = (ROOT / "assets" / name).read_text()
    ok = True
    page = browser.new_page(viewport={"width": width + 40, "height": 900})

    inline = tmp / f"{prefix}-inline.html"
    inline.write_text(f"<!doctype html><meta charset=utf-8><body style='margin:0'>{svg}</body>")
    page.goto(inline.as_uri())
    page.wait_for_timeout(800)
    frames, masks = page.evaluate(WATCH, [prefix, seconds * 1000])
    one_frame = set(frames) == {"1"}
    one_motto = set(masks) <= {"0", "1"}
    print(f"{name}: portrait frames visible {frames}, mottos open {masks}")
    ok &= one_frame and one_motto

    img = tmp / f"{prefix}-img.html"
    (tmp / name).write_text(svg)
    img.write_text(f"<!doctype html><meta charset=utf-8><body style='margin:0'><img src='{name}' width='{width}'></body>")
    page.goto(img.as_uri())
    page.wait_for_timeout(800)
    box = page.locator("img").bounding_box()
    face = {"x": box["x"], "y": box["y"], "width": box["width"] * (0.42 if prefix == "c" else 1),
            "height": box["height"] * (1 if prefix == "c" else 0.5)}
    inks = []
    for _ in range(int(seconds * 4)):
        png = page.screenshot(clip=face)
        inks.append(ImageStat.Stat(Image.open(io.BytesIO(png)).convert("L")).stddev[0])
        page.wait_for_timeout(210)
    median = sorted(inks)[len(inks) // 2]
    blank = sum(i < 0.3 * median for i in inks)
    print(f"{name}: {len(inks)} screenshots as <img>, blank {blank}")
    ok &= blank == 0
    page.close()
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--webkit", action="store_true")
    ap.add_argument("--seconds", type=float, default=8)
    a = ap.parse_args()
    ok = True
    with sync_playwright() as p, tempfile.TemporaryDirectory() as tmp:
        browser = p.webkit.launch() if a.webkit else p.chromium.launch(channel="chrome", headless=True)
        for name, prefix, width in CARDS:
            ok &= check(browser, name, prefix, width, a.seconds, Path(tmp))
        browser.close()
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
