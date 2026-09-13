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

Only **scenario-01** is built so far. The other four are planned and will be
added scenario by scenario (see `PRIMER.md`).

| # | Scenario | Status |
|---|---|---|
| 01 | Symmetric/transitive closure via `amt:InverseAxiom` | done |
| 02 | GSAS as a calibration layer between embedding similarity and AMT input | planned |
| 03 | CIDOC-CRM class inference via Backbone Thesaurus / Pactols anchors | planned |
| 04 | Neuro-symbolic recommender (embedding signal + AMT graph plausibility) | planned |
| 05 | Feeding raw embedding distances directly into AMT (operator ablation) | planned |

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
python main.py --only scenario-01
```

Figures are written to `scenario-01-symmetric-closure/img/`. Rebuilding
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
