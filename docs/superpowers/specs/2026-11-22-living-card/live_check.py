"""Play a mockup fragment in real Chrome (headless, so never throttled) and look for blinks.

Two independent measures over the same run:
  * every animation frame (rAF): how many portrait frames are at opacity 1, and how many
    typed lines are showing at once
  * screenshots every ~250 ms: ink in the portrait area (a blank face is just the ground)
"""
import io, sys
from pathlib import Path
from PIL import Image, ImageStat
from playwright.sync_api import sync_playwright

frag, prefix, seconds = Path(sys.argv[1]), sys.argv[2], float(sys.argv[3])
tmp = frag.with_suffix(".standalone.html")
tmp.write_text(f"<!doctype html><meta charset=utf-8><body style='margin:0;background:#111;width:900px'>{frag.read_text()}</body>")

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome", headless=True)
    pg = b.new_page(viewport={"width": 900, "height": 700})
    pg.goto(tmp.as_uri())
    pg.wait_for_timeout(1500)
    x, y, w, h = pg.evaluate(f"() => {{ const r = document.querySelector('.{prefix}f0').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; }}")
    pg.evaluate(f"""() => {{
        window.__f = {{}}; window.__v = {{}};
        const g = [...Array(8)].map((_, k) => document.querySelector('.{prefix}f' + k));
        const v = [0, 1, 2].map(j => document.querySelector('rect.{prefix}v' + j));
        const t0 = performance.now();
        (function tick() {{
            const nf = g.filter(e => getComputedStyle(e).opacity === '1').length;
            const nv = v.filter(e => new DOMMatrix(getComputedStyle(e).transform).a > 0.001).length;
            window.__f[nf] = (window.__f[nf] || 0) + 1; window.__v[nv] = (window.__v[nv] || 0) + 1;
            if (performance.now() - t0 < {seconds * 1000}) requestAnimationFrame(tick);
        }})(); }}""")
    inks = []
    for _ in range(int(seconds * 4)):
        png = pg.screenshot(clip={"x": x, "y": y, "width": w, "height": h})
        inks.append(ImageStat.Stat(Image.open(io.BytesIO(png)).convert("L")).stddev[0])
        pg.wait_for_timeout(210)
    pg.wait_for_timeout(500)
    frames, lines = pg.evaluate("[window.__f, window.__v]")
    b.close()

med = sorted(inks)[len(inks) // 2]
print(f"rAF samples, portrait frames visible: {frames}")
print(f"rAF samples, typed lines visible:     {lines}")
print(f"screenshots: {len(inks)}, ink median {med:.1f}, min {min(inks):.1f}, blank {sum(i < 0.3 * med for i in inks)}")
