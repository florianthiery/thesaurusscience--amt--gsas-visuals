# PRIMER — thesaurusscience--amt--gsas-visuals

Arbeitsplan für dieses Repo. Wird zu Beginn jedes Chats hochgeladen und am
Ende zurückgeschrieben. Teil A gilt immer, Teil B/C sind die Schritte
(ein Schritt = ein Szenario), Teil D sind offene Punkte.

## Teil A — Immer gültig

### A1 Ausgangslage

| Repo | Rolle | Status |
|---|---|---|
| `LasseMempel/thesaurusscience` | Quelle der echten SSSOM-Mappings | extern, read-only Referenz |
| `n4o-rse/amt-engine` | Fuzzy-Logic-RDF-Reasoning-Engine | extern, read-only Referenz |
| `Research-Squirrel-Engineers/GSAS` | Gradual Semantic Alignment for SKOS | extern, read-only Referenz |
| `florianthiery/thesaurusscience--amt--gsas-visuals` | dieses Repo | neu, S0–S6 erledigt (alle 6 Szenarien) |

**Befunde** (durch tatsächliches Klonen und Lesen der drei Quell-Repos
geprüft, nicht aus dem Gedächtnis):

- `amt.ttl`: Symmetrische Rollenschließung ist `amt:InverseAxiom`
  (`amt:antecedent`/`amt:inverse`), **nicht** `amt:SubsumptionAxiom` — Korrektur
  gegenüber einer früheren, zu ungenauen Aussage im Chat (geprüft 2026-09-13).
- `amt/reasoning.py`, `_apply_inverse`: keine Gleichheitsprüfung zwischen
  `antecedent` und `inverse` (anders als `_apply_subsumption`, die `sub == sup`
  explizit abfängt). Ein Axiom mit `antecedent == inverse` (Rolle als eigene
  Inverse = symmetrisch) ist also unterstützt und genau der Mechanismus für
  Szenario 1 (geprüft 2026-09-13).
- `amt-engine/examples/skos-mapping-example.ttl` existiert bereits und deckt
  SKOS-Rollenketten, alle sechs Logikoperatoren und ein `InverseAxiom`
  (broadMatch/narrowMatch) ab — gute Vorlage für Szenario 1 und 2, nicht neu
  erfunden (geprüft 2026-09-13).
- GSAS-Namespace `skosplus: <https://w3id.org/skos-plus/>`, zentrale Property
  `skosplus:degreeOfConnection` (`owl:AnnotationProperty`); 7-Star-Level als
  `skosplus:starLevel`; Perceptions-Modell als `skosplus:perceptions_*`
  Sub-Properties von `skos:exactMatch`/`closeMatch` (geprüft 2026-09-13,
  `skos_minimal_degrees.ttl`, `skos_7star_mapping.ttl`, `merged_ontology.ttl`).
- `thesaurusscience/Mappings`: 31 SSSOM-TSV/TTL-Dateien. Die
  Wortnetz-Kultur-Datei (10.814 Zeilen) enthält alle fünf SKOS-Mapping-
  Prädikate, aber durchgängig keine aufgelösten `object_label` (geprüft
  2026-09-13). Die DARIAH-Materials-Selbstabbildung liefert ein sauberes
  `exactMatch`-Paar mit einseitig aufgelöstem Label
  (`aat:300010439` → `oeai-materials:concept23906` "clay"); keine Rückkante
  im Corpus vorhanden (geprüft 2026-09-13).
- **`cairosvg` bricht auf Windows** (Flos Maschine, gemeldet nach dem ersten
  Commit): `OSError: no library called "cairo-2" was found`. `cairosvg`
  installiert über `pip` sauber, lädt zur Laufzeit aber die native
  `libcairo-2.dll` per `dlopen()`, die `pip` nicht mitbringt — kein
  Konfigurationsfehler bei Flo, sondern eine strukturelle Schwäche der
  ursprünglichen Bibliothekswahl. Behoben durch eine `Canvas`-Abstraktion in
  `py/viz_utils.py`: dieselbe Diagrammgeometrie wird einmal gegen
  `SVGCanvas` (String-Aufbau) und einmal gegen `PNGCanvas` (reines Pillow
  `ImageDraw`, kein Umweg über SVG) ausgeführt, kein natives Rendering, kein
  `cairosvg`. Nebenbefund dabei: Pillows eingebaute Schrift
  (`ImageFont.load_default(size=...)`, ab Pillow 10.1) hat keine Glyphen für
  „—" oder „→" (als leere Kästchen sichtbar im ersten Pillow-Render) — durch
  ASCII-Ersatz (`-`, `->`) behoben. In einer komplett frischen venv (nur
  `Pillow` aus `requirements.txt`) verifiziert (geprüft 2026-09-13).
