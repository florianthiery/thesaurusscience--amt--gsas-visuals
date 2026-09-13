#!/usr/bin/env python3
"""Build the five figures for scenario-03 (CIDOC-CRM class inference via a
real closeMatch/exactMatch chain into the Backbone Thesaurus, propagated
with AMT's RoleChainAxiom).

Run standalone:
    python scenario-03-cidoc-class-inference/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-03

Reads:
- ../data/example_chain.tsv    - the real 2-hop closeMatch/exactMatch chain
  plus one illustrative hasCRMClass annotation (see that file's header).
- ../data/fanin_concepts.tsv   - three more real concepts that closeMatch the
  same anchor, used for the "at scale" figure.

The six fuzzy-logic aggregation functions below are copied from the actual
amt-engine source (amt/logic.py: _agg_goedel, _agg_product, _agg_lukasiewicz,
_agg_einstein, _agg_geometric_mean, _agg_hamacher / _einstein_pair /
_hamacher_pair), not re-derived - including the exact fold-based
implementation, so the numbers here are what amt-engine itself would compute
for these inputs.

Writes img/scenario-03-network.{svg,png}, img/scenario-03-pipeline.{svg,png},
img/scenario-03-operator-comparison.{svg,png}, img/scenario-03-fanin.{svg,png}
and img/scenario-03-before-after.{svg,png}.
"""

from __future__ import annotations

import csv
import sys
from functools import reduce
from math import prod
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCENARIO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "py"))

from viz_utils import (  # noqa: E402
    Colours,
    arrow,
    box,
    edge_chip,
    elbow,
    oval,
    rect_shape,
    text_block,
    write_outputs,
)

DATA_DIR = SCENARIO_ROOT / "data"
IMG_DIR = SCENARIO_ROOT / "img"


# ---------------------------------------------------------------------------
# AMT's six fuzzy-logic operators, copied from amt/logic.py (see docstring)
# ---------------------------------------------------------------------------
def _einstein_pair(x: float, y: float) -> float:
    d = 2.0 - (x + y - x * y)
    return (x * y) / d if d else 0.0


def _hamacher_pair(x: float, y: float, gamma: float) -> float:
    d = gamma + (1.0 - gamma) * (x + y - x * y)
    return (x * y) / d if d else 0.0


OPERATORS = {
    "Goedel": lambda w: min(w),
    "Product": lambda w: prod(w),
    "Lukasiewicz": lambda w: max(sum(w) - (len(w) - 1), 0.0),
    "Einstein": lambda w: reduce(_einstein_pair, w),
    "GeometricMean": lambda w: prod(w) ** (1.0 / len(w)),
    "Hamacher (g=2)": lambda w: reduce(lambda a, b: _hamacher_pair(a, b, 2.0), w),
}

# AMT's own worked example (examples/skos-mapping-example.ttl) recommends
# Einstein product specifically for 3-step chains ("gentler than
# ProductLogic for n=3, keeping more signal") - used as the headline number
# in figures 1, 2 and 4. Figure 3 shows the full spread across all six.
HEADLINE_OPERATOR = "Einstein"


def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


CHAIN = load_tsv(DATA_DIR / "example_chain.tsv")
FANIN = load_tsv(DATA_DIR / "fanin_concepts.tsv")

W_CLOSE = float(CHAIN[0]["weight"])       # 0.9381 (GSAS minimal, closeMatch)
W_EXACT = float(CHAIN[1]["weight"])       # 1.0    (GSAS minimal, exactMatch)
W_CLASS = float(CHAIN[2]["weight"])       # 0.90   (illustrative)
CHAIN_WEIGHTS = [W_CLOSE, W_EXACT, W_CLASS]

HEADLINE_DEGREE = OPERATORS[HEADLINE_OPERATOR](CHAIN_WEIGHTS)

CRM_CLASS_STYLE = Colours.CLASS  # orange - this IS a CIDOC-CRM class node


