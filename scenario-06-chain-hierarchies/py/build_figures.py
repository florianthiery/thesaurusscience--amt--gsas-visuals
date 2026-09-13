#!/usr/bin/env python3
"""Build the eight figures for scenario-06 (multi-step RoleChainAxioms with
GSAS, reasoning across hierarchies with mixed SKOS mapping properties -
something plain SKOS cannot do on its own).

Run standalone:
    python scenario-06-chain-hierarchies/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-06

Reads ../data/real_chains.tsv - three real, multi-vocabulary chains found in
thesaurusscience, mixing skos:narrowMatch/exactMatch/closeMatch (only
exactMatch is transitive per the SKOS Reference; the others are not, "to
avoid the possibility of compound errors when combining mappings across more
than two concept schemes" - paraphrased from Section 10.1). The six fuzzy
operators are copied from amt/logic.py, as in scenarios 3 and 5.

Chain-diagram figures (1-3) follow AMT's own documented convention from
https://github.com/n4o-rse/amt-engine/blob/main/ontology/README.md: solid
black arrows for asserted antecedent edges, one red dashed arrow for the
inferred consequent.
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

RED = "#dc2626"  # AMT's own convention colour for the inferred consequent arc


# ---------------------------------------------------------------------------
# AMT's six fuzzy-logic operators, copied from amt/logic.py (as in scenario 3/5)
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
# Per AMT's own ontology README table: default recommendation by arity.
RECOMMENDED_BY_ARITY = {2: "Goedel", 3: "Goedel", 4: "GeometricMean"}


def load_chains() -> dict[int, list[dict]]:
    with (DATA_DIR / "real_chains.tsv").open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    data = list(csv.DictReader(rows, delimiter="\t"))
    chains: dict[int, list[dict]] = {}
    for r in data:
        r["chain"] = int(r["chain"])
        r["step"] = int(r["step"])
        r["weight"] = float(r["weight"])
        chains.setdefault(r["chain"], []).append(r)
    for c in chains.values():
        c.sort(key=lambda r: r["step"])
    return chains


CHAINS = load_chains()
CHAIN_WEIGHTS = {cid: [s["weight"] for s in steps] for cid, steps in CHAINS.items()}
CHAIN_RESULTS = {
    cid: {name: fn(w) for name, fn in OPERATORS.items()}
    for cid, w in CHAIN_WEIGHTS.items()
}


# ---------------------------------------------------------------------------
# Generic n-ary chain diagram (AMT's own documented style)
# ---------------------------------------------------------------------------
def draw_chain_diagram(canvas, chain_id: int, consequent_label: str,
                        canvas_width: int) -> None:
    steps = CHAINS[chain_id]
    n = len(steps)
    node_labels = [(steps[0]["subject_label"], steps[0]["subject_id"])]
    for s in steps:
        node_labels.append((s["object_label"], s["object_id"]))

    margin = 110
    usable = canvas_width - 2 * margin
    xs = [margin + i * (usable / n) for i in range(n + 1)]
    y = 150
    node_rx, node_ry = min(95, usable / (n + 1) / 2 - 10), 38

    canvas.text(canvas_width / 2, 34,
                f"{n}-ary chain ({n} antecedents, AMT's own diagram style)",
                "#0f172a", font_size=15, weight="600")

    for x, (label, cid) in zip(xs, node_labels):
        oval(canvas, x, y, node_rx, node_ry, label, Colours.SUBJECT_OBJECT,
             font_size=11, sub_label=cid)

    for i, s in enumerate(steps):
        x1, x2 = xs[i] + node_rx, xs[i + 1] - node_rx
        arrow(canvas, x1, y - 10, x2, y - 10, colour="#0f172a")
        pred = s["predicate_id"].replace("skos:", "")
        edge_chip(canvas, (xs[i] + xs[i + 1]) / 2, y - 46, pred,
                  f"w={s['weight']:.3f}", width=130)

    # AMT's own convention: ONE red dashed arc, antecedent-row to consequent
    arc_y = y + 140
    points = [(xs[0], y + node_ry)] + \
        [(xs[0], arc_y)] + [(xs[-1], arc_y)] + [(xs[-1], y + node_ry)]
    elbow(canvas, points, dashed=True, colour=RED, width=2.2)

    best_op = RECOMMENDED_BY_ARITY[n]
    best_val = CHAIN_RESULTS[chain_id][best_op]
    edge_chip(canvas, (xs[0] + xs[-1]) / 2, arc_y + 34,
              f"inferred {consequent_label} ({best_op}, AMT default for n={n})",
              f"w = {best_val:.3f}", style=Colours.CLASS, dashed=True,
              width=460)


def build_chain_1(canvas) -> None:
    draw_chain_diagram(canvas, 1, "skos:narrowMatch", canvas.width)


def build_chain_2(canvas) -> None:
    draw_chain_diagram(canvas, 2, "skos:narrowMatch", canvas.width)


def build_chain_3(canvas) -> None:
    draw_chain_diagram(canvas, 3, "skos:narrowMatch", canvas.width)


# ---------------------------------------------------------------------------
# Figure 4: operator result by arity, across all three real chains
# ---------------------------------------------------------------------------
def build_operator_by_arity(canvas) -> None:
    x0, y0, w, h = 130, 90, 900, 320
    canvas.text(x0 + w / 2, 34,
                "Same operators, three real chain lengths",
                "#0f172a", font_size=15, weight="600")
    canvas.line(x0, y0 + h, x0 + w, y0 + h, colour="#94a3b8", width=1.3,
                arrow=False)
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        py = y0 + h - t * h
        canvas.line(x0 - 6, py, x0, py, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 14, py, f"{t:g}", "#475569", font_size=10.5,
                    anchor="end")
    canvas.text(x0, y0 - 16, "degree of connection", "#334155", font_size=12,
                anchor="start")

    op_names = list(OPERATORS.keys())
    chain_ids = [1, 2, 3]
    group_w = w / len(chain_ids)
    bar_w = group_w / (len(op_names) + 1)
    colours = ["#e2e8f0", "#fbbf24", "#9a3412", "#4c1d95", "#166534", "#1d4ed8"]
    for gi, cid in enumerate(chain_ids):
        gx0 = x0 + gi * group_w
        for oi, name in enumerate(op_names):
            val = CHAIN_RESULTS[cid][name]
            bx = gx0 + (oi + 0.5) * bar_w
            bar_h = val * h
            by = y0 + h - bar_h
            style = {"fill": colours[oi], "stroke": "#000000",
                     "text": "#000000"}
            box(canvas, bx - bar_w / 2 + 2, by, bar_w - 4, bar_h, "", style,
                rx=2)
        n = len(CHAINS[cid])
        canvas.text(gx0 + group_w / 2, y0 + h + 24, f"chain {cid} (n={n})",
                    "#0f172a", font_size=12.5, weight="600")
        canvas.text(gx0 + group_w / 2, y0 + h + 42,
                    f"AMT default: {RECOMMENDED_BY_ARITY[n]}", "#475569",
                    font_size=10.5)

    lx = x0
    ly = y0 + h + 74
    for name, colour in zip(op_names, colours):
        box(canvas, lx, ly, 16, 14, "",
            {"fill": colour, "stroke": "#000000", "text": "#000000"},
            rx=2)
        canvas.text(lx + 22, ly + 11, name, "#0f172a", font_size=10.5,
                    anchor="start")
        lx += 155


# ---------------------------------------------------------------------------
# Figure 5: synthetic illustration - Product dampens too aggressively at
# higher n (AMT's own documented warning, verified with clean, illustrative
# weights - NOT one of the three real chains above, deliberately labelled so)
# ---------------------------------------------------------------------------
def build_product_dampening(canvas) -> None:
    x0, y0, w, h = 140, 90, 780, 320
    canvas.text(x0 + w / 2, 30,
                "Illustrative only: why Product is not recommended past n=3",
                "#0f172a", font_size=15, weight="600")
    canvas.text(x0 + w / 2, 54,
                "(clean 0.90-per-edge weights, not one of the real chains above)",
                "#94a3b8", font_size=11)

    canvas.line(x0, y0 + h, x0 + w, y0 + h, colour="#94a3b8", width=1.3,
                arrow=False)
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        py = y0 + h - t * h
        canvas.line(x0 - 6, py, x0, py, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 14, py, f"{t:g}", "#475569", font_size=10.5,
                    anchor="end")
        px = x0
    canvas.text(x0, y0 - 16, "degree of connection", "#334155", font_size=12,
                anchor="start")
    canvas.text(x0 + w / 2, y0 + h + 36, "chain length n (each edge w=0.90)",
                "#334155", font_size=12)

    ns = list(range(2, 8))
    series = {
        "Goedel": [OPERATORS["Goedel"]([0.9] * n) for n in ns],
        "Product": [OPERATORS["Product"]([0.9] * n) for n in ns],
        "GeometricMean": [OPERATORS["GeometricMean"]([0.9] * n) for n in ns],
    }
    colours = {"Goedel": "#166534", "Product": "#dc2626",
               "GeometricMean": "#1d4ed8"}
    for name, vals in series.items():
        pts = []
        for n, v in zip(ns, vals):
            px = x0 + (n - ns[0]) / (ns[-1] - ns[0]) * w
            py = y0 + h - v * h
            pts.append((px, py))
        for a, b in zip(pts, pts[1:]):
            canvas.line(a[0], a[1], b[0], b[1], colour=colours[name],
                        width=2.4, arrow=False)
        for (px, py) in pts:
            canvas.ellipse(px, py, 5, 5, {"fill": colours[name],
                                           "stroke": colours[name]})
    for i, n in enumerate(ns):
        px = x0 + (n - ns[0]) / (ns[-1] - ns[0]) * w
        canvas.text(px, y0 + h + 18, str(n), "#475569", font_size=10.5)

    ly = y0 + 10
    for i, (name, colour) in enumerate(colours.items()):
        canvas.line(x0 + w - 180, ly + i * 20, x0 + w - 150, ly + i * 20,
                    colour=colour, width=2.4, arrow=False)
        canvas.text(x0 + w - 140, ly + i * 20 + 4, name, "#0f172a",
                    font_size=11, anchor="start")

    canvas.text(x0 + w / 2, y0 + h + 66,
                f"At n=6: Product={series['Product'][4]:.2f}, "
                f"GeometricMean={series['GeometricMean'][4]:.2f} - Product "
                "has nearly halved while GeometricMean barely moved.",
                "#475569", font_size=11.5)
    canvas.text(x0 + w / 2, y0 + h + 84,
                "Goedel's line is not missing - for equal per-edge weights, "
                "min(w,...,w) = (w^n)^(1/n) = w exactly, so it sits exactly "
                "under the GeometricMean line at every n.", "#94a3b8",
                font_size=10)


# ---------------------------------------------------------------------------
# Figure 6: what plain SKOS can and cannot do
# ---------------------------------------------------------------------------
def build_skos_before_after(canvas) -> None:
    canvas.text(640, 34, "What plain SKOS can and cannot infer",
                "#0f172a", font_size=16, weight="600")

    col_w = 540
    xs = [40, 40 + col_w + 60]
    titles = ["Plain SKOS", "SKOS + AMT (this scenario)"]
    bodies = [
        [("Only skos:exactMatch is transitive", "600", 12.5),
         ("(SKOS Reference, Section 10.1).", "normal", 11),
         ("", "normal", 6),
         ("closeMatch/broadMatch/narrowMatch/", "normal", 11),
         ("relatedMatch are deliberately NOT -", "normal", 11),
         ("to avoid compound errors across", "normal", 11),
         ("more than two concept schemes.", "normal", 11),
         ("", "normal", 6),
         ("Result: a narrowMatch into vocabulary B", "normal", 11),
         ("cannot reach vocabulary C, even via a", "normal", 11),
         ("closeMatch already asserted in B.", "normal", 11)],
        [("Any mix of mapping properties can", "600", 12.5),
         ("be composed via amt:RoleChainAxiom.", "normal", 11),
         ("", "normal", 6),
         ("The result is not asserted as fact -", "normal", 11),
         ("it carries a degraded amt:weight,", "normal", 11),
         ("computed by the chosen operator.", "normal", 11),
         ("", "normal", 6),
         ("This is the principled version of what", "normal", 11),
         ("SKOS's design avoided: composition", "normal", 11),
         ("with the uncertainty made explicit,", "normal", 11),
         ("not composition assumed for free.", "normal", 11)],
    ]
    styles = [Colours.NEUTRAL_PROCESS, Colours.PROP_META]
    for x, title, body, style in zip(xs, titles, bodies, styles):
        rect_shape(canvas, x, 70, col_w, 340, style)
        canvas.text(x + col_w / 2, 96, title, style["text"], font_size=14,
                    weight="600")
        text_block(canvas, x + col_w / 2, 230, body, style["text"],
                    line_height=19)

    canvas.text(640, 430,
                "Paraphrased from the SKOS Reference, Section 10.1 (not a "
                "verbatim quote) and from amt-engine's own ontology README.",
                "#475569", font_size=11)


# ---------------------------------------------------------------------------
# Figure 7: binary vs genuinely n-ary operators
# ---------------------------------------------------------------------------
def build_binary_vs_nary(canvas) -> None:
    canvas.text(640, 34, "Two different strategies for combining n weights",
                "#0f172a", font_size=16, weight="600")

    col_w = 540
    xs = [40, 40 + col_w + 60]
    titles = ["Binary operators (folded pairwise)",
              "N-ary operators (whole list at once)"]
    bodies = [
        [("Goedel, Product, Lukasiewicz,", "600", 12.5),
         ("Einstein, Hamacher", "600", 12.5),
         ("", "normal", 6),
         ("score = w_1", "normal", 11),
         ("for i in 2..n:", "normal", 11),
         ("    score = op(score, w_i)", "normal", 11),
         ("", "normal", 6),
         ("Associative - order of folding", "normal", 11),
         ("does not change the result.", "normal", 11)],
        [("GeometricMean", "600", 12.5),
         ("", "600", 12.5),
         ("", "normal", 6),
         ("score = (w_1 * w_2 * ... * w_n)", "normal", 11),
         ("        ^ (1/n)", "normal", 11),
         ("", "normal", 11),
         ("", "normal", 6),
         ("Needs the full weight list at once -", "normal", 11),
         ("cannot be computed incrementally.", "normal", 11)],
    ]
    for x, title, body in zip(xs, titles, bodies):
        rect_shape(canvas, x, 70, col_w, 300, Colours.PROP_META)
        canvas.text(x + col_w / 2, 96, title, Colours.PROP_META["text"],
                    font_size=13, weight="600")
        text_block(canvas, x + col_w / 2, 230, body,
                    Colours.PROP_META["text"], line_height=19)

    canvas.text(640, 392,
                "The amt:arity annotation on each amt:Logic instance tells a "
                "reasoner which strategy to use - copied from amt-engine's "
                "ontology README, not re-derived.", "#475569", font_size=11)


# ---------------------------------------------------------------------------
# Figure 8: the GSAS coverage gap
# ---------------------------------------------------------------------------
def build_gsas_coverage_gap(canvas) -> None:
    canvas.text(640, 34, "GSAS calibrates three of the five SKOS mapping "
                "properties", "#0f172a", font_size=15, weight="600")

    covered = [("exactMatch", "1.0", Colours.REAL_OBJECT),
               ("closeMatch", "0.938", Colours.REAL_OBJECT),
               ("relatedMatch", "0.495 (mean)", Colours.REAL_OBJECT)]
    uncovered = [("broadMatch", Colours.TERM), ("narrowMatch", Colours.TERM)]

    cx0 = 180
    for i, (label, val, style) in enumerate(covered):
        x = cx0 + i * 200
        box(canvas, x, 100, 170, 90, label, style, sub_label=f"GSAS: {val}")
    canvas.text(cx0 + 300, 220, "Calibrated by all four GSAS models",
                "#166534", font_size=12, weight="600")

    ux0 = 900
    for i, (label, style) in enumerate(uncovered):
        x = ux0 + i * 200
        box(canvas, x, 100, 170, 90, label, style,
            sub_label="no GSAS degree exists")
    canvas.text(ux0 + 100, 220, "Not covered by any GSAS model",
                "#4c1d95", font_size=12, weight="600")

    canvas.text(640, 280,
                "This scenario's narrowMatch edges therefore use the "
                "relatedMatch degree (0.4947) as a reasoned analogy, not a "
                "GSAS value for narrowMatch itself - stated in",
                "#475569", font_size=11.5)
    canvas.text(640, 300,
                "data/real_chains.tsv's own header. A principled GSAS "
                "extension to hierarchical mapping properties is future "
                "work, not something this repository claims exists.",
                "#475569", font_size=11.5)


def main() -> None:
    write_outputs(build_chain_1, IMG_DIR, "scenario-06-chain-2ary",
                  width=1100, height=420)
    write_outputs(build_chain_2, IMG_DIR, "scenario-06-chain-3ary",
                  width=1280, height=420)
    write_outputs(build_chain_3, IMG_DIR, "scenario-06-chain-4ary",
                  width=1460, height=420)
    write_outputs(build_operator_by_arity, IMG_DIR,
                  "scenario-06-operator-by-arity", width=1160, height=520)
    write_outputs(build_product_dampening, IMG_DIR,
                  "scenario-06-product-dampening", width=1060, height=530)
    write_outputs(build_skos_before_after, IMG_DIR,
                  "scenario-06-skos-before-after", width=1280, height=460)
    write_outputs(build_binary_vs_nary, IMG_DIR,
                  "scenario-06-binary-vs-nary", width=1280, height=420)
    write_outputs(build_gsas_coverage_gap, IMG_DIR,
                  "scenario-06-gsas-coverage-gap", width=1280, height=340)

    print(f"Wrote figures to {IMG_DIR}")
    for cid, steps in CHAINS.items():
        n = len(steps)
        print(f"Chain {cid} (n={n}): weights={[round(s['weight'],4) for s in steps]}")
        for name, val in CHAIN_RESULTS[cid].items():
            print(f"   {name:16s} {val:.4f}")


if __name__ == "__main__":
    main()