- **GSAS-Formeln und -Werte für Szenario 2**, direkt aus den echten Skripten
  gelesen (nicht aus dem Paper nachgerechnet): 7-Star nutzt
  `d(s) = (1 − e^(−k·(s−1)/6)) / (1 − e^(−k))` mit `k = 2.0`
  (`skos/skos.py: degree_of_connection`); Perceptions klassifiziert Phrasen
  anhand `EXACT_MIN = 0.9382` / `CLOSE_MIN = 0.4948` und nutzt eine
  Logistik-Kurve `k = 0.348`, `r0 = 9.73` nur zur Interpolation, der
  eigentliche Degree ist der empirische Median (`skos_perceptions/
  skos_perceptions.py`). Die Perceptions-Schwellen sind fast identisch mit
  den 7-Star-Werten für closeMatch/relatedMatch — vermutlich bewusst so
  kalibriert (geprüft 2026-09-13, `skos_7star_degrees.csv`,
  `skos_minimal_degrees.csv`, `skos_perceptions_stats.csv`).
- **Wichtige Modellierungs-Nuance**: GSAS definiert `d(s)` für das 7-Star-
  Modell formal nur für die 7 diskreten Stufen, nicht als Funktion beliebiger
  kontinuierlicher Eingaben. Die kontinuierliche Interpolationskurve in
  `scenario-02-calibration-curves` ist eine Vereinfachung *für diese Abbildung*,
  keine GSAS-Aussage — im Abbildungstitel und im Szenario-README ausdrücklich
  so benannt. Die eigentliche AMT-gebundene Abbildung (`scenario-02-pipeline`)
  bindet stattdessen auf die nächstgelegene diskrete Stufe (Stern 6) und nutzt
  deren echten, tabellierten Degree (0.9381).
- **Keine echten Embeddings verfügbar**: Lasse hat laut Chat-Log noch keine
  SBERT-Embeddings für `thesaurusscience` berechnet, und diese Sandbox hat
  keinen Internetzugang zu HuggingFace. Der Cosinus-Wert in Szenario 2
  (0.78, Paar "clay"/"terracotta") ist daher ein klar gekennzeichneter
  Platzhalter, kein Messwert (geprüft/entschieden 2026-09-13).
- **Korrektur zu Szenario 3, AMT-Mechanismus**: `amt:instanceOf` ist rein
  intern (Concept-Typisierung/Validierung, `amt/core.py`), nicht vom Typ
  `amt:Role` und daher **nicht** kettenfähig in `amt:RoleChainAxiom`.
  `amt:SubsumptionAxiom` betrifft Rollen-zu-Rollen-Hierarchien, nicht
  Klassenvererbung über eine Mapping-Kante. Der richtige Mechanismus:
  CIDOC-Klassenzugehörigkeit als **eigene Rolle** modellieren
  (`ex:hasCRMClass`, nicht `amt:instanceOf`), dann ganz normal per
  `amt:RoleChainAxiom` verketten — derselbe Mechanismus wie in Szenario 1/2,
  nur mit einer selbstdefinierten Rolle (geprüft 2026-09-13, `amt/reasoning.py`,
  `amt/core.py`, `amt-shapes.ttl`).
- **Keine CIDOC-CRM-Typisierung im Corpus**: `Backbone Thesaurus.ttl` und
  beide Pactols-RDF-Dumps enthalten keinen einzigen `crm:`-Namespace, keine
  einzige `crm:`-Aussage (direkt geprüft). Lasses "CIDOC-orientiert" bezieht
  sich auf die konzeptionelle Anlehnung in Scope Notes (die CRMgeo als Text
  erwähnen), nicht auf maschinenlesbare Typisierung. Die in Szenario 3
  verwendete CIDOC-Klasse ist daher eine begründete, aber hinzugefügte
  Annotation, kein Fund (geprüft 2026-09-13).
- **Echte mehrstufige Kette für Szenario 3 gefunden**: `dai:_fac3092f`
  "Artefact" —closeMatch→ `dai:_ad8ec5e3` "goods and commodities" (real,
  `Mappings/dai__..._scheme.sssom.tsv` Zeile 6111) —exactMatch→
  `bbt:Concept_000017` "mobile objects" (real, sowohl als eigene SSSOM-Zeile
  als auch nativ im Backbone-Thesaurus-Dump selbst). Drei weitere reale
  Konzepte (`dai:_4377`, `dai:_771e668b`) closeMatchen denselben Anker,
  genutzt fürs Fan-in-Bild (geprüft 2026-09-13).
- **AMT-Logikoperatoren direkt aus `amt/logic.py` kopiert** (nicht
  nachgerechnet), inkl. der exakten Pairwise-Fold-Implementierung. Befund:
  Einstein Product und Hamacher Product bei γ=2 sind für die drei Gewichte
  [0.9381, 1.0, 0.90] **exakt identisch** (0.839076 beide) — eine echte
  mathematische Koinzidenz (Hamacher bei γ=2 ≡ Einstein per Definition),
  keine Rundung (geprüft 2026-09-13).
- **Reales Beispiel für Szenario 4 gefunden**: `wnk:wk004175` "clay pipe
  manufacture" hat aktuell nur ein einziges, schwaches `relatedMatch` zu
  einem unbeschrifteten GND-Konzept — ein echter "braucht ein besseres
  Mapping"-Fall. Vier reale Kandidatenkonzepte aus
  `Mappings/ads_aat.sssom.tsv` gefunden, inkl. eines direkt passenden FISH-
  Konzepts "CLAY PIPE KILN" (geprüft 2026-09-13).