# ---------------------------------------------------------------------------
# Figure 1: core chain network
# ---------------------------------------------------------------------------
def build_network(canvas) -> None:
    y = 140
    xs = [110, 430, 750, 1070]
    node_rx, node_ry = 130, 42

    labels = [
        ("Artefact", CHAIN[0]["subject_id"]),
        ("goods and commodities", CHAIN[0]["object_id"]),
        ("mobile objects", CHAIN[1]["object_id"]),
    ]
    for x, (label, cid) in zip(xs[:3], labels):
        oval(canvas, x, y, node_rx, node_ry, label, Colours.SUBJECT_OBJECT,
             sub_label=cid)

    box(canvas, xs[3] - 120, y - 42, 240, 84, "crm:E22_Human-Made_Object",
        CRM_CLASS_STYLE, sub_label="(illustrative annotation)", font_size=13)

    arrow(canvas, xs[0] + node_rx, y, xs[1] - node_rx, y)
    edge_chip(canvas, (xs[0] + xs[1]) / 2, y - 30, "closeMatch",
              f"w = {W_CLOSE:.3f} (GSAS)")

    arrow(canvas, xs[1] + node_rx, y, xs[2] - node_rx, y)
    edge_chip(canvas, (xs[1] + xs[2]) / 2, y - 30, "exactMatch",
              f"w = {W_EXACT:.2f} (GSAS)")

    arrow(canvas, xs[2] + node_rx, y, xs[3] - 120, y)
    edge_chip(canvas, (xs[2] + xs[3]) / 2 - 15, y - 30, "hasCRMClass",
              f"w = {W_CLASS:.2f} (illustrative)")

    # Inferred edge: Artefact -> CIDOC class, arcing below the main row
    inferred_y = y + 150
    elbow(canvas, [(xs[0], y + node_ry), (xs[0], inferred_y),
                   (xs[3], inferred_y), (xs[3], y + 44)],
          dashed=True, colour="#b45309")
    edge_chip(canvas, (xs[0] + xs[3]) / 2, inferred_y + 30,
              f"inferred hasCRMClass (RoleChainAxiom, {HEADLINE_OPERATOR})",
              f"w = {HEADLINE_DEGREE:.3f}", dashed=True, width=430)

    canvas.text((xs[0] + xs[3]) / 2, 40,
                "Real chain (closeMatch, exactMatch) into an illustrative "
                "CIDOC-CRM class annotation", "#0f172a", font_size=15,
                weight="600")


# ---------------------------------------------------------------------------
# Figure 2: RDF/AMT pipeline
# ---------------------------------------------------------------------------
def build_pipeline(canvas) -> None:
    box_w, box_h = 250, 100
    y1, y2 = 40, 200
    gap = 40

    quads = [
        ("Asserted quad 1", "Artefact closeMatch\ngoods and commodities",
         f"w = {W_CLOSE:.3f}", Colours.OWL),
        ("Asserted quad 2", "goods and commodities\nexactMatch mobile objects",
         f"w = {W_EXACT:.2f}", Colours.OWL),
        ("Asserted quad 3", "mobile objects hasCRMClass\ncrm:E22_Human-Made_Object",
         f"w = {W_CLASS:.2f} (illustrative)", Colours.PROP_META),
    ]
    xs = [70, 70 + box_w + gap, 70 + 2 * (box_w + gap)]
    for x, (title, body, w, style) in zip(xs, quads):
        rect_shape(canvas, x, y1, box_w, box_h, style)
        lines = [title] + body.split("\n") + [w]
        for i, line in enumerate(lines):
            weight = "600" if i == 0 else "normal"
            canvas.text(x + box_w / 2, y1 + 24 + i * 18, line, style["text"],
                        font_size=12.5 if i == 0 else 10.5, weight=weight)

    axiom_x = xs[1] - 40
    axiom_y = y2
    axiom_w = box_w + 80
    rect_shape(canvas, axiom_x, axiom_y, axiom_w, 130, Colours.PROP_META)
    canvas.text(axiom_x + axiom_w / 2, axiom_y + 24, "amt:RoleChainAxiom",
                Colours.PROP_META["text"], font_size=13, weight="600")
    for i, line in enumerate([
        "antecedents = (closeMatch,", "exactMatch, hasCRMClass)",
        "consequent = hasCRMClass", f"logic = {HEADLINE_OPERATOR}Product"
        if HEADLINE_OPERATOR == "Einstein" else f"logic = {HEADLINE_OPERATOR}",
    ]):
        canvas.text(axiom_x + axiom_w / 2, axiom_y + 52 + i * 18, line,
                    "#0f172a", font_size=10.5)

    for x in xs:
        arrow(canvas, x + box_w / 2, y1 + box_h, axiom_x + axiom_w / 2, axiom_y)

    out_x = axiom_x + axiom_w + gap + 40
    rect_shape(canvas, out_x, axiom_y - 15, 300, 160, Colours.REAL_OBJECT)
    canvas.text(out_x + 150, axiom_y + 12, "Inferred quad",
                Colours.REAL_OBJECT["text"], font_size=13, weight="600")
    for i, line in enumerate([
        "Artefact hasCRMClass", "crm:E22_Human-Made_Object",
        f"w = {HEADLINE_DEGREE:.3f}", "(SHACL-validated,",
        "provenance = this axiom)",
    ]):
        canvas.text(out_x + 150, axiom_y + 40 + i * 17, line, "#ffffff",
                    font_size=10.5)
    arrow(canvas, axiom_x + axiom_w, axiom_y + 65, out_x, axiom_y + 65)


