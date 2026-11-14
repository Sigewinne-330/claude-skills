# Sidspark writing style

Distilled from the physics posts on sidspark.site (pole/vibration isolation, Bertrand's theorem,
shell theorem, Playing Pool with Pi series, reduced mass). Refresh it by skimming one or two recent
posts (`reference/wordpress.md`, section 2) if the blog may have drifted.

### Voice
- Body in **English**, first person ("I"), conversational but precise. Dry humour is welcome
  ("it has been living in my head ever since", "a caveat I refuse to bury").
- Honest about limits. The author is an IB student who self-studies physics; do not claim
  mastery he does not have (e.g. Lagrangian mechanics is new to him: say "I am still fairly new to
  Lagrangians, so I'll go slowly"). Only state things he actually did (experiments, checks, where he met
  a problem). If unsure whether he did something, ask or phrase it neutrally.
- Explain *why* each step is allowed, not just what it is ("Why one degree of freedom is allowed.").
- Short paragraphs; one idea each. Don't cram every detail of the brief into one sentence:
  pick what serves the argument and drop the rest.

### Structure
- Title: punchy, often "Topic: Hook" or a series form
  ("How Differential Equations Describe the Physics World – Why …", "Playing Pool with Pi – Part 3 – …").
- Intro with no heading: a concrete hook (problem, folk claim, story), the question, and what the post
  will show. Usually 3–6 paragraphs and the first figure.
- Numbered H2 sections "1. …", "2. …" (a "0." section is fine for definitions). H3 "5.1 …" for sub-cases.
- A limit/sanity-check section is a signature move ("Breaking the answer on purpose": M→∞, M→0,
  frictionless case, dimension check).
- If the problem asks "can method X do it?", answer it explicitly in its own section.
- Final section unnumbered: "Closing: …" or "Closing, with …" — what the trick needs / where it fails,
  plus one surprising connection to something bigger. No summary of every section.
- Typical length 3,000–4,500 words; 10–15 numbered display equations; 2–5 figures.

### Formatting conventions
- Display maths: own centred paragraph, `$$ … \tag{n} $$`; refer to it as "(n)" in text.
  Un-numbered displays for intermediate steps are fine.
- Inline maths `$…$`. Vectors `\mathbf r`. Fractions in inline maths: `\tfrac`.
- Bold lead-ins start paragraphs that make one specific point: `**Heavy track, $M\to\infty$.** …`
- Key statements (Claim / The rule / Theorem 1) go in a quote block with a bold label.
- Proofs end with `\qquad\blacksquare` inside the last display.
- Tables only for numeric results. Write them in post.txt as a raw block (no blank lines inside):
  `<!-- wp:table -->` / `<figure class="wp-block-table"><table><thead>…</thead><tbody>…</tbody></table></figure>` / `<!-- /wp:table -->`.
- Figures: "Figure n." caption in bold followed by one or two sentences; numbered in order of
  appearance.

### Sources and other people's material
- Paraphrase problems from textbooks, summer schools or the web in your own words and credit the
  source in prose ("the problem from HKU summer school, in my own words"). Do not paste their text
  or reproduce someone else's worked solution; derive it yourself.
- Never use someone else's figures; redraw everything as SVG.

### Taxonomy
- Category for physics/maths posts: **Physics Club** (id 13 at time of writing; confirm by name).
  Other categories exist (Creative Writing Club, Feelings) for non-physics writing.
- Tags: 4–7 topical tags in Title Case (e.g. Classical Mechanics, Reduced Mass, Simple Harmonic
  Motion, Lagrangian Mechanics). Reuse existing tags by exact name before creating new ones.
- Excerpt: one or two sentences, no maths.