- **Realer In-Degree als Symbolik-Stellvertreter**: Anzahl der Zeilen in
  `ads_aat.sssom.tsv`, die auf ein Kandidatenkonzept verweisen, echt gezählt
  (kilns=4, ceramic=2, brick kilns=1, CLAY PIPE KILN=0). Bewusst als
  vereinfachter, aber ehrlich berechneter Stellvertreter für "AMT-
  Graph-Plausibilität" verwendet — echte AMT-Graphgewichte würden
  gewichtete Pfade über `amt:RoleChainAxiom` komponieren (wie Szenario 3),
  nicht rohen In-Degree in einer Datei zählen. Ergebnis: unter allen drei
  getesteten Operatoren (Product, Gödel, GeometricMean) gewinnt "kilns",
  nicht das lexikalisch nächstliegende "CLAY PIPE KILN" — die eigentliche
  Pointe für die Fusion zweier Signale (geprüft 2026-09-13).
- **Szenario 5, Lasses "kleiner Test" konkret gerechnet**: dieselbe echte
  Kette aus Szenario 3, nur die closeMatch-Kante mit zwei Alternativ-
  Gewichten (0.9381 GSAS-kalibriert vs. 0.65 illustrativ als "roher,
  direkt eingespeister Embedding-Wert"). Ergebnis: die Spannweite über alle
  6 Operatoren ist beim rohen Embedding-Wert **~2,7× breiter** (0.286 vs.
  0.107) als beim GSAS-kalibrierten Wert — plausibel erklärbar dadurch,
  dass GSAS-Werte näher an den Extremen (0/1) liegen, wo alle sechs
  T-Normen/Co-Normen stärker übereinstimmen (geprüft/berechnet 2026-09-13).
- **Szenario 1, Corpus-Scale-Nachtrag**: über vier echte Selbstabbildungs-
  Dateien gezählt (jede Zeile mit symmetrischem SKOS-Prädikat: exactMatch/
  closeMatch/relatedMatch), fehlt bei **9.822 von 9.831 Zeilen (99,9 %)**
  die Inverse in derselben Datei — nicht nur bei den zwei Beispielzeilen.
  Bestätigt, dass das Problem corpus-weit ist, nicht nur ein Spielbeispiel
  (geprüft/gezählt 2026-09-13).
- **Szenario 1, Korrektur einer eigenen Behauptung vor Auslieferung**: erster
  Entwurf der Abbildung 5 behauptete "SHACL verbietet `amt:logic` bei
  `InverseAxiom`" — geprüft und falsch befunden (`amt-shapes.ttl` hat kein
  `sh:closed`, verbietet also nichts explizit). Richtig: `_apply_inverse()`
  in `amt/reasoning.py` liest schlicht kein `amt:logic`-Property, die
  Spiegelung ist eine reine Kopie, keine Komposition (korrigiert vor
  Auslieferung, 2026-09-13).
- **Szenario 2, 4-Level-Modell nachgetragen**: echte Werte aus
  `skos_4level/skos_4level_degrees.csv` — dubious=0.164 (mean d(1,2)),
  low=0.647 (mean d(3,4)), medium=0.852 (d(5)), high=0.969 (mean d(6,7)) —
  bislang in keiner Abbildung gezeigt (geprüft 2026-09-13).
- **Szenario 6, SKOS Reference direkt geprüft** (W3C Recommendation,
  18.08.2009): nur `skos:exactMatch` ist transitiv (Section 10.6.3, explizit
  so formuliert). `closeMatch` ist bewusst nicht transitiv, Begründung laut
  Section 10.1 (paraphrasiert): Vermeidung von "compound errors" beim
  Kombinieren über mehr als zwei Vokabulare. `broadMatch`/`narrowMatch` sind
  Sub-Properties von `broader`/`narrower` (S41) und zueinander invers (S43),
  aber ebenfalls nicht transitiv. Erste Version hatte "Section 8.1" zitiert
  — beim Nachschlagen im vollständigen Dokument als "Section 10.1"
  korrigiert, vor Auslieferung (geprüft 2026-09-13).
- **Szenario 6, Korrektur zu Szenario 3**: `amt-engine`s eigene
  Ontology-README (`ontology/README.md`) nennt für 3-äre Ketten **Gödel**
  als Default-Empfehlung (Einstein/GeometricMean als Alternativen) — nicht
  Einstein, wie in Szenario 3 zu allgemein formuliert. Der dortige
  Einstein-Kommentar im Beispielfile begründete Einstein nur gegenüber
  Product für eine bestimmte 3er-Kette, nicht gegenüber Gödel generell.
  Szenario 3 selbst wurde dafür (noch) nicht rückwirkend geändert — auf
  Wunsch nachholbar (geprüft 2026-09-13).
- **Szenario 6, drei echte mehrstufige Ketten gefunden**, die gemischte
  SKOS-Properties über mehrere Vokabulare hinweg verketten: (1) Backbone
  `materials` –narrowMatch→ GEMET `metal` –closeMatch→ DBpedia `Metal`
  (2-är); (2) Wortnetz `tower` –narrowMatch→ AAT `towers` –exactMatch
  (Symmetrie)→ DAI `Turm` –exactMatch(Symmetrie)→ DAI `tower alone` (3-är);
  (3) wie (2), verlängert um –closeMatch→ DAI `Observation tower` (4-är).
  `narrowMatch` wird von keinem der vier GSAS-Modelle kalibriert — als
  begründete Analogie wird GSAS' `relatedMatch`-Degree (0.4947) verwendet,
  klar gekennzeichnet (geprüft 2026-09-13).

