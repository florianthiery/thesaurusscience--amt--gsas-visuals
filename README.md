# thesaurusscience--amt--gsas-visuals

Illustrated scenarios for combining three independent projects around
archaeological terminology alignment:

- **[thesaurusscience](https://github.com/LasseMempel/thesaurusscience)**
  (Lasse Mempel) - SSSOM-compatible mappings between archaeological
  vocabularies (Getty AAT, Wikidata, GND, Pactols, FISH, DARIAH-DE, Wortnetz
  Kultur, DAI World Thesaurus and others).
- **[AMT / amt-engine](https://github.com/n4o-rse/amt-engine)** - a
  fuzzy-logic RDF reasoning engine (Florian Thiery et al.) that infers new
  graded relations from existing ones (role chains, inverses, subsumption).
- **[GSAS](https://github.com/Research-Squirrel-Engineers/GSAS)** - Gradual
  Semantic Alignment for SKOS (Florian Thiery), which augments SKOS mapping
  properties with a normalised, machine-actionable degree of connection in
  `[0, 1]`.

This repository does **not** reimplement any of the three. It is a diagram-only
companion: for each scenario, a short README explains the idea, what GSAS and
AMT concretely contribute, and how it could plausibly be implemented in
Python, alongside hand-built SVG/PNG figures illustrating it with real,
attributed excerpts from `thesaurusscience`.

## Status

All five originally discussed scenarios are built (see `PRIMER.md`).

| # | Scenario | Status |
|---|---|---|
| 01 | Symmetric/transitive closure via `amt:InverseAxiom` | done |
| 02 | GSAS as a calibration layer between embedding similarity and AMT input | done |
| 03 | CIDOC-CRM class inference via a real closeMatch/exactMatch chain | done |
| 04 | Neuro-symbolic recommender (outlook - embedding signal + AMT graph plausibility) | done |
| 05 | Feeding raw embedding distances directly into AMT (operator ablation) | done |

## Repository structure

```
thesaurusscience--amt--gsas-visuals/
├── PRIMER.md                          working plan (German, internal)
├── main.py                            orchestrator: python main.py [--list|--only NAME|--dry-run]
├── py/
│   └── viz_utils.py                   shared SVG/PNG helpers + colour scheme
├── scenario-01-symmetric-closure/
│   ├── README.md                      scenario write-up (this scenario's GSAS/AMT roles + Python sketch)
│   ├── py/build_figures.py
│   ├── data/example_mappings.sssom.tsv   real 2-row excerpt from thesaurusscience
│   └── img/                           generated: *.svg + *.png (not shipped in patches, see below)
├── scenario-02-gsas-calibration/       (same layout as scenario-01)
├── scenario-03-cidoc-class-inference/  (same layout as scenario-01)
├── scenario-04-neurosymbolic-recommender/  (same layout as scenario-01)
├── scenario-05-embedding-feed-test/     (same layout as scenario-01)
├── LICENSE
├── CITATION.cff
├── requirements.txt
└── .gitignore
```

Each scenario folder is self-contained and independently runnable; `main.py`
is a convenience that runs some or all of them in one command.

## How to run

Tested with **Python 3.10+**.

```bash
git clone https://github.com/florianthiery/thesaurusscience--amt--gsas-visuals.git
cd thesaurusscience--amt--gsas-visuals

python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
python main.py --list           # show available scenarios
python main.py                  # or --only scenario-01 / scenario-02
```

Figures are written to each scenario's own `img/` folder. Rebuilding
produces byte-identical output when nothing has changed (no timestamps, no
random SVG ids - verified by running the build twice and comparing with
`cmp`).

## Colour scheme

Diagrams follow Florian Thiery's standing colour convention for RDF/ontology
node types (Subject/Object, RealObject, Class, Term, OWL, PropMeta), applied
here to hand-built SVG instead of Mermaid. Where a diagram needs a box that is
*not* one of these six node types (e.g. an external TSV row, which is not an
RDF construct at all), an additional neutral grey style is used and called out
explicitly in that figure's legend - see each scenario's README for details.

## Data

`scenario-01-symmetric-closure/data/example_mappings.sssom.tsv` is a two-row
excerpt, copied unchanged, from two files in
[thesaurusscience](https://github.com/LasseMempel/thesaurusscience) (©
Lasse Mempel, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as
declared in the source files). This is independent of the MIT-licensed code
in this repository. The `amt:weight` values shown in the figures are
illustrative placeholders added for this repository - the SSSOM source files
carry no confidence column - and this is stated in the data file's own header
and in the scenario README so it is not mistaken for a value from
`thesaurusscience` itself.

`scenario-02-gsas-calibration/data/gsas_reference_values.tsv` is likewise
copied unchanged from the actual [GSAS](https://github.com/Research-Squirrel-Engineers/GSAS)
repository's own computed CSV outputs (MIT licence). Its
`example_concepts.tsv` uses two more real, unchanged `thesaurusscience` rows
for the concept pair, but the cosine-similarity value paired with them is an
**illustrative placeholder** (no embeddings have been computed for
`thesaurusscience` yet) - stated in that file's own header and in the
scenario README.

`scenario-03-cidoc-class-inference/data/example_chain.tsv` and
`fanin_concepts.tsv` are likewise real, unchanged rows from
`thesaurusscience` (plus one native `skos:exactMatch` statement
cross-checked directly against `Backbone Thesaurus.ttl`). The one CIDOC-CRM
class used in that scenario's figures is an **illustrative annotation** -
neither `thesaurusscience` nor the raw Backbone Thesaurus/Pactols dumps
contain any `crm:`-typed RDF at all (checked directly) - and its weight is
reused from GSAS's real minimal-model degrees, not invented. See that
scenario's README for the full account.

`scenario-04-neurosymbolic-recommender/data/candidates.tsv` mixes real and
added data too: the source concept and all four candidate concepts are
real, unchanged `thesaurusscience`/`ads_aat.sssom.tsv` entries, and each
candidate's in-degree is a genuine count from that file. The neural
similarity is an illustrative placeholder (as in scenario 2), and the
in-degree count is used as a deliberately simplified stand-in for AMT graph
plausibility - see that scenario's README for why. This scenario is an
outlook, not an implemented recommender.

`scenario-05-embedding-feed-test/data/chain_variants.tsv` reuses the exact
real chain from scenario 3 with one addition: a second, illustrative weight
for its closeMatch edge, standing in for a raw (uncalibrated) embedding
similarity fed directly into AMT - testing Lasse Mempel's own suggested
experiment. See that scenario's README for the resulting comparison.

## AI usage

Parts of the Python code and the SVG figures in this repository were written
with the assistance of Claude (Anthropic), grounded against the actual
`amt-engine` and `GSAS` source repositories (ontology files, SHACL shapes and
reasoning code) rather than from memory, to avoid the kind of hallucinated
vocabulary that has been an issue in earlier AMT modelling work. All content
was reviewed by Florian Thiery.

## Authors and licence

© 2026 Florian Thiery. Code released under the MIT Licence - see
[`LICENSE`](LICENSE). See "Data" above for the separate licence on the
excerpted mapping data.

## Citation

If you use this repository, please cite it using the metadata in
[`CITATION.cff`](CITATION.cff).
