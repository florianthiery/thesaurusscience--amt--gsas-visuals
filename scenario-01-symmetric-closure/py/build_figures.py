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

from viz_utils import (  # noqa: E402
    Colours,
    arrow,
    defs_arrowhead,
    edge_chip,
    oval,
    box,
    rect_shape,
    text_block,
    svg_document,
    write_outputs,
)

FONT = "Segoe UI, Helvetica, Arial, sans-serif"

IMG_DIR = SCENARIO_ROOT / "img"


# ---------------------------------------------------------------------------
# Figure 1: before / after inverse-closure network
# ---------------------------------------------------------------------------
def build_inverse_closure() -> str:
    width, height = 1160, 560
    node_rx, node_ry = 115, 44

    def panel(panel_x, show_inverse):
        left_cx, right_cx = panel_x + 130, panel_x + 400
        pair_a_cy, pair_b_cy = 130, 370
        parts = []

        # Pair A: aat:300010439 -[exactMatch]-> oeai-materials:concept23906 "clay"
        parts.append(oval(left_cx, pair_a_cy, node_rx, node_ry,
                           "aat:300010439", Colours.SUBJECT_OBJECT,
                           sub_label="(no label in source)"))
        parts.append(oval(right_cx, pair_a_cy, node_rx, node_ry, "",
                           Colours.SUBJECT_OBJECT,
                           lines=[("oeai-materials:", "normal", 11),
                                  ("concept23906", "600", 13),
                                  ('"clay"', "normal", 11)]))
        parts.append(arrow(left_cx + node_rx, pair_a_cy,
                            right_cx - node_rx, pair_a_cy))
        parts.append(edge_chip((left_cx + right_cx) / 2, pair_a_cy - 30,
                                "exactMatch", "w = 1.00"))
        if show_inverse:
            parts.append(arrow(right_cx - node_rx, pair_a_cy + 20,
                                left_cx + node_rx, pair_a_cy + 20,
                                dashed=True, colour="#b45309"))
            parts.append(edge_chip((left_cx + right_cx) / 2, pair_a_cy + 62,
                                    "exactMatch (inverse)", "w = 1.00",
                                    dashed=True))

        # Pair B: wnk:wk000147 "summerhouse" -[relatedMatch]-> aat:300007698
        parts.append(oval(left_cx, pair_b_cy, node_rx, node_ry,
                           "wnk:wk000147", Colours.SUBJECT_OBJECT,
                           sub_label='"summerhouse"'))
        parts.append(oval(right_cx, pair_b_cy, node_rx, node_ry,
                           "aat:300007698", Colours.SUBJECT_OBJECT,
                           sub_label="(no label in source)"))
        parts.append(arrow(left_cx + node_rx, pair_b_cy,
                            right_cx - node_rx, pair_b_cy))
        parts.append(edge_chip((left_cx + right_cx) / 2, pair_b_cy - 30,
                                "relatedMatch", "w = 0.60"))
        if show_inverse:
            parts.append(arrow(right_cx - node_rx, pair_b_cy + 20,
                                left_cx + node_rx, pair_b_cy + 20,
                                dashed=True, colour="#b45309"))
            parts.append(edge_chip((left_cx + right_cx) / 2, pair_b_cy + 62,
                                    "relatedMatch (inverse)", "w = 0.60",
                                    dashed=True))
        return "\n".join(parts)

    panel_x_before, panel_x_after = 20, 590
    divider_x = 565

    body = []
    body.append(
        f'<text x="{panel_x_before + 265}" y="34" text-anchor="middle" '
        f'font-family="{FONT}" font-size="18" font-weight="700" '
        f'fill="#0f172a">Before &#8212; source graph</text>'
    )
    body.append(
        f'<text x="{panel_x_after + 265}" y="34" text-anchor="middle" '
        f'font-family="{FONT}" font-size="18" font-weight="700" '
        f'fill="#0f172a">After &#8212; + amt:InverseAxiom closure</text>'
    )
    body.append(panel(panel_x_before, show_inverse=False))
    body.append(panel(panel_x_after, show_inverse=True))
    body.append(
        f'<line x1="{divider_x}" y1="55" x2="{divider_x}" y2="500" '
        f'stroke="#cbd5e1" stroke-width="1.5" stroke-dasharray="4,4"/>'
    )

    # Legend (single row, generous spacing so nothing runs off the canvas)
    legend_y = 525
    body.append(
        f'<ellipse cx="55" cy="{legend_y}" rx="34" ry="14" '
        f'fill="{Colours.SUBJECT_OBJECT["fill"]}" '
        f'stroke="{Colours.SUBJECT_OBJECT["stroke"]}" stroke-width="1.5"/>'
    )
    body.append(
        f'<text x="100" y="{legend_y + 4}" font-family="{FONT}" '
        f'font-size="12" fill="#0f172a">skos:Concept individual</text>'
    )
    body.append(edge_chip(360, legend_y, "predicate", width=84, height=20))
    body.append(
        f'<text x="415" y="{legend_y + 4}" font-family="{FONT}" '
        f'font-size="12" fill="#0f172a">predicate + amt:weight</text>'
    )
    body.append(
        f'<line x1="640" y1="{legend_y}" x2="682" y2="{legend_y}" '
        f'stroke="#b45309" stroke-width="1.8" stroke-dasharray="7,5" '
        f'marker-end="url(#arrowhead-amber)"/>'
    )
    body.append(
        f'<text x="695" y="{legend_y + 4}" font-family="{FONT}" '
        f'font-size="12" fill="#0f172a">added by amt:InverseAxiom</text>'
    )

    defs = defs_arrowhead("arrowhead") + defs_arrowhead("arrowhead-amber", "#b45309")
    return svg_document(width, height, "\n".join(body), defs=defs)