### A2 Zielbild

```
thesaurusscience (echte SSSOM-TSVs)
        |
        v
  scenario-0X-.../
    README.md          Szenario, GSAS-Rolle, AMT-Rolle, Python-Skizze
    data/*.sssom.tsv   echter, attributierter Mini-Ausschnitt
    py/build_figures.py  reines Python/SVG (kein matplotlib/graphviz)
    img/*.svg + *.png    generiert, deterministisch
        |
        v
  main.py  orchestriert alle Szenarien (--list/--only/--from/--skip/--dry-run)
```

Eigenschaften, die das fertige Repo erfüllen muss:
1. Jedes Szenario ist eigenständig lauffähig (`python scenario-0X.../py/build_figures.py`).
2. Ein erneuter Build ist byte-identisch (geprüft per doppeltem Lauf + `cmp`).
3. Jeder AMT-/GSAS-Fachbegriff ist gegen die echten Ontologie-/Code-Dateien
   geprüft, nicht rekonstruiert.
4. Jedes Beispiel ist ein echter, attributierter Ausschnitt aus
   `thesaurusscience` (keine erfundenen Konzepte).
5. Nur Englisch im Repo (Code, README, Kommentare); Deutsch nur hier.

### A3 Querschnittsregeln

- Kein `datetime.now()` irgendwo — feste `RELEASE`-Konstante in
  `py/viz_utils.py`.
- `img/` wird **nicht** von `.gitignore` ausgeschlossen — die generierten
  Figuren sind das zitierfähige Produkt dieses Repos.
- Reines Python/SVG (Diagramm-Stil wie `bb5kbc-visuals`), kein Mermaid, kein
  matplotlib/graphviz.
- Englisch für Code/README/Kommentare; Deutsch nur in `PRIMER.md`.
- Ein Schritt = ein Szenario = ein Chat-Durchgang: vor jedem Szenario wird
  kurz gebrieft (Beispieldaten, geplante Visuals, Anzahl), erst nach
  Zustimmung wird gebaut und als Patch-ZIP geliefert.
- AMT-/GSAS-Vokabular wird vor Verwendung gegen die echten Repos geprüft
  (`amt.ttl`, `amt-shapes.ttl`, `amt/reasoning.py`; GSAS-`.ttl`-Dateien) —
  nicht aus dem Gedächtnis rekonstruiert (Lehre aus früheren AMT-Sessions,
  siehe auch das AMT-Projekt-Gedächtnis).
- Windows als Referenzplattform für Kommandos in `PATCH-README.md`.

### A4 Beschlusslage

