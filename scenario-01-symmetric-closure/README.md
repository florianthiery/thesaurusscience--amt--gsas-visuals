# Scenario 1 — Symmetric/transitive closure via `amt:InverseAxiom`

## The scenario

`thesaurusscience` currently only records mappings in one direction: a row
says `A skos:exactMatch B`, but there is no corresponding `B skos:exactMatch A`
row anywhere in the same file (the same holds for `skos:relatedMatch`). The
originally planned fix was a small Python script that adds the missing
inverse row for every `exactMatch` and `relatedMatch` triple.

This scenario replaces that script with a declarative AMT axiom instead: an
`amt:InverseAxiom` where a role is declared as its own inverse. Concretely:

```turtle
ex:IA_exactSymmetric a amt:InverseAxiom ;
    amt:antecedent skos:exactMatch ;
    amt:inverse    skos:exactMatch .

ex:IA_relatedSymmetric a amt:InverseAxiom ;
    amt:antecedent skos:relatedMatch ;
    amt:inverse    skos:relatedMatch .
```

**A note on the mechanism, corrected from an earlier, looser description in
chat**: this uses `amt:InverseAxiom`, not `amt:SubsumptionAxiom`. Checked
directly in the `amt-engine` source (`amt/reasoning.py`, `_apply_inverse`):
unlike `_apply_subsumption`, which explicitly refuses `sub == sup`,
`_apply_inverse` has no check that `antecedent != inverse`. Declaring a role as
its own inverse - i.e. symmetric - is therefore supported. The pattern is a
direct simplification of `amt-engine`'s own bundled
`examples/skos-mapping-example.ttl`, which already declares an
`InverseAxiom` between `skos:broadMatch` and `skos:narrowMatch` (two
*different* roles); this scenario is the same construct with `antecedent`
and `inverse` set to the *same* role.

## What GSAS contributes here

Nothing yet, deliberately. This scenario is pure role logic - mirroring an
edge and carrying its weight across unchanged. GSAS's calibrated
`skosplus:degreeOfConnection` values only become relevant once weights need
to be *derived* from something (an embedding similarity, a linguistic
probability) rather than simply copied - that starts in scenario 2.

## What AMT contributes here

- **`amt:InverseAxiom`**: the declarative rule itself (shown above).
- **SHACL validation** (`amt-shapes.ttl`, `InverseAxiomShape`): before
  reasoning runs, AMT checks that the axiom has exactly one `amt:antecedent`
  and exactly one `amt:inverse`, each of type `amt:Role` - catching a
  malformed axiom file before it silently does nothing.
- **Deterministic, weight-preserving mirroring**: `_apply_inverse` walks
  every edge carrying the antecedent role and adds the mirrored edge with the
  *same* `amt:weight` (no fuzzy combination needed, because this is a direct
  mirror, not a chain composition across several edges - that distinction
  matters once scenario 2 introduces role chains that *do* combine weights
  via a logic operator).
- **Idempotence for free**: because AMT only strengthens an edge that is
  itself `amt:inferred` and never overwrites an asserted one, running the
  reasoner again on an already-closed graph is a no-op rather than producing
  duplicate or conflicting rows - something a hand-written script has to
  implement deliberately, and AMT gets from its general fixed-point loop.

## Example data

`data/example_mappings.sssom.tsv` - two rows, copied unchanged, from real
files in `thesaurusscience`:

| Row | Source file | Predicate | Note |
|---|---|---|---|
| `aat:300010439` → `oeai-materials:concept23906` "clay" | `Mappings/dariah_vocabs__...oeai_materials__...oeai_materials.sssom.tsv` | `skos:exactMatch` | subject has no label in the source |
| `wnk:wk000147` "summerhouse" → `aat:300007698` | `Mappings/wortnetz__...wnk__unknown_target_scheme.sssom.tsv` | `skos:relatedMatch` | object has no label in the source |

Both source files record only this one direction; no inverse row exists in
the corpus for either. The `amt:weight` values used in the figures (`1.00`
for the `exactMatch` row, `0.60` for the `relatedMatch` row) are **illustrative
placeholders added for this repository** - the SSSOM source files carry no
confidence column at all. This is stated in the data file's own header
comment as well, so it cannot be mistaken for a value that actually appears
in `thesaurusscience`.