# ---------------------------------------------------------------------------
# Figure 3: operator comparison bar chart
# ---------------------------------------------------------------------------
def build_operator_comparison(canvas) -> None:
    x0, y0, w, h = 110, 70, 900, 340
    canvas.text(x0 + w / 2, 30,
                f"Same 3-link chain (w = {W_CLOSE:.3f}, {W_EXACT:.2f}, "
                f"{W_CLASS:.2f}), all six AMT operators", "#0f172a",
                font_size=15, weight="600")

    canvas.line(x0, y0 + h, x0 + w, y0 + h, colour="#94a3b8", width=1.3,
                arrow=False)
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    for yt in (0, 0.25, 0.5, 0.75, 1.0):
        py = y0 + h - yt * h
        canvas.line(x0 - 6, py, x0, py, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 14, py, f"{yt:g}", "#475569", font_size=10.5,
                    anchor="end")
    canvas.text(x0, y0 - 16, "degree of connection", "#334155", font_size=12,
                anchor="start")

    names = list(OPERATORS.keys())
    values = [OPERATORS[n](CHAIN_WEIGHTS) for n in names]
    n = len(names)
    bar_w = 90
    gap = (w - n * bar_w) / (n + 1)
    for i, (name, value) in enumerate(zip(names, values)):
        bx = x0 + gap + i * (bar_w + gap)
        bar_h = value * h
        by = y0 + h - bar_h
        style = Colours.PROP_META if name != HEADLINE_OPERATOR else Colours.CLASS
        box(canvas, bx, by, bar_w, bar_h, "", style, rx=5)
        canvas.text(bx + bar_w / 2, by - 14, f"{value:.3f}", "#0f172a",
                    font_size=12, weight="600")
        canvas.text(bx + bar_w / 2, y0 + h + 20, name, "#0f172a",
                    font_size=10.5, weight="600")

    canvas.text(x0 + w / 2, y0 + h + 56,
                f"{HEADLINE_OPERATOR} highlighted: AMT's own worked example "
                "recommends it for 3-step chains. Einstein and Hamacher "
                "(g=2) coincide exactly here - a real mathematical identity, "
                "not a rounding artefact.", "#475569", font_size=11)