# ---------------------------------------------------------------------------
# Figure 2: data-flow pipeline
# ---------------------------------------------------------------------------
def build_data_flow() -> str:
    width, height = 1260, 430
    box_w, box_h = 215, 130
    y = 60
    gap = 35
    n = 5
    total_w = n * box_w + (n - 1) * gap
    start_x = (width - total_w) / 2

    # Each step: (lines-for-text_block, fill/stroke/text style)
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
          ("\u2192 back into thesaurusscience /", "normal", 11),
          ("Cocoda concordance", "normal", 11)],
         Colours.NEUTRAL_PROCESS),
    ]

    body = []
    xs = [start_x + i * (box_w + gap) for i in range(n)]
    for x, (lines, style) in zip(xs, steps):
        cx, cy = x + box_w / 2, y + box_h / 2
        body.append(rect_shape(x, y, box_w, box_h, style))
        body.append(text_block(cx, cy, lines, style["text"], line_height=17))
    for i in range(n - 1):
        x1 = xs[i] + box_w
        x2 = xs[i + 1]
        body.append(arrow(x1, y + box_h / 2, x2, y + box_h / 2))

    body.append(
        f'<text x="{width/2}" y="{y + box_h + 38}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="12.5" fill="#475569">amt-runner '
        f'ingests the RDF quads and the axiom file, applies amt:InverseAxiom '
        f'under SHACL validation, and exports the mirrored quads back out.'
        f'</text>'
    )

    # Legend: which boxes follow Florian's RDF-node colour scheme, which don't
    # (stacked, left-aligned, so nothing has to compete for horizontal space)
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
        body.append(box(legend_x, ly, 92, 24, chip_label, style, font_size=11))
        body.append(
            f'<text x="{legend_x + 110}" y="{ly + 16}" font-family="{FONT}" '
            f'font-size="11.5" fill="#0f172a">{desc}</text>'
        )

    defs = defs_arrowhead("arrowhead")
    return svg_document(width, height, "\n".join(body), defs=defs)


def main() -> None:
    svg1 = build_inverse_closure()
    write_outputs(svg1, IMG_DIR, "scenario-01-inverse-closure")

    svg2 = build_data_flow()
    write_outputs(svg2, IMG_DIR, "scenario-01-data-flow")

    print(f"Wrote figures to {IMG_DIR}")


if __name__ == "__main__":
    main()
