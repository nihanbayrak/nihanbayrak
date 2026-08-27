# Nihan Bayrak

**Berlin · AI Specialist · WIN Creating Images**

<table>
<tr>
<td width="38%" valign="top">
<img src="assets/object.webp" width="100%" alt="A brass and bone-enamel mechanical octopus turning on its axis, its lenses glowing green">
</td>
<td width="62%" valign="top">

I build AI systems at a creative packaging agency in Berlin, and I care what they
look like when they are finished. Most people in this field have no visual
vocabulary. Most people with a visual vocabulary cannot ship. The interesting
work is in between.

Turkish, English, German, and enough French to be dangerous.

The thing on the left is a real object turning — thirty-seven thousand triangles,
lit and rendered here rather than filmed anywhere.

Python · TypeScript. Agents, generative image, evals. Most of the work sits in
private repositories; what follows is what can be shown.

</td>
</tr>
</table>

## Selected work

**[Brief to Concept, Locally](https://github.com/nihanbayrak/Ollama_pipeline)** — a raw client
packaging brief becomes a design brief, then a first concept image. Nothing leaves the machine.<br>
`DSPy · LangGraph · Ollama · Python`

**[Editorial Photo Generator](https://github.com/nihanbayrak/editorial-photo-app)** — a selfie
becomes an editorial shoot. Reference images drive style, wardrobe and pose separately.<br>
`Gemini · JavaScript`

**[Conscious](https://github.com/nihanbayrak/conscious-legal)** — a scanner for food and
cosmetics that never invents an ingredient. Two hundred and sixty-nine tests stand behind that.<br>
`React Native · TypeScript · Expo`

**[Ojin Avatar Agent](https://github.com/nihanbayrak/ojin-avatar-app)** — speech goes in, a
lip-synced talking head comes out, and the whole pipeline runs live.<br>
`Gemini · Ojin Flashhead · Web Audio`

**[Soul and Face Swap](https://github.com/nihanbayrak/soul-faceswap-generator)** — Higgsfield
Soul stages the scene. WaveSpeed puts a face in it. One page, two models.<br>
`Higgsfield · WaveSpeed · HTML`

**[This page](https://github.com/nihanbayrak/nihanbayrak)** — a 3D mesh rasterised and then
cut as hatch lines, turning in a document that allows no JavaScript.<br>
`Python · numpy · fontTools · Actions`

## About this page

The octopus is a mesh, not a video of one. `nautilia-octopus.obj` carries 37,327
triangles across 427 separate parts — brass bands sitting on bone-enamel arms — and
every frame of the turn is rendered here: z-buffer, smooth normals, a
metallic-roughness shading model, and a cast shadow projected onto the floor. The
material values are not guesses. They are the PBR figures lifted out of the source
GLB and kept in [`data/materials.json`](data/materials.json), which is why the brass
is that brass and the lenses actually emit.

Shading is deferred — the triangle loop writes only depth, normal and material, and
the lighting runs once per frame over the whole buffer. Back faces are culled by
their vertex normals rather than by winding order, because this model's winding is
consistent but inverted, and about 8% of its triangles disagree with it outright.

It is a WebP because a shaded surface is a continuous gradient and there is no honest
way to write forty-eight frames of one as vector paths. The background is transparent,
so it sits on either GitHub theme, and the shadow rides in the alpha channel.

Drawn by [`tools/render.py`](tools/render.py). Nothing here is a badge service.

## Elsewhere

[LinkedIn](https://www.linkedin.com/in/nihan-bayrak/) · Berlin, CET
