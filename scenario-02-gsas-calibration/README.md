# Scenario 2 — GSAS as a calibration layer between embedding similarity and AMT input

## The scenario

The CAA JCM abstract's core idea is to use sentence embeddings (SBERT) as a
richer similarity signal than string matching, and to use GSAS to "translate
heterogeneous similarity signals into graded, qualitatively meaningful
mapping recommendations". This scenario works through one concrete instance
of that: a candidate mapping between two real, currently-unlinked concepts
from `thesaurusscience`, run through each of GSAS's three input-taking
models (Minimal, 7-Star, Perceptions - the fourth, "4-Level", is a bin-mean
derivative of the 7-Star numbers and is not run separately here).

## The example - and what is and is not real about it

`data/example_concepts.tsv`: `aat:300010439` "clay" and `aat:300010669`
"terracotta" are two real concepts, each already `skos:exactMatch`-mapped to
its own DARIAH-materials concept in `thesaurusscience` - but **not** mapped
to each other anywhere in the corpus. That is exactly the situation the CAA
JCM abstract's envisioned recommender addresses: an embedding similarity
search over concept labels would surface "clay"/"terracotta" as a mapping
*candidate*, which still needs a principled degree before AMT (or a human
curator) can act on it.

**No real SBERT similarity value exists for this pair.** Per Lasse Mempel's
message in the chat this repository is drawn from, embeddings have not been
computed for `thesaurusscience` yet, and this repository's build environment
has no network access to compute one. The cosine value used throughout this
scenario's figures, **0.78, is an illustrative placeholder** - stated as
such in `data/example_concepts.tsv`'s own header, exactly parallel to how
`amt:weight` was handled in scenario 1. Treat every number derived from it
(the calibrated degrees, the bar heights) as "what the calibration would
output *if* the similarity were 0.78", not as a finding about clay and
terracotta.

