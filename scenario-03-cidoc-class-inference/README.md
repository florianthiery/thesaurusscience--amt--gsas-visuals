# Scenario 3 — CIDOC-CRM class inference via a real closeMatch/exactMatch chain

## The scenario

Lasse Mempel's own observation (chat, 2026-09): Backbone Thesaurus and
Pactols are CIDOC-CRM-oriented, so it might be possible to infer a
concept's CIDOC class from its position in the mapping graph rather than
asserting it directly. This scenario works through one concrete, mostly-real
instance of that idea.

## A mechanism correction, made before building this

An earlier description in this project's chat called the mechanism
"subsumption". That was wrong in a specific way worth recording:

- `amt:instanceOf` (the property that would normally link an individual to
  its type) is reserved for AMT's own internal Concept-typing/validation
  system - checked directly in `amt/core.py` and `amt.ttl`. It is not typed
  `amt:Role`, so it **cannot** appear inside an `amt:RoleChainAxiom`'s
  `amt:antecedents` list, which requires every link to be an `amt:Role`.
- `amt:SubsumptionAxiom` relates two *roles* to each other ("every edge
  carrying the sub-role also carries the super-role") - not a concept to a
  class via a mapping edge.

The mechanism that actually does this: model CIDOC class membership as a
**custom role**, `ex:hasCRMClass` (not `amt:instanceOf`), so it can sit
inside an ordinary `amt:RoleChainAxiom` alongside `skos:closeMatch` and
`skos:exactMatch` - exactly the same construct scenario 1 and 2 already
used, just with one more (self-defined) role in the chain. No new AMT
feature is needed; this is a modelling choice, not an engine change.

## Befund: no literal CIDOC-CRM typing exists in the data

Checked directly (2026-09-13): neither `Dariah Vocabs/Backbone Thesaurus.ttl`
nor either Pactols RDF dump in `thesaurusscience` declares a `crm:` namespace
or contains a single `crm:`-typed triple. Backbone Thesaurus's scope notes
*reference* CIDOC-CRM and CRMgeo in prose (e.g. "can be coordinated with the
suitable type of phenomenal place, in the sense of CRMgeo") - real,
conceptual alignment - but there is no machine-readable class assertion to
crosswalk mechanically. The one CIDOC class used in this scenario,
`crm:E22_Human-Made_Object`, is therefore an **illustrative annotation**,
added here and motivated by the real concept's own label and facet
("mobile objects", under "material things") - not sourced from the data.
Stated in `data/example_chain.tsv`'s header as well.

## What is real and what is added

Real, unchanged, found by searching `thesaurusscience` and cross-referencing
against the raw `Backbone Thesaurus.ttl` dump:

- `dai:_fac3092f` "Artefact" —`skos:closeMatch`→ `dai:_ad8ec5e3`
  "goods and commodities" (`Mappings/dai__..._scheme.sssom.tsv`, line 6111).
- `dai:_ad8ec5e3` "goods and commodities" (also labelled "Mobile Objekte"@de
  in the DAI dump) —`skos:exactMatch`→ `bbt:Concept_000017` "mobile objects"
  in Backbone Thesaurus - present both as a separate SSSOM row
  (`Mappings/dariah_vocabs__..._scheme.sssom.tsv`, line 229) **and** as a
  native `skos:exactMatch` statement inside `Backbone Thesaurus.ttl` itself.
- Three further real concepts that `skos:closeMatch` the same anchor
  (`data/fanin_concepts.tsv`), used for the "at scale" figure: `dai:_4377`
  "finds and collected material", `dai:_771e668b` "Objektgattungen" (no
  English label in this DAI export - shown as-is rather than invented).

Added for this scenario, clearly flagged in the data files and here:

- `ex:hasCRMClass crm:E22_Human-Made_Object` on `bbt:Concept_000017` - the
  one illustrative link, discussed above.
- Its weight, `0.90` - deliberately **below** 1.0, to reflect that this is
  an inference-workflow addition rather than a documented fact, not a
  measured confidence.
- The `closeMatch`/`exactMatch` weights are **not** invented for this
  scenario - they are GSAS's own real minimal-model degrees (`0.9381`,
  `1.0`), reused from scenario 2's reference table, giving the whole chain a
  consistent, traceable provenance.

## What GSAS contributes here

The two real SKOS mapping weights (`0.9381` for closeMatch, `1.0` for
exactMatch) - the same minimal-model degrees introduced in scenario 2,
reused rather than re-derived. GSAS has no notion of "class inference"
itself; its contribution here is exactly what it was designed for -
principled numeric weights for existing SKOS mapping properties - feeding
into a chain that AMT composes.

## What AMT contributes here

- **`amt:RoleChainAxiom`** with a 3-link `amt:antecedents` list
  (`skos:closeMatch`, `skos:exactMatch`, `ex:hasCRMClass`) and
  `amt:consequent ex:hasCRMClass` - propagating class membership across two
  real mapping edges and one added assertion in a single declarative rule.
- **A concrete operator recommendation, taken from AMT's own example file**:
  `amt-engine/examples/skos-mapping-example.ttl` recommends Einstein
  product specifically for 3-step chains ("gentler than ProductLogic for
  n=3, keeping more signal"). This scenario follows that recommendation
  (`img/scenario-03-operator-comparison` shows why: Einstein sits between
  the conservative Gödel minimum and the more punishing Product/
  Lukasiewicz values).
- **Scale, for free**: the same axiom, defined once, applies to every
  concept that closeMatches the anchor - demonstrated with three real
  concepts in `img/scenario-03-fanin`, not just the one worked example in
  `img/scenario-03-network`.
- **A genuine mathematical detail worth knowing**: Einstein product and
  Hamacher product at γ=2 coincide exactly (both reduce to the same
  `(xy)/(2-(x+y-xy))` form) - verified numerically here (`0.839076` for
  both, to six decimals), not merely close. Copied from `amt/logic.py`'s
  actual pairwise fold implementations, not re-derived independently.

## Figures

1. **`img/scenario-03-network.svg`/`.png`** - the core chain: three real
   concept ovals connected by the two real mapping edges, one illustrative
   `hasCRMClass` edge into an orange CIDOC-class box, and the inferred
   dashed edge (Einstein product, `w = 0.839`) running directly from
   "Artefact" to the class.
2. **`img/scenario-03-pipeline.svg`/`.png`** - the RDF/AMT view: three
   asserted quads feeding into one `amt:RoleChainAxiom` box, producing one
   inferred quad.
3. **`img/scenario-03-operator-comparison.svg`/`.png`** - the same 3-link
   chain under all six AMT operators (Gödel 0.900, Product 0.844,
   Łukasiewicz 0.838, Einstein 0.839, Geometric Mean 0.945, Hamacher γ=2
   0.839), with Einstein highlighted as AMT's own documented choice for
   this chain length.
4. **`img/scenario-03-fanin.svg`/`.png`** - three real DAI concepts fanning
   into the same anchor, all inheriting the same illustrative CIDOC class
   through one shared axiom - the "at scale" argument made concrete.
5. **`img/scenario-03-before-after.svg`/`.png`** - a one-glance summary:
   three disconnected concepts before, one shared class after.

## Sketch: how this could actually be implemented

1. **Model the custom role once**, alongside the SKOS roles already shown
   in scenario 1/2's sketches:

   ```turtle
   ex:hasCRMClass a amt:Role ;
       rdfs:label "hasCRMClass" ;
       rdfs:domain ex:Concept ;
       rdfs:range  ex:Concept .   # CIDOC classes represented as individuals too
   ```

2. **Assert the one illustrative link and the real mapping edges** as RDF
   quads with `amt:weight`, exactly as in scenario 1/2's sketches - the
   real ones read from `thesaurusscience`, the illustrative one written
   once by whoever curates the class annotations.

3. **Declare the chain axiom**:

   ```turtle
   ex:RCA_crmClassPropagation a amt:RoleChainAxiom ;
       amt:antecedents ( skos:closeMatch skos:exactMatch ex:hasCRMClass ) ;
       amt:consequent  ex:hasCRMClass ;
       amt:logic       amt:EinsteinProduct .
   ```

4. **Run `amt-engine`** (`amt scenario-03.ttl --reason --export-ttl
   out.ttl`, as in scenario 1's sketch) and read off every inferred
   `ex:hasCRMClass` edge - each one a concept that gained a CIDOC anchor
   "for free" from the mapping graph, with a weight that says how much to
   trust it.

5. **Scale it**: run this once against the *whole* `thesaurusscience`
   corpus rather than three hand-picked concepts, and pair it with
   scenario 2's embedding-calibrated weights instead of the fixed GSAS
   minimal-model values used here, for a weight that reflects each
   individual mapping's actual strength rather than a single shared number.

None of this is implemented here - `py/build_figures.py` only draws the
five figures above from the real chain and the real fan-in data; it does
not call `amt-engine`.