| Frage | Beschluss | seit |
|---|---|---|
| Diagrammtechnik | Reines Python (SVG/PNG), kein Mermaid | 2026-09-13 |
| Sprache im Repo | Nur Englisch | 2026-09-13 |
| Datenbasis für Beispiele | Echte Mini-Ausschnitte aus `thesaurusscience` | 2026-09-13 |
| Szenario-1-Mechanismus | `amt:InverseAxiom` mit `antecedent = inverse = Rolle` (Symmetrie), nicht `SubsumptionAxiom` | 2026-09-13 |
| Szenario-1-Beispieldaten | `aat:300010439` –exactMatch→ `oeai-materials:concept23906` "clay"; `wnk:wk000147` "summerhouse" –relatedMatch→ `aat:300007698` | 2026-09-13 |
| `amt:weight`-Werte in Szenario 1 | Illustrative Platzhalter (1.00 / 0.60), nicht aus der SSSOM-Quelle — explizit so gekennzeichnet in Datei-Header, README und Abbildung | 2026-09-13 |
| Bildanzahl je Szenario | Vorschlag 2/3/2/2/2 (insgesamt 11) | Vorschlag, seit 2026-09-13 |
| Bildformat | SVG + PNG, beide direkt aus derselben Geometrie über eine `Canvas`-Abstraktion (`SVGCanvas`/`PNGCanvas`) | 2026-09-13, korrigiert 2026-09-13 |
| PNG-Rendering | Reines Pillow (`ImageDraw`, `ImageFont.load_default(size=...)`), **nicht** `cairosvg` | 2026-09-13 (Korrektur, s. Befund unten) |
| Szenario-2-Beispielpaar | `aat:300010439` "clay" / `aat:300010669` "terracotta" — real, beide einzeln ins DARIAH-Vokabular gemappt, aber nicht miteinander | 2026-09-13 |
| Szenario-2-Cosinus-Wert | 0.78, illustrativer Platzhalter (keine echten Embeddings verfügbar, kein Internetzugang zu HuggingFace in der Sandbox) | 2026-09-13 |
| Szenario-2-Bilder | 3 wie vorgeschlagen: Kalibrierungskurven-Vergleich, Pipeline (diskrete Bindung), Balkendiagramm (gleicher Input, 3 Modelle) | 2026-09-13, bestätigt und gebaut |
| Zweck von Szenario 2 (und generell) | Erster Entwurf zur Vorlage an Lasse Mempel — nicht final, seine Ideen/Änderungswünsche werden danach eingearbeitet | 2026-09-13 |
| Szenario-3-Mechanismus | `amt:RoleChainAxiom` mit selbstdefinierter Rolle `ex:hasCRMClass` (nicht `amt:instanceOf`, nicht `SubsumptionAxiom`) | 2026-09-13 |
| Szenario-3-Beispielkette | `dai:_fac3092f` "Artefact" –closeMatch→ `dai:_ad8ec5e3` "goods and commodities" –exactMatch→ `bbt:Concept_000017` "mobile objects" –hasCRMClass(illustrativ)→ `crm:E22_Human-Made_Object` | 2026-09-13 |
| Szenario-3-Gewichte | closeMatch/exactMatch = echte GSAS-Minimal-Degrees (0.9381/1.0, wiederverwendet aus Szenario 2); hasCRMClass = 0.90, illustrativ | 2026-09-13 |
| Szenario-3-Logikoperator | Einstein Product (AMT-eigene Empfehlung für 3er-Ketten laut `skos-mapping-example.ttl`); alle 6 Operatoren zum Vergleich gezeigt | 2026-09-13 |
| Szenario-3-Ordnername | `scenario-03-cidoc-class-inference` (umbenannt von der ursprünglich skizzierten „…-subsumption", passend zur Korrektur) | 2026-09-13 |
| Szenario-3-Bilder | 5 (Netzwerk, Pipeline, Operator-Vergleich, Fan-in, Vorher/Nachher) — auf Wunsch erweitert von ursprünglich 2 | 2026-09-13 |
| Szenario-4-Beispiel | `wnk:wk004175` "clay pipe manufacture" (real) gegen 4 reale AAT/FISH-Kandidaten aus `ads_aat.sssom.tsv` | 2026-09-13 |
| Szenario-4-Symbolik-Signal | Realer In-Degree in `ads_aat.sssom.tsv` (Laplace-geglättet), als ehrlich benannter, vereinfachter Stellvertreter für echte AMT-Graphgewichte | 2026-09-13 |
| Szenario-4-Fusionsoperator | Product als Schlagzeile, alle 3 nicht-parametrisierten Operatoren zum Robustheitsvergleich gezeigt | 2026-09-13 |
| Szenario-4-Bilder | 5 (Architektur, Ranking, Quadrant, Operator-Robustheit, Vorher/Nachher) | 2026-09-13 |
| Szenario-5-Test | Dieselbe echte Kette wie Szenario 3, closeMatch-Gewicht 2x variiert (GSAS 0.9381 vs. illustrativ 0.65) | 2026-09-13 |
| Szenario-5-Bilder | 5 (Kette mit Doppel-Gewicht, Heatmap, Headline-Vergleich, Sensitivitäts-Spread, Takeaway) | 2026-09-13 |
| Szenario-1/2 auf 5 Bilder erweitert | Auf Wunsch nachträglich: S1 +3 (Corpus-Scale, Idempotenz, Axiom-Kontrast), S2 +2 (4-Level-Modell, Modellauswahl-Guide) | 2026-09-13 |
| Szenario-6-Ketten | 3 echte mehrstufige Ketten (2-är/3-är/4-är), gemischte Properties über mehrere Vokabulare (s. A1) | 2026-09-13 |
| Szenario-6-narrowMatch-Gewicht | GSAS-`relatedMatch`-Degree (0.4947) als begründete Analogie, da GSAS `narrowMatch` nicht kalibriert | 2026-09-13 |
| Szenario-6-Operatoren je Arität | Aus `amt-engine`s Ontology-README übernommen: Gödel (n=2,3 Default), GeometricMean (n=4 Default) — nicht Einstein wie in Szenario 3 zu allgemein behauptet | 2026-09-13 |
| Szenario-6-Bilder | 8 (3× Ketten-Diagramm im n-ary-Stil, Operator-nach-Arität, Product-Dämpfung [synthetisch], SKOS-Vorher/Nachher, binär-vs-n-är, GSAS-Abdeckungslücke) | 2026-09-13 |
| Szenario-3-Korrektur | Headline-Operator von Einstein auf Gödel geändert (allgemeiner 3-är-Default laut `amt-engine`-Ontology-README); alle 5 Abbildungen + README neu | 2026-09-13 |

### A5 Was in welchem Chat hochgeladen wird

Das Repo ist klein und ohne große Binärdateien; ein volles ZIP ist praktikabel.
Für die nächste Szenario-Sitzung: dieses `PRIMER.md` hochladen, optional den
aktuellen Repo-Stand als ZIP (ohne `.git/`, `.venv/`, `__pycache__/` — `img/`
kann mit, ist aber klein genug, dass es keine Rolle spielt).

## Teil B — Schrittübersicht

| Schritt | Szenario | Status |
|---|---|---|
| S0 | Repo-Skelett + Entscheidungen | erledigt 2026-09-13 |
| S1 | Symmetrische/transitive Graderweiterung (`amt:InverseAxiom`) | erledigt 2026-09-13 |
| S2 | GSAS als Kalibrierungsschicht (Embedding → Degree of Connection) | erledigt 2026-09-13 |
| S3 | CIDOC-CRM-Klassenschluss über Backbone-Thesaurus/Pactols | erledigt 2026-09-13 |
| S4 | Neuro-symbolischer Recommender (Ausblick) | erledigt 2026-09-13 |
| S5 | Kleiner Test: Embedding-Distanzen direkt in AMT | erledigt 2026-09-13 |
| S6 | Mehrstufige RoleChainAxioms mit GSAS über gemischte Property-Hierarchien | erledigt 2026-09-13 |

## Teil C — Die Schritte

### S0 — Repo-Skelett + Entscheidungen (erledigt 2026-09-13)

- **Ziel**: Leeres GitHub-Repo mit Skelett befüllen: `main.py`,
  `py/viz_utils.py`, `README.md`, `LICENSE`, `CITATION.cff`,
  `requirements.txt`, `.gitignore`, `PRIMER.md`.
- **Substanz**: `viz_utils.py` mit Florians sechs Farbschema-Kategorien plus
  einer expliziten siebten Neutral-Kategorie für Nicht-RDF-Boxen; jede Figur
  wird als `build(canvas)`-Funktion einmal definiert und deterministisch
  gegen zwei Canvas-Backends ausgeführt (`SVGCanvas`, `PNGCanvas` via reinem
  Pillow) — ursprünglich über `cairosvg`, nach dem Windows-Befund oben
  umgebaut.
- **Abnahme**: `python main.py --list` zeigt die Schritte; `python main.py`
  läuft ohne Fehler durch.

### S1 — Symmetrische/transitive Graderweiterung (erledigt 2026-09-13)

- **Ziel**: Zeigen, wie `amt:InverseAxiom` das erledigt, was ursprünglich als
  Handscript geplant war (`a exactMatch b` → `b exactMatch a`, dasselbe für
  `relatedMatch`).
- **Uploads/Daten**: `data/example_mappings.sssom.tsv` — zwei echte,
  unveränderte Zeilen aus `thesaurusscience` (siehe A1); `data/corpus_scale.tsv`
  — echte Zählung über 4 Selbstabbildungs-Dateien (nachgetragen, s. u.).
- **Substanz**: fünf Abbildungen (nachträglich von 2 auf 5 erweitert) —
  1. `scenario-01-inverse-closure.svg/png`: Vorher/Nachher-Netzwerk (2 Paare,
     Vorher nur Hinkante, Nachher zusätzlich gespiegelte, gestrichelte
     Rückkante mit `amt:InverseAxiom`-Beschriftung).
  2. `scenario-01-data-flow.svg/png`: Pipeline SSSOM-TSV → RDF-Quadrupel →
     `amt:InverseAxiom` (SHACL-validiert) → gespiegeltes Quadrupel → neue
     TSV-Zeile.
  3. `scenario-01-corpus-scale.svg/png`: echte Zählung — 9.822/9.831 (99,9 %)
     symmetrische Zeilen ohne Inverse, über 4 Dateien.
  4. `scenario-01-idempotence.svg/png`: zweimaliger Lauf, zweiter Lauf ändert
     nichts (Fixpunkt nach einem Durchlauf erreicht).
  5. `scenario-01-axiom-contrast.svg/png`: `InverseAxiom` (Kopie, kein
     Operator) vs. `RoleChainAxiom` (Komposition, Operator nötig).
- **Abnahme**: `python main.py --only scenario-01` erzeugt alle fünf
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`).

### S2 — GSAS als Kalibrierungsschicht (erledigt 2026-09-13)

- **Ziel**: Zeigen, wie GSAS eine (hier platzhalterhafte) Embedding-
  Ähnlichkeit in einen begründeten, AMT-tauglichen Degree übersetzt, und wie
  unterschiedlich die drei Modelle (Minimal/7-Star/Perceptions) dieselbe
  Evidenz einschätzen.
- **Uploads/Daten**: `data/example_concepts.tsv` (echtes, ungemapptes
  "clay"/"terracotta"-Paar + Platzhalter-Cosinus 0.78);
  `data/gsas_reference_values.tsv` (echte, unveränderte Degree-Tabellen aus
  dem GSAS-Repo selbst, inkl. nachgetragenem 4-Level-Modell, siehe A1).
- **Substanz**: fünf Abbildungen (nachträglich von 3 auf 5 erweitert) —
  1. `scenario-02-calibration-curves.svg/png`: alle drei Modelle auf einer
     gemeinsamen `[0,1]`-Achse (7-Star und Perceptions als – für diese
     Abbildung vereinfachte – kontinuierliche Kurven inkl. aller echten
     Stützpunkte; Minimal als drei feste Referenzlinien).
  2. `scenario-02-pipeline.svg/png`: konkretes Beispiel mit diskreter
     Bindung auf Stern 6 → `skos:closeMatch`, `degree_of_connection = 0.9381`.
  3. `scenario-02-model-comparison.svg/png`: gleicher Platzhalter-Input,
     Balkendiagramm über alle drei Modelle (Minimal=7-Star=0.938,
     Perceptions=0.8 — sichtbar unterschiedlich).
  4. `scenario-02-four-level.svg/png`: das 4-Level-Modell (echte Werte:
     dubious=0.164, low=0.647, medium=0.852, high=0.969) — bislang in
     keiner Abbildung gezeigt.
  5. `scenario-02-model-selection-guide.svg/png`: welches der vier Modelle
     zu welcher Situation passt, paraphrasiert aus dem GSAS-Paper selbst.
- **Abnahme**: `python main.py --only scenario-02` erzeugt alle fünf
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`); Konsolen-Ausgabe
  bestätigt die berechneten Werte.
