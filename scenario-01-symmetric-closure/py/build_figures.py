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

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py"))

from viz_utils import Colours, arrow, box, edge_chip, oval, write_outputs  # noqa: E402

IMG_DIR = SCENARIO_ROOT / "img"


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


def main() -> None:
    write_outputs(build_inverse_closure, IMG_DIR, "scenario-01-inverse-closure",
                  width=1160, height=560)
    write_outputs(build_data_flow, IMG_DIR, "scenario-01-data-flow",
                  width=1260, height=430)
    print(f"Wrote figures to {IMG_DIR}")


if __name__ == "__main__":
    main()
