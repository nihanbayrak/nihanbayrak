<p align="center">
  <img src="assets/object.webp" width="700" alt="A brass and bone-enamel mechanical octopus turning slowly on its axis, green lenses for eyes, its shadow pooling to the left">
</p>

<h1 align="center">Nihan Bayrak</h1>

<p align="center">
  <b>AI specialist · Product manager · Solutions engineer</b><br>
  Berlin · <a href="https://www.linkedin.com/in/nihan-bayrak/">LinkedIn</a> · <a href="https://consciouseyes.app">consciouseyes.app</a>
</p>

<br>

I take a messy problem — a client's packaging brief, a tester's four-word bug report, a
question about taste — and turn it into an AI system that people use. Then I check
whether it works. A model that sounds right and a model that is right are two different
products, and most of my job is telling them apart.

By day I build AI systems at WIN Creating Images, a creative packaging agency in Berlin.
I care what the work looks like when it is finished. Most people in this field have no
visual vocabulary; most people with one cannot ship. I work in between.

Turkish, English, German, and enough French to be dangerous.

## Three jobs, three proofs

**Build · Roundtrip** &nbsp;<sub>AI SPECIALIST</sub><br>
A beta tester sends a screenshot and four words: *"It doesn't work."* Roundtrip reads the
screenshot to work out what they were trying to do, finds that screen in the code, and
decides whether it is a bug to fix or a call for a person to make. Bugs go to a coding
agent; the next build's release note is drafted to tell the tester theirs was fixed.
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
material never touches a third-party API.<br>
`DSPy · LangGraph · Ollama · Python`

## What I hold to

- **Untrusted text is data.** A tester's words go into Roundtrip as evidence, never as
  instructions. Text written at an AI is quarantined, not obeyed.
- **No match, no trust.** When a model reads a screenshot, the on-screen text it claims to
  see is searched for in the source. If it is not there, the reading does not drive a fix.
- **Say what you do not know.** Conscious Eyes would rather show *not found* than a guess.
- **Measure taste instead of assuming it.** I pre-registered a test of LAION's aesthetic
  predictor against my own design references. It scored 39 of 52 below 5 out of 10, and
  had no relation to how I rated them (ρ = −0.02). Write-up coming on Substack.

## More work

**[Ojin Avatar Agent](https://github.com/nihanbayrak/ojin-avatar-app)** — speech goes in, a
lip-synced talking head comes out, live.<br>
`Gemini · Ojin Flashhead · Web Audio`

**[Editorial Photo Generator](https://github.com/nihanbayrak/editorial-photo-app)** — a selfie
becomes an editorial shoot. Reference images steer style, wardrobe and pose separately.<br>
`Gemini · JavaScript`

**[Soul and Face Swap](https://github.com/nihanbayrak/soul-faceswap-generator)** — Higgsfield
Soul stages the scene, WaveSpeed puts a face in it.<br>
`Higgsfield · WaveSpeed`

## The octopus

A mesh, not a video: 37,327 triangles in 427 parts, rendered frame by frame in plain numpy
with a z-buffer, smooth normals and the PBR materials lifted from the source model, then a
shadow cast onto a floor that is not there. Drawn by [`tools/render.py`](tools/render.py).