# ---------------------------------------------------------------------------
# Figure 4: fan-in at scale
# ---------------------------------------------------------------------------
def build_fanin(canvas) -> None:
    canvas.text(660, 34,
                "Three real concepts, one shared anchor, one inferred class "
                "- no new mappings needed", "#0f172a", font_size=15,
                weight="600")

    left_x = 140
    ys = [110, 230, 350]
    node_rx, node_ry = 150, 38
    for y, row in zip(ys, FANIN):
        oval(canvas, left_x, y, node_rx, node_ry, row["subject_label"],
             Colours.SUBJECT_OBJECT, sub_label=row["subject_id"])

    anchor_x = 560
    anchor_y = 230
    oval(canvas, anchor_x, anchor_y, 150, 42, "goods and commodities",
         Colours.SUBJECT_OBJECT, sub_label="= mobile objects (Backbone)")

    for y in ys:
        arrow(canvas, left_x + node_rx, y, anchor_x - 150, anchor_y)
    edge_chip(canvas, (left_x + anchor_x) / 2 + 40, 190, "closeMatch (all 3)",
              f"w = {W_CLOSE:.3f}")

    class_x = 1000
    box(canvas, class_x - 120, anchor_y - 42, 240, 84,
        "crm:E22_Human-Made_Object", CRM_CLASS_STYLE,
        sub_label="(illustrative annotation)", font_size=13)
    arrow(canvas, anchor_x + 150, anchor_y, class_x - 120, anchor_y)
    edge_chip(canvas, (anchor_x + class_x) / 2 + 20, anchor_y - 60,
              "exactMatch + hasCRMClass", f"w = {W_EXACT * W_CLASS:.3f}*")

    # Dashed "inferred" connectors: leave each source oval from its own
    # right edge, drop straight down to a shared baseline well clear of
    # every node (nothing else occupies y=440-470), then across and up into
    # the class box - never crossing the anchor oval or its arrows.
    baseline_y = 445
    for y in ys:
        elbow(canvas,
              [(left_x + node_rx, y), (left_x + node_rx, baseline_y),
               (class_x, baseline_y), (class_x, anchor_y + 42)],
              dashed=True, colour="#b45309")

    canvas.text(660, 500,
                f"All three inherit the same class via amt:RoleChainAxiom, "
                f"each with w = {HEADLINE_DEGREE:.3f} ({HEADLINE_OPERATOR} "
                "product) - one axiom, applied once, covers every concept "
                "that ever closeMatches this anchor.", "#475569",
                font_size=11.5)
    canvas.text(660, 522,
                "* product of the two real GSAS weights only, before the "
                "third (illustrative) step - see the scenario README.",
                "#94a3b8", font_size=10)


# ---------------------------------------------------------------------------
# Figure 5: before / after summary
# ---------------------------------------------------------------------------
def build_before_after(canvas) -> None:
    node_rx, node_ry = 140, 36
    ys = [90, 190, 290]

    canvas.text(280, 34, "Before", "#0f172a", font_size=17, weight="600")
    canvas.text(920, 34, "After", "#0f172a", font_size=17, weight="600")
    canvas.line(600, 55, 600, 380, colour="#cbd5e1", width=1.5, dashed=True,
                arrow=False)

    for y, row in zip(ys, FANIN):
        oval(canvas, 280, y, node_rx, node_ry, row["subject_label"],
             Colours.SUBJECT_OBJECT, font_size=12)
    canvas.text(280, 350, "3 concepts, no shared class", "#475569",
                font_size=11.5)

    for y, row in zip(ys, FANIN):
        oval(canvas, 800, y, node_rx, node_ry, row["subject_label"],
             Colours.SUBJECT_OBJECT, font_size=12)
    box(canvas, 1020, 150, 220, 80, "crm:E22_Human-Made_Object",
        CRM_CLASS_STYLE, font_size=12)
    for y in ys:
        arrow(canvas, 800 + node_rx, y, 1020, 190, dashed=True,
              colour="#b45309")
    canvas.text(910, 350,
        f"3 concepts, 1 shared class (w~{HEADLINE_DEGREE:.2f}, 1 axiom)",
        "#475569", font_size=11.5)


def main() -> None:
    write_outputs(build_network, IMG_DIR, "scenario-03-network",
                  width=1280, height=420)
    write_outputs(build_pipeline, IMG_DIR, "scenario-03-pipeline",
                  width=1200, height=380)
    write_outputs(build_operator_comparison, IMG_DIR,
                  "scenario-03-operator-comparison", width=1080, height=520)
    write_outputs(build_fanin, IMG_DIR, "scenario-03-fanin",
                  width=1320, height=560)
    write_outputs(build_before_after, IMG_DIR, "scenario-03-before-after",
                  width=1280, height=420)

    print(f"Wrote figures to {IMG_DIR}")
    print("Chain weights:", CHAIN_WEIGHTS)
    for name in OPERATORS:
        print(f"  {name:18s} {OPERATORS[name](CHAIN_WEIGHTS):.6f}")


if __name__ == "__main__":
    main()
