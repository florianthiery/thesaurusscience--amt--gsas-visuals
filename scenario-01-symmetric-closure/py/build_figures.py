#!/usr/bin/env python3
"""Build the two figures for scenario-01 (symmetric/transitive closure via
AMT's amt:InverseAxiom).

Run standalone:
    python scenario-01-symmetric-closure/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-01

Reads the two-row example in ../data/example_mappings.sssom.tsv (a real,
attributed excerpt from thesaurusscience - see that file's header) and writes
img/scenario-01-inverse-closure.{svg,png} and
img/scenario-01-data-flow.{svg,png}.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py"))

from viz_utils import (  # noqa: E402
    Colours,
    arrow,
    box,
    edge_chip,
    oval,
    rect_shape,
    text_block,
    write_outputs,
)

IMG_DIR = SCENARIO_ROOT / "img"
DATA_DIR = SCENARIO_ROOT / "data"


def load_corpus_scale() -> list[dict]:
    with (DATA_DIR / "corpus_scale.tsv").open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    data = list(csv.DictReader(rows, delimiter="\t"))
    for r in data:
        r["symmetric_rows"] = int(r["symmetric_rows"])
        r["rows_missing_inverse"] = int(r["rows_missing_inverse"])
        r["rows_with_inverse"] = int(r["rows_with_inverse"])
    return data


CORPUS_SCALE = load_corpus_scale()
TOTAL_SYMMETRIC = sum(r["symmetric_rows"] for r in CORPUS_SCALE)
TOTAL_MISSING = sum(r["rows_missing_inverse"] for r in CORPUS_SCALE)


# ---------------------------------------------------------------------------
# Figure 1: before / after inverse-closure network
# ---------------------------------------------------------------------------
def build_inverse_closure(canvas) -> None:
    node_rx, node_ry = 115, 44

    def panel(panel_x, show_inverse):
        left_cx, right_cx = panel_x + 130, panel_x + 400
        pair_a_cy, pair_b_cy = 130, 370

        # Pair A: aat:300010439 -[exactMatch]-> oeai-materials:concept23906 "clay"
        oval(canvas, left_cx, pair_a_cy, node_rx, node_ry, "aat:300010439",
             Colours.SUBJECT_OBJECT, sub_label="(no label in source)")
        oval(canvas, right_cx, pair_a_cy, node_rx, node_ry, "",
             Colours.SUBJECT_OBJECT,
             lines=[("oeai-materials:", "normal", 11),
                    ("concept23906", "600", 13),
                    ('"clay"', "normal", 11)])
        arrow(canvas, left_cx + node_rx, pair_a_cy, right_cx - node_rx, pair_a_cy)
        edge_chip(canvas, (left_cx + right_cx) / 2, pair_a_cy - 30,
                  "exactMatch", "w = 1.00")
        if show_inverse:
            arrow(canvas, right_cx - node_rx, pair_a_cy + 20,
                  left_cx + node_rx, pair_a_cy + 20, dashed=True,
                  colour="#b45309")
            edge_chip(canvas, (left_cx + right_cx) / 2, pair_a_cy + 62,
                      "exactMatch (inverse)", "w = 1.00", dashed=True)

        # Pair B: wnk:wk000147 "summerhouse" -[relatedMatch]-> aat:300007698
        oval(canvas, left_cx, pair_b_cy, node_rx, node_ry, "wnk:wk000147",
             Colours.SUBJECT_OBJECT, sub_label='"summerhouse"')
        oval(canvas, right_cx, pair_b_cy, node_rx, node_ry, "aat:300007698",
             Colours.SUBJECT_OBJECT, sub_label="(no label in source)")
        arrow(canvas, left_cx + node_rx, pair_b_cy, right_cx - node_rx, pair_b_cy)
        edge_chip(canvas, (left_cx + right_cx) / 2, pair_b_cy - 30,
                  "relatedMatch", "w = 0.60")
        if show_inverse:
            arrow(canvas, right_cx - node_rx, pair_b_cy + 20,
                  left_cx + node_rx, pair_b_cy + 20, dashed=True,
                  colour="#b45309")
            edge_chip(canvas, (left_cx + right_cx) / 2, pair_b_cy + 62,
                      "relatedMatch (inverse)", "w = 0.60", dashed=True)

    panel_x_before, panel_x_after = 20, 590
    divider_x = 565

    # Plain hyphen, not an em dash: Pillow's built-in default font (used for
    # the PNG backend) has no glyph for U+2014 and silently draws a "tofu"
    # box instead - discovered when reviewing the first Pillow-rendered PNG.
    canvas.text(panel_x_before + 265, 34, "Before - source graph",
                "#0f172a", font_size=18, weight="600")
    canvas.text(panel_x_after + 265, 34,
                "After - + amt:InverseAxiom closure", "#0f172a",
                font_size=18, weight="600")

    panel(panel_x_before, show_inverse=False)
    panel(panel_x_after, show_inverse=True)

    canvas.line(divider_x, 55, divider_x, 500, colour="#cbd5e1", width=1.5,
                dashed=True, arrow=False)

    # Legend
    legend_y = 525
    canvas.ellipse(55, legend_y, 34, 14, Colours.SUBJECT_OBJECT)
    canvas.text(100, legend_y + 4, "skos:Concept individual", "#0f172a",
                font_size=12, anchor="start")
    edge_chip(canvas, 360, legend_y, "predicate", width=84, height=20)
    canvas.text(415, legend_y + 4, "predicate + amt:weight", "#0f172a",
                font_size=12, anchor="start")
    canvas.line(640, legend_y, 682, legend_y, colour="#b45309", width=1.8,
                dashed=True, arrow=True)
    canvas.text(695, legend_y + 4, "added by amt:InverseAxiom", "#0f172a",
                font_size=12, anchor="start")


# ---------------------------------------------------------------------------
# Figure 2: data-flow pipeline
# ---------------------------------------------------------------------------
def build_data_flow(canvas) -> None:
    box_w, box_h = 215, 130
    y = 60
    gap = 35
    n = 5
    width = canvas.width
    total_w = n * box_w + (n - 1) * gap
    start_x = (width - total_w) / 2

    steps = [
        ([("SSSOM TSV row", "600", 14),
          ("subject_id / predicate_id /", "normal", 11),
          ("object_id", "normal", 11),
          ("(thesaurusscience)", "normal", 11)],
         Colours.NEUTRAL_PROCESS),
        ([("RDF quad", "600", 14),
          ("rdf:subject / predicate /", "normal", 11),
          ("object + amt:weight", "normal", 11)],
         Colours.OWL),
        ([("amt:InverseAxiom", "600", 14),
          ("antecedent = inverse", "normal", 11),
          ("= predicate", "normal", 11),
          ("(SHACL-validated)", "normal", 11)],
         Colours.PROP_META),
        ([("Mirrored RDF quad", "600", 14),
          ("inverse edge,", "normal", 11),
          ("same amt:weight", "normal", 11)],
         Colours.OWL),
        ([("New TSV row", "600", 14),
          ("-> back into thesaurusscience /", "normal", 11),
          ("Cocoda concordance", "normal", 11)],
         Colours.NEUTRAL_PROCESS),
    ]

    from viz_utils import rect_shape, text_block  # local import, avoids
    # widening the module-level import list above just for these two

    xs = [start_x + i * (box_w + gap) for i in range(n)]
    for x, (lines, style) in zip(xs, steps):
        cx, cy = x + box_w / 2, y + box_h / 2
        rect_shape(canvas, x, y, box_w, box_h, style)
        text_block(canvas, cx, cy, lines, style["text"], line_height=17)
    for i in range(n - 1):
        x1 = xs[i] + box_w
        x2 = xs[i + 1]
        arrow(canvas, x1, y + box_h / 2, x2, y + box_h / 2)

    canvas.text(
        width / 2, y + box_h + 38,
        "amt-runner ingests the RDF quads and the axiom file, applies "
        "amt:InverseAxiom under SHACL validation, and exports the mirrored "
        "quads back out.", "#475569", font_size=12.5,
    )

    # Legend: which boxes follow Florian's RDF-node colour scheme, which don't
    legend_x = width / 2 - 230
    legend_y0 = y + box_h + 75
    legend_rows = [
        (Colours.OWL, "OWL", "raw RDF construct (subject/predicate/object + weight)"),
        (Colours.PROP_META, "PropMeta", "axiom / property-level construct"),
        (Colours.NEUTRAL_PROCESS, "n/a", "external TSV artefact "
         "(not part of Florian's RDF-node colour scheme)"),
    ]
    for i, (style, chip_label, desc) in enumerate(legend_rows):
        ly = legend_y0 + i * 32
        box(canvas, legend_x, ly, 92, 24, chip_label, style, font_size=11)
        canvas.text(legend_x + 110, ly + 16, desc, "#0f172a", font_size=11.5,
                    anchor="start")


# ---------------------------------------------------------------------------
# Figure 3: corpus-scale finding (real, computed across the corpus)
# ---------------------------------------------------------------------------
def build_corpus_scale(canvas) -> None:
    canvas.text(580, 34,
                "How much of the corpus does this actually affect?",
                "#0f172a", font_size=16, weight="600")

    x0, bar_h, gap = 340, 34, 20
    row_w = 660
    rows = CORPUS_SCALE + [{
        "file": "All four combined",
        "symmetric_rows": TOTAL_SYMMETRIC,
        "rows_missing_inverse": TOTAL_MISSING,
        "rows_with_inverse": TOTAL_SYMMETRIC - TOTAL_MISSING,
    }]
    for i, r in enumerate(rows):
        y = 80 + i * (bar_h + gap)
        total = r["symmetric_rows"]
        missing_w = row_w * (r["rows_missing_inverse"] / total) if total else 0
        has_w = row_w - missing_w
        bold = i == len(rows) - 1
        box(canvas, x0, y, missing_w, bar_h, "", Colours.PROP_META, rx=3)
        if has_w > 2:
            box(canvas, x0 + missing_w, y, has_w, bar_h, "",
                Colours.REAL_OBJECT, rx=3)
        canvas.text(x0 - 20, y + bar_h / 2, r["file"], "#0f172a",
                    font_size=11.5 if not bold else 12.5,
                    weight="600" if bold else "normal", anchor="end")
        pct = 100 * r["rows_missing_inverse"] / total if total else 0
        canvas.text(x0 + row_w + 20, y + bar_h / 2,
                    f'{r["rows_missing_inverse"]}/{total} missing ({pct:.1f}%)',
                    "#475569", font_size=11, anchor="start")

    ly = 80 + len(rows) * (bar_h + gap) + 20
    box(canvas, x0, ly, 20, 16, "", Colours.PROP_META, rx=3)
    canvas.text(x0 + 28, ly + 12, "missing inverse", "#0f172a", font_size=11,
                anchor="start")
    box(canvas, x0 + 220, ly, 20, 16, "", Colours.REAL_OBJECT, rx=3)
    canvas.text(x0 + 248, ly + 12, "inverse already present", "#0f172a",
                font_size=11, anchor="start")

    canvas.text(580, ly + 50,
                "Counted across 4 real self-mapping files in thesaurusscience "
                "(every skos:exactMatch/closeMatch/relatedMatch row, since "
                "all three are symmetric in SKOS) - not just the two rows "
                "in the worked example above.", "#475569", font_size=11)


# ---------------------------------------------------------------------------
# Figure 4: idempotence (run twice, stable)
# ---------------------------------------------------------------------------
def build_idempotence(canvas) -> None:
    canvas.text(580, 34, "Running the axiom twice does not duplicate anything",
                "#0f172a", font_size=16, weight="600")

    node_rx, node_ry = 90, 34
    for panel_x, title in [(20, "Run 1 (on the asserted graph)"),
                            (620, "Run 2 (on the already-closed graph)")]:
        canvas.text(panel_x + 260, 70, title, "#0f172a", font_size=12.5,
                    weight="600")
        left_cx, right_cx = panel_x + 110, panel_x + 400
        y = 160
        oval(canvas, left_cx, y, node_rx, node_ry, "aat:300010439",
             Colours.SUBJECT_OBJECT, font_size=11)
        oval(canvas, right_cx, y, node_rx, node_ry, "concept23906",
             Colours.SUBJECT_OBJECT, font_size=11)
        arrow(canvas, left_cx + node_rx, y - 10, right_cx - node_rx, y - 10)
        edge_chip(canvas, (left_cx + right_cx) / 2, y - 40, "exactMatch",
                  "asserted, w=1.00", width=150)
        arrow(canvas, right_cx - node_rx, y + 10, left_cx + node_rx, y + 10,
              dashed=True, colour="#166534")
        edge_chip(canvas, (left_cx + right_cx) / 2, y + 44, "exactMatch",
                  "inferred, w=1.00" if panel_x == 20
                  else "inferred, w=1.00 (unchanged)",
                  style=Colours.REAL_OBJECT, dashed=True, width=190)

    canvas.line(580, 55, 580, 260, colour="#cbd5e1", width=1.5, dashed=True,
                arrow=False)
    caption = [
        "AMT only strengthens edges already marked amt:inferred; it never",
        "overwrites an asserted one (amt/reasoning.py). Since run 1's inferred",
        "edge already carries the maximum weight the axiom would produce,",
        "run 2 changes nothing - the fixed point is reached in one pass here.",
    ]
    for i, line in enumerate(caption):
        canvas.text(580, 300 + i * 18, line, "#475569", font_size=11.5)


# ---------------------------------------------------------------------------
# Figure 5: InverseAxiom vs RoleChainAxiom - why no operator choice here
# ---------------------------------------------------------------------------
def build_axiom_contrast(canvas) -> None:
    canvas.text(610, 34,
                "Why this scenario has no fuzzy-operator choice to make",
                "#0f172a", font_size=16, weight="600")

    col_w = 520
    xs = [60, 60 + col_w + 60]
    titles = ["amt:InverseAxiom (this scenario)", "amt:RoleChainAxiom (scenarios 3 & 5)"]
    bodies = [
        [("One antecedent, one inverse", "600", 12.5),
         ("edge mirrored, weight copied as-is", "normal", 11),
         ("amt:weight(inferred) = amt:weight(asserted)", "normal", 11),
         ("", "normal", 6),
         ("No amt:logic property at all -", "normal", 11),
         ("_apply_inverse() doesn't read one;", "normal", 11),
         ("the mirroring is a copy, not a composition", "normal", 11)],
        [("Two or more antecedents", "600", 12.5),
         ("weights combined along the chain", "normal", 11),
         ("amt:weight(inferred) = op(w1, w2, ...)", "normal", 11),
         ("", "normal", 6),
         ("amt:logic is required -", "normal", 11),
         ("choice of operator changes the result", "normal", 11)],
    ]
    for x, title, body in zip(xs, titles, bodies):
        rect_shape(canvas, x, 70, col_w, 260, Colours.PROP_META)
        canvas.text(x + col_w / 2, 96, title, Colours.PROP_META["text"],
                    font_size=13, weight="600")
        text_block(canvas, x + col_w / 2, 200, body,
                    Colours.PROP_META["text"], line_height=20)

    canvas.text(610, 360,
                "This is why scenario 1's weights are exact copies (w=1.00, "
                "w=0.60) while scenarios 3 and 5 show six different answers "
                "for the same chain - the two axiom types solve different "
                "problems.", "#475569", font_size=11.5)


def main() -> None:
    write_outputs(build_inverse_closure, IMG_DIR, "scenario-01-inverse-closure",
                  width=1160, height=560)
    write_outputs(build_data_flow, IMG_DIR, "scenario-01-data-flow",
                  width=1260, height=430)
    write_outputs(build_corpus_scale, IMG_DIR, "scenario-01-corpus-scale",
                  width=1160, height=440)
    write_outputs(build_idempotence, IMG_DIR, "scenario-01-idempotence",
                  width=1160, height=420)
    write_outputs(build_axiom_contrast, IMG_DIR, "scenario-01-axiom-contrast",
                  width=1220, height=420)
    print(f"Wrote figures to {IMG_DIR}")
    print(f"Corpus scale: {TOTAL_MISSING}/{TOTAL_SYMMETRIC} symmetric rows "
          f"missing an inverse ({100 * TOTAL_MISSING / TOTAL_SYMMETRIC:.1f}%)")


if __name__ == "__main__":
    main()