`data/gsas_reference_values.tsv` **is** real: every degree, star level,
phrase, median and threshold in it is copied unchanged from the actual GSAS
repository's own computed CSV outputs (`skos_minimal_degrees.csv`,
`skos_7star_degrees.csv`, `skos_perceptions_stats.csv`,
`skos_4level_degrees.csv`), not recomputed or
approximated. `py/build_figures.py` also copies the exact formulas from the
real scripts (`skos/skos.py`'s `degree_of_connection`, `skos_perceptions/
skos_perceptions.py`'s `logistic`), with their actual default parameters:
`k=2.0` (7-Star), `k=0.348`/`r0=9.73` (Perceptions logistic interpolation),
`EXACT_MIN=0.9382`/`CLOSE_MIN=0.4948` (Perceptions' own classification
thresholds - notice these are almost identical to the 7-Star model's
closeMatch/relatedMatch degrees; the two were evidently calibrated against
each other in GSAS itself).

## A modelling caveat worth being explicit about

GSAS's 7-Star model formally defines `d(s)` for **seven discrete star
levels**, `s ∈ {1, ..., 7}` - it is a lookup table with a smooth
mathematical shape behind it, not a continuous function GSAS itself
evaluates at arbitrary input. The Perceptions model *is* explicitly designed
with a continuous interpolation for extending beyond its 17 known phrases
(the paper says so directly), but the 7-Star model is not documented that
way.

This scenario is honest about that distinction:

- **`img/scenario-02-calibration-curves.*`** treats both the 7-Star and
  Perceptions formulas as continuous, purely to make them visually
  comparable on one shared `[0, 1]` axis. **This is a simplification
  introduced for this figure, not a GSAS claim** - said in the figure's own
  title and repeated here.
- **`img/scenario-02-pipeline.*`** and **`img/scenario-02-model-comparison.*`**
  use GSAS the way it is actually meant to be used: the placeholder cosine
  is first binned to the *nearest* of the 7 discrete star levels (star 6
  here), and the degree that travels onward to AMT is the real, tabulated
  `skos_7star_degrees.csv` value for that level (`0.9381`), not the
  continuous interpolation's slightly different value (`0.9135`).

## What GSAS contributes here

- A **principled, already-computed degree** for whichever discrete level
  (star, phrase, or minimal predicate) the similarity score is binned to -
  no need to invent a number or hand-pick a confidence.
- **Three genuinely different calibration philosophies**, visible side by
  side in `scenario-02-model-comparison`: Minimal and 7-Star agree here
  (`0.938`, because they share the same closeMatch/exactMatch reference
  points), but Perceptions - grounded in empirical human judgement rather
  than a designed curve - lands noticeably lower (`0.8`, "Very Good
  Chance"). That is the paper's stated "Comparability" benefit, made
  concrete with one worked example instead of an abstract claim.
- A **materialised RDF sub-property** to attach the degree to
  (`skosplus:degreeOfConnection` on the chosen `skos:*Match` property, or on
  one of the `skosplus:relatedMatch*`/`skosplus:perceptions_*` sub-properties
  for finer levels) - this is what AMT actually reads.

## What AMT contributes here

Nothing new beyond scenario 1, and that is the point of this scenario:
AMT's role is unchanged - it still just reads a graded RDF assertion
(`amt:weight` in `[0, 1]`) and reasons over it (role chains, inverses,
subsumption). What scenario 2 changes is *where that weight comes from*:
in scenario 1 it was a stand-in placeholder; here it is a GSAS-calibrated
degree, traceable back to a specific model, a specific star/phrase, and a
specific real reference value. AMT does not care which - it is exactly the
"conservative extension" design GSAS's own paper describes (Section 4.3):
SKOS mapping properties reused unchanged, degrees added as annotations,
nothing about AMT's reasoning has to change to consume them.

## Figures

- **`img/scenario-02-calibration-curves.svg`/`.png`** - all three models on
  one `[0, 1]` input axis: the 7-Star curve (with its 7 real discrete
  points marked), the Perceptions logistic curve (with all 17 real median
  points marked), and the Minimal model as three flat reference levels
  (it does not take a continuous input at all). A vertical marker shows
  where the placeholder cosine (0.78) sits.
- **`img/scenario-02-pipeline.svg`/`.png`** - the concrete worked example:
  clay/terracotta → placeholder cosine → GSAS 7-Star calibration (binned to
  the nearest discrete star) → `skos:closeMatch`, `degree_of_connection =
  0.9381` → an AMT-ready graded RDF assertion.
- **`img/scenario-02-model-comparison.svg`/`.png`** - the same placeholder
  input run through all three models' *discrete* binning, side by side:
  Minimal and 7-Star agree (`0.938`), Perceptions differs (`0.8`).
- **`img/scenario-02-four-level.svg`/`.png`** - the fourth GSAS model, not
  shown elsewhere in this repository: dubious/low/medium/high, each the real
  mean of its 7-Star bin (`0.164`/`0.647`/`0.852`/`0.969`) - a coarser,
  more communicable view of the same curve as figure 1.
- **`img/scenario-02-model-selection-guide.svg`/`.png`** - which of the four
  models fits which situation, paraphrased from the GSAS paper's own stated
  rationale for each (Sections 2.3-2.6): the four are complementary entry
  points into the same scale, not a hierarchy from worst to best.

## Figures at a glance vs. the fourth model

The 4-Level model is the one GSAS model not otherwise exercised by figures
1-3 (which focus on Minimal, 7-Star and Perceptions, since those are the
ones the worked example's calibration and comparison actually use). Figure 4
above closes that gap using GSAS's own precomputed bin means, not a
recalculation.

## Sketch: how this could actually be implemented

1. **Compute real embeddings** (not done here - no network access in this
   sandbox): `sentence-transformers`, a suitable pretrained SBERT model, and
   the `skos:prefLabel`/`skos:altLabel` values already present in
   `thesaurusscience`'s vocabulary dumps.

   ```python
   from sentence_transformers import SentenceTransformer, util

   model = SentenceTransformer("all-MiniLM-L6-v2")
   emb = model.encode(["clay", "terracotta"], convert_to_tensor=True)
   cosine = util.cos_sim(emb[0], emb[1]).item()
   ```

2. **Bin the cosine score onto a GSAS scale.** For the 7-Star model this
   means picking the nearest of the 7 precomputed levels (as this scenario
   does); a real implementation would likely reuse GSAS's own
   `skos_7star.py` output table directly rather than reimplementing the
   binning, to guarantee the degree matches what GSAS itself would publish.

3. **Materialise the result as an RDF quad with `amt:weight`**, using the
   chosen level's IRI as the predicate (e.g.
   `<https://w3id.org/skos-plus/relatedMatchVeryStrong>` for star 5, or
   plain `skos:closeMatch` for star 6/7, matching how the real GSAS TTL
   files already model this) and the real `skosplus:degreeOfConnection`
   value as the weight - exactly the shape scenario 1's sketch already
   showed for feeding AMT.

4. **Repeat per candidate pair, at scale**, to build the actual recommender
   Lasse described: for every concept in a source vocabulary, embed it,
   compare against all target-vocabulary concepts, keep the top candidates,
   calibrate each with GSAS, and hand the graded result to AMT for further
   reasoning (chain composition with existing mappings, subsumption against
   CIDOC-CRM-anchored vocabularies - see scenario 3).

None of this is implemented here - `py/build_figures.py` only draws the
three figures above, from the real GSAS reference table and one placeholder
cosine value; it does not call `sentence-transformers` or GSAS's scripts.
