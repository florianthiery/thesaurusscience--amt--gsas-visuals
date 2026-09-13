# Scenario 4 — Neuro-symbolic recommender (outlook)

## The scenario

Lasse Mempel's "endgame" idea from the chat this repository is drawn from:
for every concept in a source vocabulary that lacks a strong mapping, rank
candidate targets by combining two independent [0,1] signals - an embedding
similarity (GSAS-calibrated, scenario 2) and an AMT-derived graph
plausibility (scenario 3-style chain composition) - via a fuzzy fusion
operator. Lasse himself flagged that a full implementation "sprengt etwas
den Auftritt" (is too much for the talk); this scenario is the outlook
section that sketches the idea concretely without building the recommender
itself.

**Nothing in this scenario is a working recommender.** No embedding model,
no candidate-generation pipeline, no ranking service exists in this
repository or elsewhere. What follows is one worked example, computed by
hand from real and illustrative inputs, to make the architecture concrete.

## The worked example

**Source concept**: `wnk:wk004175` "clay pipe manufacture" - real, from
`thesaurusscience`. Its only existing mapping is a single
`skos:relatedMatch` to an unlabelled GND concept - a genuine "needs a better
mapping" case, not a constructed one.

**Four candidate targets** - all real Getty AAT / FISH concepts, found in
`Mappings/ads_aat.sssom.tsv`:

| Candidate | Real in-degree* | Neural similarity | Fused (Product) |
|---|---|---|---|
| CLAY PIPE KILN (`fish:eh_tmt2_69086`) | 0 | 0.95 (placeholder) | 0.19 |
| kilns (`aat:300022798`) | 4 | 0.78 (placeholder) | **0.78** |
| brick kilns (`aat:300022989`) | 1 | 0.55 (placeholder) | 0.22 |
| ceramic (material) (`aat:300235507`) | 2 | 0.45 (placeholder) | 0.27 |

\* Real, counted directly in `ads_aat.sssom.tsv`: how many *other* rows in
that one file `skos:exactMatch`/`skos:broadMatch` onto this concept. "kilns"
is a real hub - independently reached from KILN (exact), KILN WASTE
(broad), CLAY PIPE KILN (broad) and MALT KILN (broad). "CLAY PIPE KILN"
itself is real but is only ever a *subject* in this file, never confirmed
by anything else pointing to it.

## What is real and what is added

Real: the source concept, all four candidate concepts and labels, and every
in-degree count (`data/candidates.tsv`'s `real_indegree_in_ads_aat` column).

Added, both clearly flagged in `data/candidates.tsv`'s header:

- **`neural_similarity_placeholder`** - illustrative, for the same reason as
  scenario 2: no embeddings exist for `thesaurusscience` yet.
- **The symbolic score itself is a simplification.** Real in-degree, counted
  in one file, is used here as an honestly-computed stand-in for "AMT graph
  plausibility" because it is directly computable from real data without a
  full reasoning implementation. Genuine AMT graph plausibility (as
  scenario 3 shows) would compose *weighted paths* via `amt:RoleChainAxiom`
  across the *whole* mapping graph, not count raw in-degree in one file.
  The simplification is stated here so the distinction is not lost.

## What GSAS contributes here

Nothing beyond what scenario 2 already established: a principled way to
turn a raw embedding similarity into a calibrated `[0, 1]` degree, rather
than using the placeholder cosine directly. This scenario's "neural signal"
box is exactly scenario 2's pipeline, reused as a component.

## What AMT contributes here

- **The fusion mechanism itself**: the same `aggregate_weights` operators
  used in scenario 3 (`amt/logic.py`), applied here to combine exactly two
  inputs (neural, symbolic) into one ranking score, rather than a chain of
  mapping edges. `img/scenario-04-operator-robustness` shows that Product,
  Gödel and Geometric Mean all agree on the winner for this example - a
  reason for cautious optimism that the *ranking* is not overly sensitive
  to which operator gets chosen, though this is one example, not a proof.
- **The actual argument for fusion, made concrete**: `img/scenario-04-quadrant`
  and `img/scenario-04-before-after` show *why* two signals matter here - the
  neural-only ranking would pick "CLAY PIPE KILN" (closest label, never
  independently corroborated), while fusing in the graph signal correctly
  promotes "kilns" (a well-established concept many independent sources
  already agree on).

## Figures

1. **`img/scenario-04-architecture.svg`/`.png`** - the two-signal
   architecture: neural (GSAS-calibrated embedding) and symbolic (AMT
   graph-composed plausibility) feeding a fusion operator, producing a
   ranked candidate list.
2. **`img/scenario-04-ranking.svg`/`.png`** - grouped bar chart, all four
   real candidates, their neural/symbolic/fused scores side by side, sorted
   by fused score.
3. **`img/scenario-04-quadrant.svg`/`.png`** - neural (x) vs. symbolic (y)
   scatter: "CLAY PIPE KILN" sits high-right-low (high neural, low
   symbolic), "kilns" sits high on both - the actual winner.
4. **`img/scenario-04-operator-robustness.svg`/`.png`** - the same four
   candidates under Product, Gödel and Geometric Mean: the winner ("kilns")
   does not change.
5. **`img/scenario-04-before-after.svg`/`.png`** - neural-only ranking next
   to the fused ranking, side by side, showing the reordering directly.

## Sketch: how this could actually be implemented

This is deliberately further from implementation than scenarios 1-3's
sketches, matching its outlook status:

1. **Generate candidates** for a source concept by nearest-neighbour search
   over precomputed embeddings of every label in the target vocabularies
   (the `sentence-transformers` step already sketched in scenario 2),
   keeping the top-`k` by cosine similarity.
2. **Calibrate each candidate's neural score** via GSAS (scenario 2's
   sketch) rather than using the raw cosine.
3. **Compute each candidate's symbolic score** by running AMT's actual
   reasoning (not an in-degree count) over the existing mapping graph plus
   scenario 3-style class-inference axioms, and reading off the resulting
   `amt:weight` on any path connecting the candidate to already-trusted
   concepts.
4. **Fuse and rank**:

   ```python
   from amt.logic import aggregate_weights, PRODUCT

   for candidate in candidates:
       candidate.fused = aggregate_weights(
           [candidate.neural, candidate.symbolic], PRODUCT
       )
   candidates.sort(key=lambda c: -c.fused)
   ```

5. **Surface the top few to a human curator** rather than auto-accepting
   the top rank - GSAS's own paper is explicit that a degree of connection
   is not a probability of correctness, and neither is a fused recommender
   score.

None of this is implemented here - `py/build_figures.py` only draws the
five figures above from the one worked example in `data/candidates.tsv`.
