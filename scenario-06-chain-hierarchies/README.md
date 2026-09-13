# Scenario 6 — multi-step RoleChainAxioms across hierarchies, with GSAS

## The scenario

Plain SKOS deliberately does not let you compose most of its own mapping
properties. Checked directly against the SKOS Reference (W3C Recommendation,
18 August 2009):

- **Only `skos:exactMatch` is declared transitive** (Section 10.6.3: *"The
  only SKOS mapping property which is declared as transitive is
  skos:exactMatch"*).
- `skos:closeMatch` is explicitly **not** transitive, and the Reference
  states why (Section 10.1, paraphrased): declaring it transitive would risk
  "compound errors" when mappings are combined across more than two concept
  schemes.
- `skos:broadMatch`/`skos:narrowMatch` are sub-properties of
  `skos:broader`/`skos:narrower` respectively (S41) and inverses of each
  other (S43), but are **not** transitive either - only their
  `broaderTransitive`/`narrowerTransitive` super-properties are (S22, S24),
  and those are explicitly for inference only, never for assertion.

So a `narrowMatch` into vocabulary B cannot, in plain SKOS, be combined with
a `closeMatch` already asserted in B to say anything about vocabulary C -
by design, not by oversight. `amt:RoleChainAxiom` is what makes that
composition possible: not by assuming it silently, but by attaching an
explicit, degraded `amt:weight` to the result via a chosen fuzzy operator.
This scenario works through three real, multi-vocabulary chains that do
exactly this, at three different chain lengths (2, 3 and 4), and shows what
AMT's own documentation says about choosing an operator for each length.

## What is real and what is added

All three chains are built from real, unchanged rows in `thesaurusscience`,
crossing actual vocabulary boundaries - not constructed for this scenario:

| Chain | Path | Real source |
|---|---|---|
| 1 (2-ary) | Backbone Thesaurus `materials` –`narrowMatch`→ GEMET `metal` –`closeMatch`→ DBpedia `Metal` | `Mappings/dariah_vocabs__..._backbone_thesaurus__unknown_target_scheme.sssom.tsv` + `Mappings/dariah_vocabs__..._gemet_gemetthesaurus__unknown_target_scheme.sssom.tsv` |
| 2 (3-ary) | Wortnetz `tower (single built work)` –`narrowMatch`→ AAT `towers (single built works)` –`exactMatch`(symmetric)→ DAI `Turm` –`exactMatch`(symmetric)→ DAI `tower alone` | `Mappings/wortnetz__..._unknown_target_scheme.sssom.tsv` + `Mappings/dai_aat.sssom.tsv` + `Mappings/dai__..._scheme.sssom.tsv` |
| 3 (4-ary) | Chain 2, extended: …→ `tower alone` –`closeMatch`→ DAI `Observation tower` | as above, plus one more row in the same DAI self-mapping file |

Chain 2/3's two `exactMatch` hops are only usable in this direction thanks
to **scenario 1's `amt:InverseAxiom`**: the source rows record `Turm
exactMatch aat:...` and `tower alone exactMatch Turm`, and symmetry (real,
per SKOS S44: `exactMatch` is `owl:SymmetricProperty`) is what lets the
chain be read left-to-right. This scenario builds directly on scenario 1's
mechanism rather than re-deriving it.

**Added, and clearly flagged**: `narrowMatch` has no GSAS-calibrated degree
at all - checked against every one of GSAS's four models, none of which
positions `broadMatch`/`narrowMatch` on the Degree-of-Connection scale (see
`img/scenario-06-gsas-coverage-gap` and the Discussion below). This
scenario's `narrowMatch` edges therefore carry GSAS's `relatedMatch` degree
(`0.4947`) as a **reasoned analogy** - narrowMatch, like relatedMatch, is
looser than an equivalence-type match - not a GSAS value for narrowMatch
itself. Stated in `data/real_chains.tsv`'s own header. `exactMatch` (`1.0`)
and `closeMatch` (`0.9381`) are GSAS's real minimal-model degrees, reused
unchanged from scenario 2.

## A correction, carried over from the briefing

An earlier description in this project's chat called Einstein product "AMT's
own recommendation for 3-step chains", based on a comment in
`amt-engine/examples/skos-mapping-example.ttl` explaining one specific
heterogeneous 3-step chain. Checked against `amt-engine`'s actual ontology
README (`ontology/README.md`), the general, documented default for 3-ary
chains is **Gödel**, with Einstein product and Geometric Mean as
alternatives - the example file's comment justified Einstein over Product
for that one case, not over Gödel in general. This scenario uses the
correct, general table (reproduced in `img/scenario-06-operator-by-arity`'s
captions): Gödel default at n=2/3, Geometric Mean default at n=4.

## What GSAS contributes here

The two real per-predicate degrees (`exactMatch`, `closeMatch`) that make
two of the three chains' weights principled rather than invented, plus - by
its absence - a clearly-marked gap: GSAS has no model for hierarchical
mapping properties, so `narrowMatch`/`broadMatch` weights in any AMT
pipeline built on GSAS today require a judgement call like the one made
here, not a lookup.

## What AMT contributes here

- **`amt:RoleChainAxiom` with `amt:antecedents` of length 2, 3 and 4** -
  the actual composition mechanism, demonstrated at the arities AMT's own
  documentation gives explicit guidance for.
- **Arity-specific operator guidance, taken from `amt-engine`'s ontology
  README, not invented**: Gödel/Product for n=2, Gödel (default) for n=3,
  Geometric Mean (default) for n=4, with an explicit warning that Product
  "dampens too aggressively" past n=3 - verified numerically here
  (`img/scenario-06-product-dampening`), not just quoted.
- **The binary/n-ary implementation distinction**: five of six operators
  fold pairwise; Geometric Mean needs the whole weight list at once and
  cannot be computed incrementally - taken directly from the ontology
  README's own pseudocode.
- **A genuine mathematical curiosity, verified rather than assumed**: for a
  chain of *equal* per-edge weights, Gödel's minimum and the Geometric
  Mean coincide exactly (`min(w,...,w) = (w^n)^(1/n) = w`) - visible in
  `img/scenario-06-product-dampening` as two perfectly overlapping lines.

## Figures

1. **`img/scenario-06-chain-2ary.svg`/`.png`**, 2. **`-3ary`**, 3. **`-4ary`**
   - the three real chains, drawn in **AMT's own documented diagram
   convention** (`ontology/README.md`): solid black arrows for asserted
   antecedent edges, one red dashed arrow for the inferred consequent,
   labelled with the arity-appropriate default operator and its result.
4. **`img/scenario-06-operator-by-arity.svg`/`.png`** - all six operators
   against all three real chains side by side, each chain's AMT-recommended
   default operator named underneath.
5. **`img/scenario-06-product-dampening.svg`/`.png`** - illustrative only
   (clean 0.90-per-edge weights, not the real chains): Product visibly
   drops away from Gödel/Geometric Mean as chain length grows past 3,
   verifying AMT's own documented warning.
6. **`img/scenario-06-skos-before-after.svg`/`.png`** - what plain SKOS can
   and cannot infer, versus what `amt:RoleChainAxiom` adds.
7. **`img/scenario-06-binary-vs-nary.svg`/`.png`** - the pairwise-fold vs.
   whole-list-at-once implementation distinction among the six operators.
8. **`img/scenario-06-gsas-coverage-gap.svg`/`.png`** - which of the five
   SKOS mapping properties GSAS actually calibrates, and which it does not.

## Sketch: how this could actually be implemented

1. **Declare the chain axioms directly**, one per real chain, e.g. for
   chain 1:

   ```turtle
   ex:RCA_materialsToMetal a amt:RoleChainAxiom ;
       amt:antecedents ( skos:narrowMatch skos:closeMatch ) ;
       amt:consequent  skos:narrowMatch ;
       amt:logic       amt:GoedelLogic .   # AMT's documented default for n=2
   ```

   Chain 3 (4-ary) would use `amt:GeometricMean` instead, per the same
   table.

2. **Assert the real mapping edges as weighted RDF quads**, exactly as in
   scenario 1/3's sketches - reading the `narrowMatch`/`exactMatch`/
   `closeMatch` rows straight out of the relevant `thesaurusscience` SSSOM
   files, with GSAS-calibrated (or, for `narrowMatch`, analogy) weights
   attached via the scenario 2-style calibration step.

3. **Run `amt-engine`** (`amt chains.ttl --reason --export-ttl out.ttl`) and
   read off the inferred `narrowMatch` edges directly connecting the first
   and last concept of each chain, each carrying a weight that says how
   much the multi-hop inference should be trusted.

4. **Address the GSAS gap properly**, rather than borrowing `relatedMatch`:
   this would mean extending GSAS's own methodology (a 7-star-style curve,
   or an empirical study analogous to the Perceptions model) specifically
   for `broadMatch`/`narrowMatch`, which neither GSAS nor this repository
   currently provides.

None of this is implemented here - `py/build_figures.py` only draws the
eight figures above from the three real chains in `data/real_chains.tsv`
and one synthetic illustration; it does not call `amt-engine`.
