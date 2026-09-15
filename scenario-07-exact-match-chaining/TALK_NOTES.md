# Talk notes — one sentence + one paragraph per scenario

For slide use: each scenario gets one short sentence (a slide title/section
header) and one short paragraph (what the accompanying figure(s) actually
show, for speaker notes or a caption). Written after the fact, from the
finished scenarios and their READMEs — not aspirational, describes what is
actually built and verified in each scenario folder.

## Scenario 1 — Symmetric closure

**Sentence:** AMT's `InverseAxiom` closes a gap that affects 99.9% of the
mapping corpus — not a toy example.

**Paragraph:** Of 9,831 `exactMatch`/`closeMatch`/`relatedMatch` rows
counted across four real self-mapping files in `thesaurusscience`, 9,822
have no inverse row anywhere in the same file, even though all three
predicates are symmetric by definition (SKOS Reference). `amt:InverseAxiom`
mirrors such an edge with its weight copied exactly — no fuzzy operator
involved, because it is a direct copy, not a composition, unlike every
other axiom type used later in this repository.

## Scenario 2 — GSAS as a calibration layer

**Sentence:** The same raw similarity score means something different
depending on which of GSAS's four models reads it.

**Paragraph:** A single illustrative cosine value (0.78, between two real
but currently-unmapped concepts) is run through all three of GSAS's
input-taking models — Minimal, 7-Star, Perceptions — plus the 4-Level
model shown for completeness. Minimal and 7-Star agree closely; the
empirically-grounded Perceptions model reads the same evidence more
conservatively. A model-selection guide, paraphrased from GSAS's own paper,
shows which of the four fits which curation situation.

## Scenario 3 — CIDOC-CRM class inference

**Sentence:** A concept can inherit a CIDOC-CRM class through the mapping
graph alone, no new mapping required.

**Paragraph:** A real two-hop chain (`Artefact` –closeMatch→ `goods and
commodities` –exactMatch→ `mobile objects` in the Backbone Thesaurus) is
combined with one added, clearly-flagged CIDOC-CRM class annotation
(`crm:E22_Human-Made_Object`) via `amt:RoleChainAxiom`. All six AMT fuzzy
operators are compared on the same chain; Gödel — `amt-engine`'s own
documented default for 3-ary chains — is used as the answer, correcting an
earlier, over-general claim about Einstein product.

## Scenario 4 — Neuro-symbolic recommender (outlook)

**Sentence:** The candidate with the best embedding score is not always the
one a recommender should pick.

**Paragraph:** A real source concept without a strong mapping ("clay pipe
manufacture") is ranked against four real Getty AAT/FISH candidates using
two signals: an illustrative embedding similarity, and a real graph
in-degree (how many independent sources already point to that candidate).
The lexically closest candidate ("CLAY PIPE KILN") loses to the
better-attested "kilns" once both signals are fused — under all three
fusion operators tested, not just one. Explicitly an outlook: no
recommender is implemented.

## Scenario 5 — Feeding raw embeddings directly into AMT

**Sentence:** Skipping GSAS's calibration step does not break AMT, but it
makes the choice of fuzzy operator matter roughly 2.7× more.

**Paragraph:** The same real three-link chain from scenario 3 is run twice
— once with GSAS's calibrated closeMatch degree (0.938), once with an
illustrative "raw embedding fed directly" placeholder (0.65). The spread
across all six AMT operators is 0.107 for the calibrated input versus 0.286
for the raw one, because GSAS's calibrated values sit closer to the
extremes where every operator agrees more.

## Scenario 6 — Multi-step chains across mixed properties

**Sentence:** SKOS deliberately does not let `closeMatch` or `narrowMatch`
compose across vocabularies — AMT is what makes that composition possible,
with the uncertainty made explicit instead of ignored.

**Paragraph:** Three real chains (2/3/4 `amt:RoleChainAxiom` antecedents),
crossing real vocabularies (Backbone Thesaurus → GEMET → DBpedia; Wortnetz
→ AAT → DAI, extended one hop further), mix predicates the SKOS Reference
explicitly does not declare transitive (only `exactMatch` is). Drawn in
`amt-engine`'s own documented diagram convention: solid black antecedent
edges, one red dashed inferred edge. A synthetic (clearly labelled)
comparison verifies `amt-engine`'s own warning that Product "dampens too
aggressively" past three-step chains.

## Scenario 7 — Exact-match chaining at scale, with per-technique calibration

**Sentence:** Three countries, three languages, one real Getty AAT concept
— and 226 more real opportunities just like it.

**Paragraph:** Real German, French and English excavation-recording
vocabularies each independently mapped their own word for "bridge" to the
same real AAT concept, with no direct link between any two of them
anywhere in the corpus — one of 227 such real cross-national bridging
opportunities found in the (now ~399,000-row) `thesaurusscience` mapping
corpus. `amt:InverseAxiom` + `amt:RoleChainAxiom` infer the missing link at
full confidence, since both source edges are already-curated
`exactMatch`es. A second, separate story shows why a raw embedding
similarity cannot be used the same way without a calibration step first —
using Lasse Mempel's own real, newly-computed embedding evaluation results,
including a real case where a "high-looking" score turns out to be weak
once judged against that technique's own baseline.