`data/corpus_scale.tsv` is real, computed data of a different kind: counts,
not example rows. For four real self-mapping files (subject and object
vocabulary the same, so a missing inverse would have to appear as a separate
row in the same file if it existed), every row whose predicate is one of the
three SKOS-symmetric properties was counted, and checked for whether its
reverse triple also appears in that file. See `img/scenario-01-corpus-scale`
below for the result.

## Figures

- **`img/scenario-01-inverse-closure.svg`/`.png`** - before/after network: the
  two example pairs with only the asserted edge (left) versus with the
  `amt:InverseAxiom`-mirrored edge added (right), each edge labelled with its
  predicate and `amt:weight`.
- **`img/scenario-01-data-flow.svg`/`.png`** - the pipeline: SSSOM TSV row →
  RDF quad (`rdf:subject`/`predicate`/`object` + `amt:weight`) →
  `amt:InverseAxiom` (SHACL-validated) → mirrored RDF quad → new TSV row,
  closing the loop back towards a Cocoda-importable concordance.
- **`img/scenario-01-corpus-scale.svg`/`.png`** - real, corpus-wide evidence
  for how much of `thesaurusscience` this actually affects: across four real
  self-mapping files, counting every `skos:exactMatch`/`closeMatch`/
  `relatedMatch` row (all three symmetric in SKOS), **9,822 of 9,831 rows
  (99.9%)** have no inverse present anywhere in the same file - not just the
  two rows used in the worked example above.
- **`img/scenario-01-idempotence.svg`/`.png`** - running the axiom a second
  time on an already-closed graph changes nothing: AMT only strengthens
  edges already marked `amt:inferred` and never overwrites an asserted one,
  so the fixed point is reached in one pass here.
- **`img/scenario-01-axiom-contrast.svg`/`.png`** - why this scenario has no
  fuzzy-operator choice to make, contrasted with `amt:RoleChainAxiom`
  (scenarios 3 and 5): `InverseAxiom` mirrors a weight as-is (no `amt:logic`
  property, and `_apply_inverse()` in the engine never reads one), while
  `RoleChainAxiom` composes multiple weights and requires choosing an
  operator.

Every figure uses Florian Thiery's standing colour scheme for RDF/ontology
node types (`py/viz_utils.py: Colours`). The data-flow figure also needs two
boxes for things that are *not* RDF node types in that scheme (the external
TSV row at either end); those are drawn in a separate neutral grey and called
out in the figure's own legend rather than forced into one of the six
categories.

## Sketch: how this could actually be implemented

This repository only draws the diagrams; it does not run AMT. A real
implementation would look roughly like this:

1. **Convert the SSSOM excerpt to RDF quads.** Read the TSV with `csv` or
   `pandas`, and for each row emit an `rdf:Statement` reification carrying
   `amt:weight` (as in `amt-engine`'s own examples), e.g. with `rdflib`:

   ```python
   from rdflib import Graph, BNode, RDF, Literal, XSD, Namespace

   AMT = Namespace("http://academic-meta-tool.xyz/vocab#")
   SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

   g = Graph()
   for row in read_sssom_tsv("example_mappings.sssom.tsv"):
       stmt = BNode()
       g.add((stmt, RDF.subject, row.subject_iri))
       g.add((stmt, RDF.predicate, row.predicate_iri))
       g.add((stmt, RDF.object, row.object_iri))
       g.add((stmt, AMT.weight, Literal(row.weight, datatype=XSD.decimal)))
   ```

2. **Declare the two roles and the `InverseAxiom`s** as shown above, in the
   same file or a separate axioms file - `amt-engine` loads its own
   `ontology/amt.ttl` automatically, so only the domain-specific roles and
   axioms need to be authored.
3. **Run `amt-engine`'s own CLI** rather than reimplementing the reasoning:

   ```bash
   pip install amt-engine
   amt scenario-01.ttl --validate
   amt scenario-01.ttl --reason --export-ttl scenario-01-closed.ttl
   ```

4. **Convert the closed graph back to SSSOM rows** (the reverse of step 1),
   and either append these as new rows to the relevant `thesaurusscience` TSV
   files or route them into Cocoda as an additional concordance import - the
   `rdf:subject`/`predicate`/`object` triple of every edge tagged
   `amt:inferred` maps directly back onto `subject_id`/`predicate_id`/
   `object_id`, with `mapping_justification` set to something like
   `semapv:LogicalReasoning` rather than `semapv:UnspecifiedMatching`, since
   the provenance is now the axiom rather than "unknown".

None of this is implemented here - `py/build_figures.py` only draws the two
figures above from the two-row excerpt, it does not call `amt-engine`.