- **Hinweis**: erster Entwurf zur Vorlage an Lasse Mempel, nicht final.

### S3 — CIDOC-CRM-Klassenschluss (erledigt 2026-09-13)

- **Ziel**: Lasses Beobachtung (Backbone/Pactols sind CIDOC-orientiert)
  konkret als AMT-Rollenkette umsetzen, nachdem die ursprüngliche
  "Subsumption"-Skizze korrigiert wurde (s. A1).
- **Uploads/Daten**: `data/example_chain.tsv` (echte 2-Hop-Kette
  Artefact→goods and commodities→mobile objects, plus illustrative
  `hasCRMClass`-Annotation); `data/fanin_concepts.tsv` (3 weitere echte
  Konzepte, gleicher Anker).
- **Substanz**: fünf Abbildungen (auf Wunsch von ursprünglich 2 auf 5
  erweitert) —
  1. `scenario-03-network`: die Kernkette als Netzwerk, inkl. abgeleiteter
     gestrichelter Kante (Gödel, w=0.900).
  2. `scenario-03-pipeline`: drei asserted Quads → `RoleChainAxiom` →
     inferred Quad.
  3. `scenario-03-operator-comparison`: alle 6 AMT-Operatoren im Vergleich,
     Gödel hervorgehoben.
  4. `scenario-03-fanin`: drei echte Konzepte, ein Anker, eine Klasse "at
     scale".
  5. `scenario-03-before-after`: Vorher/Nachher-Zusammenfassung.
