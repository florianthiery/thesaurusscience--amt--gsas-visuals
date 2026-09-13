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
| `florianthiery/thesaurusscience--amt--gsas-visuals` | dieses Repo | neu, S0/S1/S2 erledigt |

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
| S3 | CIDOC-CRM-Klassenschluss über Backbone-Thesaurus/Pactols | geplant |
| S4 | Neuro-symbolischer Recommender (Ausblick) | geplant |
| S5 | Kleiner Test: Embedding-Distanzen direkt in AMT | geplant |

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
  unveränderte Zeilen aus `thesaurusscience` (siehe A1).
- **Substanz**: zwei Abbildungen —
  1. `scenario-01-inverse-closure.svg/png`: Vorher/Nachher-Netzwerk (2 Paare,
     Vorher nur Hinkante, Nachher zusätzlich gespiegelte, gestrichelte
     Rückkante mit `amt:InverseAxiom`-Beschriftung).
  2. `scenario-01-data-flow.svg/png`: Pipeline SSSOM-TSV → RDF-Quadrupel →
     `amt:InverseAxiom` (SHACL-validiert) → gespiegeltes Quadrupel → neue
     TSV-Zeile.
- **Abnahme**: `python main.py --only scenario-01` erzeugt beide Abbildungen;
  zweimaliger Lauf ist byte-identisch (`cmp`).

### S2 — GSAS als Kalibrierungsschicht (erledigt 2026-09-13)

- **Ziel**: Zeigen, wie GSAS eine (hier platzhalterhafte) Embedding-
  Ähnlichkeit in einen begründeten, AMT-tauglichen Degree übersetzt, und wie
  unterschiedlich die drei Modelle (Minimal/7-Star/Perceptions) dieselbe
  Evidenz einschätzen.
- **Uploads/Daten**: `data/example_concepts.tsv` (echtes, ungemapptes
  "clay"/"terracotta"-Paar + Platzhalter-Cosinus 0.78);
  `data/gsas_reference_values.tsv` (echte, unveränderte Degree-Tabellen aus
  dem GSAS-Repo selbst, siehe A1).
- **Substanz**: drei Abbildungen —
  1. `scenario-02-calibration-curves.svg/png`: alle drei Modelle auf einer
     gemeinsamen `[0,1]`-Achse (7-Star und Perceptions als – für diese
     Abbildung vereinfachte – kontinuierliche Kurven inkl. aller echten
     Stützpunkte; Minimal als drei feste Referenzlinien).
  2. `scenario-02-pipeline.svg/png`: konkretes Beispiel mit diskreter
     Bindung auf Stern 6 → `skos:closeMatch`, `degree_of_connection = 0.9381`.
  3. `scenario-02-model-comparison.svg/png`: gleicher Platzhalter-Input,
     Balkendiagramm über alle drei Modelle (Minimal=7-Star=0.938,
     Perceptions=0.8 — sichtbar unterschiedlich).
- **Abnahme**: `python main.py --only scenario-02` erzeugt alle drei
  Abbildungen; zweimaliger Lauf ist byte-identisch (`cmp`); Konsolen-Ausgabe
  bestätigt die berechneten Werte.
- **Hinweis**: erster Entwurf zur Vorlage an Lasse Mempel, nicht final.

### S3–S5 — noch nicht im Detail geplant

Wird zu Beginn des jeweiligen Chats besprochen: Beispieldaten aus
`thesaurusscience` auswählen, Anzahl und Art der Abbildungen bestätigen, dann
bauen. Grobe Richtung siehe die Szenario-Beschreibungen im Chat vom
2026-09-13 (Szenario 2: GSAS-Kalibrierungskurven + Pipeline; Szenario 3:
CIDOC-CRM-Netzwerk + Flowchart; Szenario 4: Architektur- + Ranking-Diagramm;
Szenario 5: Ketten- + Operator-Balkendiagramm).

## Teil D — Offene Punkte

- ~~Reale Wikidata/SBERT-Cosinuswerte für Szenario 2 berechnen, oder nur
  illustrative Zahlen?~~ Entschieden (s. A4): illustrativer Platzhalter,
  da weder Lasse noch diese Sandbox echte Embeddings zur Verfügung haben.
- `main.py --strict` ist noch nicht implementiert, da noch keine Schritte
  Warnungen erzeugen, die es abfangen könnte — nachholen, sobald relevant.
- Konkrete Beispielkonzepte für Szenario 3 (CIDOC-CRM-Anker in Backbone
  Thesaurus/Pactols) und Szenario 4/5 noch nicht aus `thesaurusscience`
  ausgewählt.
- Zenodo-DOI für dieses Repo noch nicht vergeben (`CITATION.cff` hat keinen
  `doi`-Eintrag).
- Szenario 1 und 2 sind erste Entwürfe zur Vorlage an Lasse Mempel — sobald
  er Feedback/Ideen dazu hat, ggf. Anpassungen an Beispielen, Modellwahl
  oder Abbildungen nötig; noch nicht eingearbeitet.
