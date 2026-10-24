<p align="center">
  <img src="assets/object.webp" width="700" alt="A brass and bone enamel mechanical octopus turning slowly on its axis, green lenses for eyes, its shadow pooling to the left">
</p>

<h1 align="center">Nihan Bayrak</h1>

<p align="center">
  <b>AI specialist · Product manager · Solutions engineer</b><br>
  Berlin · <a href="https://www.linkedin.com/in/nihan-bayrak/">LinkedIn</a> · <a href="https://consciouseyes.app">consciouseyes.app</a>
</p>

<br>

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/care-dark.svg">
    <img src="assets/care-light.svg" width="620" alt="Care is my building language.">
  </picture>
</p>

<br>

AI made building fast. Most people spend that speed on building more. I spend it on
attention.

The hours AI gives back, I put into planning: what we are making, why, and how we will
know it worked. Then I track it, measure it and improve it. When the numbers say the
system is wrong, I take the whole thing apart and rethink it, even when that is the
uncomfortable thing to do. Especially then.

You can see it in the details. A seasonal tip that names the months instead of calling
late October peak season. A palm oil warning that appears once, not twice. A highlight
that holds still while the octopus turns, because a moving one strobes.

I trust my taste, and I test it. Most people in this field have no visual vocabulary;
most people with one cannot ship. I work in between.

By day I build AI systems at WIN Creating Images, a creative packaging agency in Berlin.
Turkish, English, German, and enough French to be dangerous.

## Three jobs, three proofs

**Build · Roundtrip** &nbsp;<sub>AI SPECIALIST</sub><br>
A beta tester sends a screenshot and four words: *"It doesn't work."* Roundtrip reads the
screenshot to work out what they were trying to do, finds that screen in the code, and
decides whether it is a bug to fix or a call for a person to make. Bugs go to a coding
agent, and the next build's release note is drafted to tell the tester theirs was fixed.
Eleven tester reports from Conscious Eyes have gone through it. All eleven are fixed.<br>
`Claude · Claude Code · App Store Connect API · Node` &nbsp;<sub>private repository</sub>

**Ship · [Conscious Eyes](https://consciouseyes.app)** &nbsp;<sub>PRODUCT MANAGER</sub><br>
A food and cosmetics scanner for iPhone that never invents an ingredient. When it does not
know, it says so: an empty record reads *not found*, and a grade built from ingredients
alone says the nutrition is unknown. I wrote the spec, including what it refuses to do,
ran it through TestFlight with real testers, and submitted it to the App Store.
627 tests stand behind it.<br>
`React Native · TypeScript · Expo`

**Translate · [Brief to Concept, Locally](https://github.com/nihanbayrak/Ollama_pipeline)** &nbsp;<sub>SOLUTIONS ENGINEER</sub><br>
The agency's problem, solved where the agency can trust it. A raw client packaging brief
becomes a structured design brief, then a first concept image, on one machine. Client
material never touches an outside API.<br>
`DSPy · LangGraph · Ollama · Python`

## What I hold to

- **Untrusted text is data.** A tester's words go into Roundtrip as evidence, never as
  instructions. Text written at an AI is quarantined, not obeyed.
- **No match, no trust.** When a model reads a screenshot, the text it claims to see on
  screen is searched for in the source. If it is not there, the reading does not drive a fix.
- **Measure taste instead of assuming it.** I preregistered a test of LAION's aesthetic
  predictor against my own design references. It scored 39 of 52 below 5 out of 10, and
  had no relation to how I rated them (ρ = −0.02). The full story is coming on Substack.

## This page

The octopus is a mesh, not a video: 37,327 triangles in 427 parts, rendered frame by frame
in plain numpy with a depth buffer, smooth normals and the PBR materials lifted from the
source model, then a shadow cast onto a floor that is not there. The line above dances
because it is not text. A README allows no script and no hover, so every letter is its own
outline with its own timing. Drawn by [`tools/render.py`](tools/render.py) and
[`tools/dance.py`](tools/dance.py).