- **Abnahme**: `python main.py --only scenario-03` erzeugt alle fünf
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`); Konsolen-Ausgabe
  bestätigt alle 6 Operator-Werte.
- **Korrektur 2026-09-13** (nach Bau von Szenario 6): Headline-Operator von
  Einstein auf Gödel umgestellt — `amt-engine`s Ontology-README nennt Gödel
  als allgemeinen 3-är-Default, Einstein war nur für eine bestimmte
  heterogene Kette im Beispielfile begründet, nicht allgemein. Alle 5
  Abbildungen neu gebaut und erneut byte-identisch verifiziert.
- **Hinweis**: wie S1/S2 ein erster Entwurf zur Vorlage an Lasse Mempel.

### S4 — Neuro-symbolischer Recommender / Ausblick (erledigt 2026-09-13)

- **Ziel**: Lasses "Endgame"-Idee (Embedding-Ähnlichkeit + AMT-
  Graph-Plausibilität fusioniert zu einem Ranking-Score) konkret an einem
  Beispiel zeigen, ausdrücklich als Ausblick, nicht als gebautes System.
- **Uploads/Daten**: `data/candidates.tsv` — ein echtes Quellkonzept ohne
  starkes Mapping, vier echte Kandidatenkonzepte mit echtem In-Degree als
  Symbolik-Stellvertreter, illustrativer Cosinus als neuronales Signal.
- **Substanz**: fünf Abbildungen —
  1. `scenario-04-architecture`: zwei Signalpfade → Fusionsoperator →
     Ranking.
  2. `scenario-04-ranking`: gruppiertes Balkendiagramm, alle 4 Kandidaten,
     neuronal/symbolisch/fusioniert.
  3. `scenario-04-quadrant`: neuronal vs. symbolisch als Streudiagramm —
     zeigt visuell, warum "CLAY PIPE KILN" trotz höchstem neuronalen Wert
     verliert.
  4. `scenario-04-operator-robustness`: 3 Operatoren, gleicher Gewinner
     ("kilns") bei allen dreien.
  5. `scenario-04-before-after`: Neuronal-only-Ranking vs. fusioniertes
     Ranking nebeneinander.
- **Abnahme**: `python main.py --only scenario-04` erzeugt alle fünf
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`); Konsolen-Ausgabe
  bestätigt alle Werte.
- **Hinweis**: wie S1–S3 ein erster Entwurf zur Vorlage an Lasse Mempel;
  explizit als Ausblick markiert, kein implementierter Recommender.

### S5 — Kleiner Test: Embedding-Distanzen direkt in AMT (erledigt 2026-09-13)

- **Ziel**: Lasses eigenen Vorschlag konkret durchrechnen — was passiert,
  wenn man AMT statt eines GSAS-kalibrierten Gewichts direkt einen rohen
  (illustrativen) Embedding-Ähnlichkeitswert füttert.
- **Uploads/Daten**: `data/chain_variants.tsv` — dieselbe echte Kette wie
  Szenario 3, mit einem zweiten, illustrativen Gewicht für die
  closeMatch-Kante.
