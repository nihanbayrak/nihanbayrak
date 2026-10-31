<p>
  <picture>
    <source media="(max-width: 600px)" srcset="assets/page-narrow.svg">
    <img src="assets/page.svg" width="100%" alt="A brass and bone enamel octopus automaton swims on Yves Klein blue, its arms waving. Care is my building language. Writing code is becoming the easy part; deciding what to build, and why, is now the bottleneck. The time AI gives back, I spend on judgment: a clear spec before the build, a measure of whether it worked after, and the honesty to rethink the whole system when the numbers say it is wrong. The models are getting better quickly, which makes taste and care more valuable, not less. Nihan Bayrak: AI specialist, product manager, solutions engineer, Berlin. Below, a year of contributions, 328 in all, as dots that a small octopus walks through and eats. Then three cards: Roundtrip, Conscious Eyes, and Brief to Concept.">
  </picture>
</p>

<a href="https://www.linkedin.com/in/nihan-bayrak/">LinkedIn</a> · <a href="https://consciouseyes.app">consciouseyes.app</a>

<details>
<summary>☞ Case file I · Roundtrip</summary>
<br>

A beta tester sends a screenshot and four words: *"It doesn't work."* Roundtrip reads the
screenshot to work out what they were trying to do, finds that screen in the code, and
decides whether it is a bug to fix or a call for a person to make. Bugs go to a coding
agent, and the next build's release note is drafted to tell the tester theirs was fixed.
Eleven tester reports from Conscious Eyes have gone through it. All eleven are fixed.

`Claude · Claude Code · App Store Connect API · Node` · private repository, demo on request

</details>

<details>
<summary>☞ Case file II · Conscious Eyes</summary>
<br>

When it does not know, it says so: an empty record reads *not found*, and a grade built
from ingredients alone says the nutrition is unknown. I wrote the spec, including what it
refuses to do, ran it through TestFlight with real testers, and submitted it to the App
Store. 627 tests stand behind it.

`React Native · TypeScript · Expo` · [consciouseyes.app](https://consciouseyes.app)

</details>

<details>
<summary>☞ Case file III · Brief to Concept</summary>
<br>

The agency's problem, solved where the agency can trust it. A raw client packaging brief
becomes a structured design brief, then a first concept image, on one machine. Client
material never touches an outside API.

`DSPy · LangGraph · Ollama · Python` · [the repository](https://github.com/nihanbayrak/Ollama_pipeline)

</details>

<br>

<details>
<summary>☞ What I hold to</summary>
<br>

- **Untrusted text is data.** A tester's words go into Roundtrip as evidence, never as
  instructions. Text written at an AI is quarantined, not obeyed.
- **No match, no trust.** When a model reads a screenshot, the text it claims to see on
  screen is searched for in the source. If it is not there, the reading does not drive a fix.
- **Measure taste instead of assuming it.** I preregistered a test of LAION's aesthetic
  predictor against my own design references. It scored 39 of 52 below 5 out of 10, and
  had no relation to how I rated them (ρ = −0.02). The full story is coming on Substack.

</details>

<details>
<summary>☞ How this page is made</summary>
<br>

One image, so there are no gaps. The octopus is a mesh, not a video: 37,327 triangles in 427
parts, bent every frame so the arms wave and the body rides each stroke, then lit in plain
numpy on the page's own Klein blue ([`tools/render.py`](tools/render.py),
[`tools/swim.py`](tools/swim.py)). Under it, the words are set like a 1922 magazine page with
Yao's kaleidoscope turning behind them, and the headline ticks letter by letter
([`tools/dance.py`](tools/dance.py)). The dots are the last year of contributions, redrawn
every night from GitHub's own calendar; the small octopus glides through them a week at a
time and eats what it finds ([`tools/commits.py`](tools/commits.py)). A README allows no
script and no hover, so all of it is CSS inside one SVG ([`tools/page.py`](tools/page.py)).

</details>
