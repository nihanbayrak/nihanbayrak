"""Three cards, one per job: the object you choose.

From her interactive references (moodboard §1d): a row of physical things as the
menu, and the interface on the object. Each card is a printed label on the same
paper as the sheet, and each is its own link, because a click is the one thing a
README lets a visitor do. The verb is printed on the card beside a manicule, and
the manicule steps forward in the same held clockwork steps as the headline, so
the only motion here says what will happen.

The proof behind each card sits under it in a folded case file (<details> in the
README), which is the other thing a README lets a visitor do: open something.

Run by hand with dance.py; same dependencies, same reasons.
"""
import typeset
from dance import ASSETS, DISPLAY, FACT, FACT_BOLD, READING, THEMES, TRACK, Sheet

CARDS = [
    dict(n="I", act="BUILD", role="AI SPECIALIST", title="Roundtrip",
         deck="A tester's screenshot goes in. A located, triaged and fixed case comes out.",
         stack="CLAUDE · CLAUDE CODE · NODE", status="PRIVATE REPOSITORY",
         verb="ASK FOR A DEMO"),
    dict(n="II", act="SHIP", role="PRODUCT MANAGER", title="Conscious Eyes",
         deck="A food and cosmetics scanner that never invents an ingredient. "
              "627 tests stand behind that.",
         stack="REACT NATIVE · EXPO · TYPESCRIPT", status="SUBMITTED TO THE APP STORE",
         verb="VISIT THE SITE"),
    dict(n="III", act="TRANSLATE", role="SOLUTIONS ENGINEER", title="Brief to Concept",
         deck="A raw client packaging brief becomes a design brief, then a first concept "
              "image, on one machine.",
         stack="DSPY · LANGGRAPH · OLLAMA", status="PUBLIC REPOSITORY",
         verb="OPEN THE CODE"),
]

LAYOUTS = {
    "wide": dict(W=800, pad=56, inset=40, numeral=96, title=44, deck=14.5, lead=23, fact=11, fact_lead=17),
    "narrow": dict(W=380, pad=30, inset=18, numeral=64, title=36, deck=14, lead=22, fact=10.5, fact_lead=16),
}

STYLE = """
.m { transform-box: fill-box; animation: point 4s steps(1, end) infinite; }
@keyframes point {
  0%, 12%, 100% { transform: none; }
  3%  { transform: translateX(4px); }
  6%  { transform: translateX(9px); }
  9%  { transform: translateX(4px); }
}
@media (prefers-reduced-motion: reduce) { .m { animation: none; } }
"""


def manicule(sh, x, y, size, delay):
    """The pointing hand, set in Cormorant, on its own clock."""
    uses, width = sh.glyphs("☞", DISPLAY, size, x, y)
    sh.marks.append(f'<g class="m" fill="{sh.structure}" style="animation-delay:{delay:.2f}s">'
                    f'{"".join(u for u, _ in uses)}</g>')
    return width


def frame(sh, W, H, inset):
    sh.marks.append(f'<rect x="{inset}" y="{inset}" width="{W - 2 * inset}" height="{H - 2 * inset}" '
                    f'fill="none" stroke="{sh.ink}" stroke-width=".75"/>')


def build(card, L, delay, ink, structure):
    sh = Sheet(ink, structure)
    W, pad, f, fl = L["W"], L["pad"], L["fact"], L["fact_lead"]

    if W >= 600:
        # Numeral | label, title, deck | ruled facts and the verb
        nx, rule_x = pad + 8, pad + 118
        cx, right_x = rule_x + 26, W - pad - 190
        cw = right_x - 24 - cx
        y = pad + 14 + fl
        w = sh.text(card["act"], FACT_BOLD, f, cx, y, sh.structure, TRACK)
        sh.text(card["role"], FACT, f, cx + w + f, y, sh.ink, TRACK)
        y += L["title"] * 0.95
        sh.text(card["title"], DISPLAY, L["title"], cx, y, sh.ink)
        y += L["lead"] * 1.4
        for line in typeset.wrap(card["deck"], READING, L["deck"], cw):
            sh.text(line, READING, L["deck"], cx, y, sh.ink)
            y += L["lead"]
        H = max(y - L["lead"] + pad + 18, 168)

        num_w = typeset.measure(card["n"], DISPLAY, L["numeral"])
        sh.text(card["n"], DISPLAY, L["numeral"], rule_x - 22 - num_w, pad + 18 + L["numeral"] * 0.66,
                sh.structure)
        sh.rule(rule_x, pad + 6, rule_x, H - pad - 6, sh.structure, 1)

        fx, fx1 = right_x, W - pad - 8
        y = pad + 14
        sh.rule(fx, y, fx1, y, sh.ink)
        for text in (card["stack"], card["status"]):
            for line in typeset.wrap(text, FACT, f - .5, fx1 - fx, TRACK):
                y += fl
                sh.text(line, FACT, f - .5, fx, y - 4, sh.ink, TRACK)
            y += 7
            sh.rule(fx, y, fx1, y, sh.ink)
        vy = H - pad - 14
        w = sh.text(card["verb"], FACT_BOLD, f, fx, vy, sh.structure, TRACK)
        manicule(sh, fx + w + 8, vy + 7, 34, delay)
    else:
        # Narrow: numeral and label on one line, then title, deck, facts, verb
        x0, x1 = pad + 8, W - pad - 8
        y = pad + 6 + L["numeral"] * 0.66
        nw = sh.text(card["n"], DISPLAY, L["numeral"], x0, y, sh.structure)
        ly = y - L["numeral"] * 0.66 + fl
        sh.text(card["act"], FACT_BOLD, f, x0 + nw + 16, ly, sh.structure, TRACK)
        sh.text(card["role"], FACT, f, x0 + nw + 16, ly + fl, sh.ink, TRACK)
        y += 14 + L["title"] * 0.8
        sh.text(card["title"], DISPLAY, L["title"], x0, y, sh.ink)
        y += L["lead"] * 1.15
        for line in typeset.wrap(card["deck"], READING, L["deck"], x1 - x0):
            sh.text(line, READING, L["deck"], x0, y, sh.ink)
            y += L["lead"]
        y += 2
        sh.rule(x0, y - 12, x1, y - 12, sh.ink)
        for line in typeset.wrap(f'{card["stack"]} · {card["status"]}', FACT, f - .5, x1 - x0, TRACK):
            y += fl - 4
            sh.text(line, FACT, f - .5, x0, y, sh.ink, TRACK)
        y += 30
        w = sh.text(card["verb"], FACT_BOLD, f, x0, y, sh.structure, TRACK)
        manicule(sh, x0 + w + 8, y + 6, 28, delay)
        H = y + pad + 14

    frame(sh, W, H, L["inset"])
    alt = (f'{card["n"]}. {card["act"].title()}, {card["role"].lower()}. {card["title"]}. '
           f'{card["deck"]} {card["verb"].capitalize()}.')
    return sh.svg(W, H, alt, title=card["title"], style=STYLE)
