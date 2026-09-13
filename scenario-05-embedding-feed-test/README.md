# Scenario 5 — feeding raw embedding distances directly into AMT

## The scenario

Lasse Mempel's own suggested "small test" (chat, 2026-09): what happens if
you feed AMT with embedding distances directly, skipping GSAS's calibration
step? This scenario answers that with an actual computation, reusing the
exact same real chain as scenario 3 so the only variable is the one input
weight being tested.

## The test

Same 2-hop real chain as scenario 3 (`dai:_fac3092f` "Artefact"
→closeMatch→ `dai:_ad8ec5e3` "goods and commodities" →exactMatch→
`bbt:Concept_000017` "mobile objects" →hasCRMClass (illustrative)→
`crm:E22_Human-Made_Object`), with **one change**: the closeMatch edge is
given two alternative weights to compare -

- **GSAS-calibrated**: `0.9381` - GSAS's real minimal-model closeMatch
  degree, unchanged from scenario 2/3.
- **Raw embedding (direct)**: `0.65` - an **illustrative placeholder**
  standing in for an uncalibrated embedding similarity fed straight in, no
  GSAS binning applied. No real embeddings exist for `thesaurusscience` yet
  (same limitation as scenario 2/4), so this number cannot be a measured
  cosine value - it is chosen only to be plausibly "less extreme" than
  GSAS's own calibrated degrees, which is the entire point of the test.

The other two edges (`exactMatch = 1.0`, illustrative `hasCRMClass = 0.90`)
are identical in both runs, so any difference in the final result comes
from exactly one input.

## What was actually found

Propagating both variants through all six AMT operators
(`amt/logic.py`, copied as in scenario 3):

| Operator | GSAS-calibrated (in=0.938) | Raw embedding (in=0.65) |
|---|---|---|
| Gödel | 0.900 | 0.650 |
| Product | 0.844 | 0.585 |
| Łukasiewicz | 0.838 | 0.550 |
| Einstein | 0.839 | 0.565 |
| Geometric Mean | 0.945 | 0.836 |
| Hamacher (γ=2) | 0.839 | 0.565 |
| **spread (max−min)** | **0.107** | **0.286** |

The spread across operators is roughly **2.7× wider** for the raw-embedding
input than for the GSAS-calibrated one. This is a genuine, computed result
from this one worked example, not a general theorem - but it has a
plausible explanation: GSAS's calibrated degrees sit close to the extremes
of `[0, 1]` (0.938, 1.0), where every t-norm/co-norm agrees more (all six
operators satisfy `T(x, 1) = x` and converge as inputs approach 1). A raw,
uncalibrated similarity in the middle of the range (0.65) gives the six
operators more room to disagree.

## What GSAS contributes here

The comparison itself. GSAS's contribution is not visible in this scenario
as a new mechanism - it is visible as the *difference* between the two
rows of the table above. Skipping it doesn't break anything technically
(AMT accepts any `[0, 1]` weight regardless of provenance), but it does
make the final result more dependent on an operator choice than on the
evidence itself.

## What AMT contributes here

Nothing new mechanically - the same `amt:RoleChainAxiom` and the same six
operators as scenario 3, run twice against the same chain shape. AMT's
contribution to *this* scenario's argument is that it makes the operator's
role isolable: because AMT lets the operator be swapped independently of
the input data, this experiment (same chain, same axiom, six operators,
two input conditions) is a clean ablation rather than a confounded one.

## Figures

1. **`img/scenario-05-chain.svg`/`.png`** - the shared chain, with the
   closeMatch edge carrying both weight variants side by side (solid amber
   = GSAS-calibrated, dashed purple = raw embedding).
2. **`img/scenario-05-heatmap.svg`/`.png`** - a 2×6 grid (input condition ×
   operator), colour intensity by degree - visually, the GSAS row reads
   uniformly dark/high, the raw-embedding row shows more contrast.
3. **`img/scenario-05-headline-comparison.svg`/`.png`** - the two
   conditions under Einstein product alone (AMT's own recommendation for
   this chain length), directly comparable bars.
4. **`img/scenario-05-sensitivity-spread.svg`/`.png`** - a min-max range
   ("dumbbell") per condition, making the 0.107-vs-0.286 spread difference
   the visual subject rather than a footnote.
5. **`img/scenario-05-takeaway.svg`/`.png`** - the finding stated in one
   sentence, framed as a direct answer to Lasse's question.

## Sketch: how this could actually be tested for real

1. **Compute a real embedding similarity** for the "Artefact"/"goods and
   commodities" label pair (the same `sentence-transformers` step already
   sketched in scenario 2), instead of the `0.65` placeholder used here.
2. **Run the same chain twice through `amt-engine`** (`amt chain.ttl
   --reason --export-ttl out_gsas.ttl` and again with the raw-embedding
   weight substituted in), rather than reimplementing the six operators by
   hand as this repository's figures do.
3. **Repeat across many chains**, not just one, and report the *distribution*
   of per-chain operator spreads under each calibration condition - one
   worked example (as here) suggests the effect; many chains would test
   whether it holds generally.
4. **If it holds generally**, the practical takeaway for the CAA JCM
   abstract's recommender (scenario 4) would be concrete: calibrate
   embedding similarities with GSAS *before* handing them to AMT, not only
   for interpretability, but because doing so appears to make the choice of
   fusion/composition operator less consequential - a smaller decision
   surface for whoever configures the pipeline.

None of this is implemented here - `py/build_figures.py` only draws the
five figures above from the two hand-specified input conditions; it does
not call `amt-engine` or any embedding model.
