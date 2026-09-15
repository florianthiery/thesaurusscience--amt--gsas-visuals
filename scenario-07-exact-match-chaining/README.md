# Scenario 7 — exact-match chaining at scale, with per-technique calibration

## The scenario

A direct follow-up to Lasse Mempel's "Neue Infos" message: he computed real
embedding similarities (two models) and string-similarity baselines over
the Ariadne-derived mapping tables - the only files with both source and
target labels - and found that raw average similarity alone is not
informative (his strong model scores exactMatch, closeMatch *and* random
pairs all fairly high). AUC-ROC and Cohen's d against a random-pair null
baseline rescue the signal. For AMT specifically, Lasse suggested starting
conservatively: chain real, already-asserted `exactMatch` edges (A→B,
B→A/C) rather than mixed properties, and use the per-technique similarity
metrics to calibrate GSAS-style degrees separately per technique, since
each one lives on its own value range.

This scenario works through both halves of that at once, using real data
throughout - Lasse's actual script outputs, and mapping rows found directly
in the (now much larger - 44 files, ~399k rows) `thesaurusscience`
`Mappings/` folder, not invented for illustration.

**Style note**: unlike scenarios 1-6, these figures carry no baked-in title
or caption text, following the convention in
[bb-5kbc-visuals](https://github.com/Research-Squirrel-Engineers/bb-5kbc-visuals)
("general-purpose diagram assets meant to be dropped into a slide... each of
which supplies its own caption"). The per-scenario slide sentence and
explanatory paragraph for every scenario in this repository - not only this
one - live in [`TALK_NOTES.md`](TALK_NOTES.md) instead. Canvas size
(1750×1000, a 7:4 slide aspect ratio) follows the same repository's
convention.

## Two stories, kept deliberately separate

- **Story A - curated chaining** (figures 1-3): both edges in every chain
  are real, already-asserted `skos:exactMatch` SSSOM rows. GSAS's degree
  for `exactMatch` is `1.0`, unconditionally - there is no raw score to
  calibrate here, and no risk from doing so.
- **Story B - calibrated candidates** (figures 4-5): the "edge" is a raw
  similarity score from an embedding or string technique, standing in for a
  mapping that has not been curated yet. It needs a calibration step before
  it means anything as an `amt:weight` - and, as figure 4 shows, a
  raw-looking-high score does not automatically mean a strong signal once
  placed against that technique's own real distribution.

Figures 6-7 make this split, and its current limits, explicit.

## What is real and what is added

**Story A - all real.** Checked directly (2026-09, after Lasse's update):
across the ten `*_aat.sssom.tsv` files his own script uses, there are
**1,775** real `exactMatch` rows into Getty AAT, targeting **1,431**
distinct AAT concepts. **227** of those concepts are independently reached
by `exactMatch` from **two or more different source files**; **19** from
three or more. No `dai_aat`↔`inrap_pactols`↔`ads_eh_tmt2` cross-file
mapping exists anywhere in the corpus - every inferred link this scenario
draws is a genuinely new fact, not a restatement of one already in the data.
The three worked examples (`data/real_bridges.tsv`) are three of those 19
real three-way bridges:

| Concept (AAT) | DE (DAI) | FR (Pactols) | EN (ADS/Historic England) |
|---|---|---|---|
| bridges (built works) | Brücke | pont | BRIDGE |
| aqueducts | Aquädukt | aqueduc | AQUEDUCT |
| barracks | Kaserne | caserne | BARRACKS |

Three independent national recording traditions, each mapping their own
term to the same real Getty AAT concept, never referencing each other
directly.

**Story B - real pair, real per-technique scores, one added interpretation
layer.** `data/example_calibration.tsv` uses one real `closeMatch` row from
`Mappings/inrap_pactols_sujets_aat.sssom.tsv` - "petit appareil" (a French
masonry term) / "brickwork (masonry)" - with its real similarity scores
from Lasse's own `Scripts/outputs/mapping_similarities__*.csv`: `0.805`
(e5-large-instruct), `0.051` (m2v-bge-m3, essentially a miss), `0.242`
(Levenshtein string similarity). All three real, copied unchanged. Added:

- `random_pair_mean` / `exactmatch_mean` for e5 - **not** copied from
  Lasse's CSVs (his script computes these in-memory and does not write them
  to a file). `exactmatch_mean` is read straight from
  `mapping_similarities__e5-large-instruct.csv`; `random_pair_mean` is
  **resampled here** from his own cached embeddings
  (`label_embeddings__e5-large-instruct__full.pkl`), using the same method
  (2,000 random label pairs) but not the same random draw, so it is a real,
  independently-computed number from his real embeddings, not a bit-exact
  reproduction of one specific run of his script. Stated in the data file's
  header.
- `calibrated_band` - **this scenario's own placement**, not a GSAS output.
  No GSAS model (Minimal, 4-Level, 7-Star or Perceptions) calibrates
  embedding or string techniques at all; GSAS's degrees are defined only
  for `exactMatch`/`closeMatch`/`relatedMatch` as *categories*, not for
  arbitrary continuous inputs from an external technique. What this
  scenario does is place the raw score against that one technique's own
  real reference points and borrow GSAS's 4-Level *vocabulary*
  (dubious/low/medium/high) to name the result, because it is more
  informative than a bare float. `petit appareil`/`brickwork` lands as
  **"dubious"** - genuinely: at `0.805`, its raw e5 score is *below* e5's
  own real random-pair mean (`~0.828`) on this corpus, because e5's cosine
  space is compressed upward for every pair regardless of relatedness (the
  exact anisotropy problem Lasse's script was written to catch). This is
  not a clean "calibration confirms high confidence" example - it is a
  real, slightly humbling one, kept deliberately rather than swapped for a
  tidier pair.

## What GSAS contributes here

In Story A: nothing beyond the fixed `exactMatch = 1.0` degree already
established in scenario 1/2/3. In Story B: its 4-Level *vocabulary*, reused
as a naming scheme for a placement GSAS itself does not compute - a
genuine gap, not papered over (see `img/scenario-07-calibration-pipeline`
and the GSAS-coverage discussion already raised in scenario 6 for
`broadMatch`/`narrowMatch` - this scenario adds embedding/string
*techniques* as a second, distinct kind of thing GSAS does not calibrate).

## What AMT contributes here

- **`amt:InverseAxiom` + `amt:RoleChainAxiom` on pure `exactMatch`**
  (figures 1-2): the conservative starting point Lasse proposed. Because
  `skos:exactMatch` is already the one SKOS mapping property that *is*
  declared transitive (SKOS Reference, checked in scenario 6), this chain
  is not asking AMT to do something SKOS forbids, the way scenario 6's
  mixed-property chains do - it is asking AMT to actually *compute* a
  composition SKOS already sanctions, at a scale (1,775 real rows, 227 real
  bridging opportunities) no one is going to do by hand.
- **The same graded machinery, ready for calibrated candidate weights**:
  Story B's calibrated band is not yet fed into an axiom in this scenario
  (see figure 7's scope boundary) - but it is expressed in the same
  `amt:weight`-shaped terms as Story A precisely so that it *could* be,
  once a real calibration methodology (not this scenario's placeholder
  banding) exists.

## Figures

1. **`img/scenario-07-bridge-hub.svg`/`.png`** - the flagship real bridge:
   three real concepts (DE/FR/EN), one real shared AAT hub, solid asserted
   `exactMatch` edges in, dashed inferred edges directly between each pair
   of source concepts.
2. **`img/scenario-07-axiom-representation.svg`/`.png`** - the same
   inference (Brücke ~ pont) as an axiom pipeline: two asserted quads →
   `amt:InverseAxiom` / `amt:RoleChainAxiom` → one inferred quad, `w = 1.0`.
3. **`img/scenario-07-pattern-repeats.svg`/`.png`** - the same schema, two
   more real triples (aqueduct, barracks) side by side.
4. **`img/scenario-07-calibration-pipeline.svg`/`.png`** - Story B as a
   pipeline: real SSSOM row → raw technique score (with its technique's own
   real reference points as plain text, not a plotted curve) → calibration
   step → GSAS-vocabulary band.
5. **`img/scenario-07-multi-provenance.svg`/`.png`** - the same pair, three
   parallel technique-specific edges (e5, m2v, Levenshtein), each carrying
   its own real raw value - a graph, not a comparison chart.
6. **`img/scenario-07-safe-vs-candidate.svg`/`.png`** - Story A vs. Story B
   side by side: what each one is, and what it costs.
7. **`img/scenario-07-scope-boundary.svg`/`.png`** - what this scenario
   models (chaining, per-technique banding) against what Lasse's message
   explicitly leaves for later (candidate generation across the whole AAT,
   recall checking, LLM re-ranking with context).

## Sketch: how this could actually be implemented

1. **Story A at real scale**: convert the ten `*_aat.sssom.tsv` files (or
   all 44) to RDF quads (the `sssom-js` step Lasse mentions he still owes),
   assert `ex:IA_exactSymmetric` (scenario 1) and one
   `amt:RoleChainAxiom` (`antecedents = (exactMatch, exactMatch)`), and run
   `amt-engine` once over the whole graph. Every one of the 227 real
   bridging concepts would fire the same axiom automatically - no
   per-concept modelling needed, matching Lasse's own framing.
2. **Story B, done properly**: replace this scenario's illustrative banding
   with a real per-technique calibration fitted the way GSAS's own
   Perceptions model is fitted - empirical reference points (random-pair,
   closeMatch, exactMatch means, computed the way Lasse's script already
   does) turned into a continuous function per technique, published
   alongside the technique the way GSAS publishes its own curves.
3. **Join them**: feed Story B's calibrated weights into the *same*
   `amt:RoleChainAxiom` machinery as Story A, so a candidate mapping and a
   curated one can sit in the same reasoning graph with honestly different
   confidence - this is the "Ähnlichkeit über Bande" (similarity via a
   detour) question Lasse poses and flags as still needing to be tested.
4. **Everything past that** - candidate generation over the full AAT,
   recall evaluation against held-out real mappings, LLM re-ranking with
   parent/sibling/scope-note context - is explicitly out of scope for this
   scenario (figure 7) and for AMT specifically, per Lasse's own message.

None of this is implemented here - `py/build_figures.py` only draws the
seven figures above from the real bridge triples and the one real
calibration example; it does not call `amt-engine` or recompute any
embeddings.