- **Substanz**: fünf Abbildungen —
  1. `scenario-05-chain`: die Kette mit beiden Gewicht-Varianten an
     derselben Kante.
  2. `scenario-05-heatmap`: 2×6-Raster (Eingabebedingung × Operator).
  3. `scenario-05-headline-comparison`: beide Bedingungen unter Einstein
     Product allein.
  4. `scenario-05-sensitivity-spread`: Min-Max-Spannweite je Bedingung als
     Dumbbell-Diagramm.
  5. `scenario-05-takeaway`: das Ergebnis in einem Satz.
- **Abnahme**: `python main.py --only scenario-05` erzeugt alle fünf
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`); Konsolen-Ausgabe
  bestätigt alle Werte inkl. Spannweiten.
- **Ergebnis**: Spannweite über alle 6 Operatoren ist beim rohen
  Embedding-Gewicht ~2,7× breiter als beim GSAS-kalibrierten (s. A1).
- **Hinweis**: wie S1–S4 ein erster Entwurf zur Vorlage an Lasse Mempel.

### S6 — Mehrstufige RoleChainAxioms über Property-Hierarchien (erledigt 2026-09-13)

- **Ziel**: zeigen, wie `amt:RoleChainAxiom` genau die Verkettung
  ermöglicht, die SKOS selbst bewusst nicht erlaubt (nur `exactMatch` ist
  transitiv), an mehreren echten, mehrstufigen Ketten mit gemischten
  Properties über mehrere Vokabulare.
- **Uploads/Daten**: `data/real_chains.tsv` — drei echte Ketten (2-är,
  3-är, 4-är), s. A1.
- **Substanz**: acht Abbildungen (auf Wunsch "gerne mehr als 5") —
  1–3. Ketten-Diagramme im n-ary-Stil von `amt-engine`s eigener
     Ontology-README (schwarze Antezedens-Pfeile, ein roter gestrichelter
     Konsequenz-Pfeil).
  4. Operator-Ergebnis je Kette, alle 6 Operatoren im Vergleich.
  5. Synthetischer Beleg (nicht aus echten Daten): Product dämpft ab n=4
     spürbar stärker als Gödel/GeometricMean.
  6. SKOS Vorher/Nachher (was transitiv ist, was AMT ergänzt).
  7. Binär- vs. echt-n-äre Operatoren (Faltung vs. Gesamtliste).
  8. GSAS-Abdeckungslücke (3 von 5 Mapping-Properties kalibriert).
- **Abnahme**: `python main.py --only scenario-06` erzeugt alle acht
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`); Konsolen-Ausgabe
  bestätigt alle Kettengewichte und Operator-Werte.
- **Hinweis**: wie S1–S5 ein erster Entwurf zur Vorlage an Lasse Mempel.

Damit sind alle 6 bislang besprochenen Szenarien gebaut. Weiteres Vorgehen
hängt von Lasses Feedback ab.

## Teil D — Offene Punkte

- ~~Reale Wikidata/SBERT-Cosinuswerte für Szenario 2 berechnen, oder nur
  illustrative Zahlen?~~ Entschieden (s. A4): illustrativer Platzhalter,
  da weder Lasse noch diese Sandbox echte Embeddings zur Verfügung haben.
- `main.py --strict` ist noch nicht implementiert, da noch keine Schritte
  Warnungen erzeugen, die es abfangen könnte — nachholen, sobald relevant.
- ~~Konkrete Beispielkonzepte für Szenario 3 ... noch nicht ausgewählt.~~
  Erledigt (s. A1/A4): echte Kette gefunden und verwendet.
- ~~Beispielkonzepte für Szenario 4 ... noch nicht ausgewählt.~~ Erledigt
  (s. A1/A4): reales Quellkonzept + 4 reale Kandidaten gefunden und
  verwendet.
- ~~Beispielkonzepte für Szenario 5 noch nicht ausgewählt.~~ Erledigt
  (s. A1/A4): dieselbe echte Kette wie Szenario 3 wiederverwendet.
- ~~Szenario 3 nennt Einstein Product noch als "AMT-Empfehlung für
  3er-Ketten".~~ Erledigt 2026-09-13: Headline-Operator auf Gödel
  umgestellt (alle 5 Abbildungen neu gebaut, byte-identisch verifiziert),
  README korrigiert und Korrekturhinweis dort dokumentiert.
- GSAS deckt `broadMatch`/`narrowMatch` nicht ab (s. Szenario 6). Eine
  echte GSAS-Erweiterung dafür existiert nicht; Szenario 6 nutzt eine
  begründete Analogie statt eines Werts.
- Zenodo-DOI für dieses Repo noch nicht vergeben (`CITATION.cff` hat keinen
  `doi`-Eintrag).
- Szenario 1, 2, 3, 4, 5 und 6 sind erste Entwürfe zur Vorlage an Lasse
  Mempel — sobald er Feedback/Ideen dazu hat, ggf. Anpassungen an
  Beispielen, Modellwahl oder Abbildungen nötig; noch nicht eingearbeitet.
- Alle 5 ursprünglich besprochenen Szenarien sind jetzt gebaut. Nächster
  Schritt hängt von Lasses Rückmeldung ab — ggf. Überarbeitung statt neuer
  Szenarien.
