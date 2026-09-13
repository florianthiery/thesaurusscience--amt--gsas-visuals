#!/usr/bin/env python3
"""Build the five figures for scenario-05 (Lasse Mempel's suggested test:
feed a raw embedding similarity directly into AMT, bypassing GSAS
calibration, and see how much the choice of fuzzy operator then matters).

Run standalone:
    python scenario-05-embedding-feed-test/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-05

Reads ../data/chain_variants.tsv - the same real 2-hop chain used in
scenario 3, with one edge given two alternative weights: GSAS's real
minimal-model closeMatch degree, and an illustrative "raw embedding fed
directly" placeholder. The six fuzzy-logic aggregation functions are copied
from amt/logic.py, as in scenario 3.

Writes img/scenario-05-chain.{svg,png}, img/scenario-05-heatmap.{svg,png},
img/scenario-05-headline-comparison.{svg,png},
img/scenario-05-sensitivity-spread.{svg,png} and
img/scenario-05-takeaway.{svg,png}.
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
    oval,
    rect_shape,
    text_block,
    write_outputs,
)

DATA_DIR = SCENARIO_ROOT / "data"
IMG_DIR = SCENARIO_ROOT / "img"


# ---------------------------------------------------------------------------
# AMT's six fuzzy-logic operators, copied from amt/logic.py (as in scenario 3)
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
HEADLINE_OPERATOR = "Einstein"  # AMT's own recommendation for 3-step chains
                                  # (see scenario 3's README)


def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


CHAIN = load_tsv(DATA_DIR / "chain_variants.tsv")
W_EXACT = float(CHAIN[1]["weight_gsas_calibrated"])  # 1.0, same in both variants
W_CLASS = float(CHAIN[2]["weight_gsas_calibrated"])  # 0.90, same in both variants
W_CLOSE_GSAS = float(CHAIN[0]["weight_gsas_calibrated"])
W_CLOSE_RAW = float(CHAIN[0]["weight_raw_embedding"])

VARIANTS = {
    "GSAS-calibrated": [W_CLOSE_GSAS, W_EXACT, W_CLASS],
    "Raw embedding (direct)": [W_CLOSE_RAW, W_EXACT, W_CLASS],
}

RESULTS = {
    variant: {name: fn(weights) for name, fn in OPERATORS.items()}
    for variant, weights in VARIANTS.items()
}
SPREADS = {
    variant: max(vals.values()) - min(vals.values())
    for variant, vals in RESULTS.items()
}

CRM_CLASS_STYLE = Colours.CLASS


# ---------------------------------------------------------------------------
# Figure 1: chain with dual-labelled closeMatch edge
# ---------------------------------------------------------------------------
def build_chain(canvas) -> None:
    y = 150
    xs = [110, 430, 750, 1070]
    node_rx, node_ry = 130, 42

    labels = [("Artefact", "dai:_fac3092f"),
              ("goods and commodities", "dai:_ad8ec5e3"),
              ("mobile objects", "bbt:Concept_000017")]
    for x, (label, cid) in zip(xs[:3], labels):
        oval(canvas, x, y, node_rx, node_ry, label, Colours.SUBJECT_OBJECT,
             sub_label=cid)
    box(canvas, xs[3] - 120, y - 42, 240, 84, "crm:E22_Human-Made_Object",
        CRM_CLASS_STYLE, sub_label="(illustrative)", font_size=13)

    arrow(canvas, xs[0] + node_rx, y - 14, xs[1] - node_rx, y - 14)
    edge_chip(canvas, (xs[0] + xs[1]) / 2, y - 58, "closeMatch: GSAS-calibrated",
              f"w = {W_CLOSE_GSAS:.3f}", style=Colours.PROP_META)
    arrow(canvas, xs[0] + node_rx, y + 14, xs[1] - node_rx, y + 14,
          dashed=True, colour="#7c3aed")
    edge_chip(canvas, (xs[0] + xs[1]) / 2, y + 58,
              "closeMatch: raw embedding (direct)",
              f"w = {W_CLOSE_RAW:.2f} (illustrative)", style=Colours.TERM,
              dashed=True)

    arrow(canvas, xs[1] + node_rx, y, xs[2] - node_rx, y)
    edge_chip(canvas, (xs[1] + xs[2]) / 2, y - 30, "exactMatch",
              f"w = {W_EXACT:.2f} (GSAS)")
    arrow(canvas, xs[2] + node_rx, y, xs[3] - 120, y)
    edge_chip(canvas, (xs[2] + xs[3]) / 2 - 15, y - 30, "hasCRMClass",
              f"w = {W_CLASS:.2f} (illustrative)")

    canvas.text((xs[0] + xs[3]) / 2, 34,
                "Same real chain, two ways to weight the first edge",
                "#0f172a", font_size=16, weight="600")
    canvas.text((xs[0] + xs[3]) / 2, y + 150,
                "Everything downstream of the closeMatch edge is identical "
                "in both runs - only its input weight changes.", "#475569",
                font_size=11.5)


# ---------------------------------------------------------------------------
# Figure 2: operator x calibration heatmap
# ---------------------------------------------------------------------------
def build_heatmap(canvas) -> None:
    canvas.text(660, 30,
                "Propagated degree: 2 input conditions x 6 AMT operators",
                "#0f172a", font_size=15, weight="600")

    variants = list(VARIANTS.keys())
    ops = list(OPERATORS.keys())
    x0, y0 = 260, 90
    cell_w, cell_h = 150, 70
    row_label_w = 240

    for j, op in enumerate(ops):
        canvas.text(x0 + j * cell_w + cell_w / 2, y0 - 16, op, "#0f172a",
                    font_size=11, weight="600")

    lo, hi = 0.5, 1.0  # colour scale range across all shown values
    for i, variant in enumerate(variants):
        y = y0 + i * (cell_h + 20)
        canvas.text(x0 - row_label_w + 10, y + cell_h / 2, variant,
                    "#0f172a", font_size=12.5, weight="600", anchor="start")
        for j, op in enumerate(ops):
            x = x0 + j * cell_w
            val = RESULTS[variant][op]
            t = max(0.0, min(1.0, (val - lo) / (hi - lo)))
            # amber (#fde68a, low) -> orange (#9a3412, high) interpolation
            r = round(0xfd + (0x9a - 0xfd) * t)
            g = round(0xe6 + (0x34 - 0xe6) * t)
            b = round(0x8a + (0x12 - 0x8a) * t)
            fill = f"#{r:02x}{g:02x}{b:02x}"
            style = {"fill": fill, "stroke": "#000000",
                     "text": "#ffffff" if t > 0.5 else "#000000"}
            rect_shape(canvas, x, y, cell_w - 8, cell_h, style, rx=6)
            canvas.text(x + (cell_w - 8) / 2, y + cell_h / 2, f"{val:.3f}",
                        style["text"], font_size=13, weight="600")

    ry0 = y0 + len(variants) * (cell_h + 20) + 10
    for i, variant in enumerate(variants):
        canvas.text(x0 - row_label_w + 10, ry0 + i * 20,
                    f"spread ({variant}): {SPREADS[variant]:.3f}", "#475569",
                    font_size=11, anchor="start")


# ---------------------------------------------------------------------------
# Figure 3: headline-operator comparison
# ---------------------------------------------------------------------------
def build_headline_comparison(canvas) -> None:
    x0, y0, w, h = 200, 90, 500, 320
    canvas.text(x0 + w / 2 + 100, 30,
                f"Same chain, {HEADLINE_OPERATOR} product only: GSAS vs. raw "
                "embedding input", "#0f172a", font_size=15, weight="600")

    canvas.line(x0, y0 + h, x0 + w + 300, y0 + h, colour="#94a3b8", width=1.3,
                arrow=False)
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        py = y0 + h - t * h
        canvas.line(x0 - 6, py, x0, py, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 14, py, f"{t:g}", "#475569", font_size=10.5,
                    anchor="end")
    canvas.text(x0, y0 - 16, f"{HEADLINE_OPERATOR} product degree",
                "#334155", font_size=12, anchor="start")

    bar_w = 140
    positions = [x0 + 100, x0 + 100 + 260]
    for x, variant in zip(positions, VARIANTS.keys()):
        val = RESULTS[variant][HEADLINE_OPERATOR]
        style = Colours.CLASS if variant == "GSAS-calibrated" else Colours.TERM
        bar_h = val * h
        by = y0 + h - bar_h
        box(canvas, x, by, bar_w, bar_h, "", style, rx=6)
        canvas.text(x + bar_w / 2, by - 16, f"{val:.3f}", "#0f172a",
                    font_size=13, weight="600")
        canvas.text(x + bar_w / 2, y0 + h + 26, variant, "#0f172a",
                    font_size=11.5, weight="600")

    gap = RESULTS["GSAS-calibrated"][HEADLINE_OPERATOR] - \
        RESULTS["Raw embedding (direct)"][HEADLINE_OPERATOR]
    canvas.text(x0 + w / 2 + 100, y0 + h + 70,
                f"Gap: {gap:.3f} degree of connection - purely from skipping "
                "GSAS's calibration step on one edge.", "#475569",
                font_size=11.5)


# ---------------------------------------------------------------------------
# Figure 4: sensitivity spread (range/whisker per condition)
# ---------------------------------------------------------------------------
def build_sensitivity_spread(canvas) -> None:
    x0, y0, w, h = 220, 90, 700, 300
    canvas.text(x0 + w / 2, 30,
                "How much the operator choice matters, per input condition",
                "#0f172a", font_size=15, weight="600")
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    canvas.line(x0, y0 + h, x0 + w, y0 + h, colour="#94a3b8", width=1.3,
                arrow=False)
    for t in (0, 0.25, 0.5, 0.75, 1.0):
        py = y0 + h - t * h
        canvas.line(x0 - 6, py, x0, py, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 14, py, f"{t:g}", "#475569", font_size=10.5,
                    anchor="end")
    canvas.text(x0, y0 - 16, "degree of connection across all 6 operators",
                "#334155", font_size=12, anchor="start")

    xs = [x0 + w * 0.3, x0 + w * 0.7]
    for x, variant in zip(xs, VARIANTS.keys()):
        vals = list(RESULTS[variant].values())
        lo_v, hi_v = min(vals), max(vals)
        y_lo = y0 + h - lo_v * h
        y_hi = y0 + h - hi_v * h
        canvas.line(x, y_lo, x, y_hi, colour="#334155", width=3, arrow=False)
        canvas.ellipse(x, y_hi, 7, 7, {"fill": Colours.CLASS["fill"],
                                       "stroke": "#000000"})
        canvas.ellipse(x, y_lo, 7, 7, {"fill": Colours.SUBJECT_OBJECT["fill"],
                                       "stroke": "#000000"})
        canvas.text(x, y_hi - 16, f"max {hi_v:.3f}", "#0f172a", font_size=10.5)
        canvas.text(x, y_lo + 20, f"min {lo_v:.3f}", "#0f172a", font_size=10.5)
        canvas.text(x, y0 + h + 30, variant, "#0f172a", font_size=12,
                    weight="600")
        canvas.text(x, y0 + h + 50, f"spread = {hi_v - lo_v:.3f}", "#475569",
                    font_size=11)


# ---------------------------------------------------------------------------
# Figure 5: takeaway summary
# ---------------------------------------------------------------------------
def build_takeaway(canvas) -> None:
    canvas.text(660, 40, "Lasse's test, answered", "#0f172a", font_size=18,
                weight="600")
    rect_shape(canvas, 140, 100, 1040, 260, Colours.NEUTRAL_PROCESS)
    lines = [
        ('"What happens if you feed AMT with the embedding distances?"',
         "600", 14),
        ("", "normal", 8),
        (f"Same 3-link chain, only the first edge's weight changes: "
         f"{W_CLOSE_GSAS:.3f} (GSAS) vs {W_CLOSE_RAW:.2f} (raw, illustrative).",
         "normal", 12.5),
        ("", "normal", 6),
        (f"Spread across all 6 operators: {SPREADS['GSAS-calibrated']:.3f} "
         f"(GSAS-calibrated) vs {SPREADS['Raw embedding (direct)']:.3f} "
         "(raw embedding) - roughly 2.7x wider.", "normal", 12.5),
        ("", "normal", 6),
        ("GSAS's calibration doesn't just add interpretability - by pushing",
         "normal", 12.5),
        ("values toward the extremes, it also makes the choice of AMT",
         "normal", 12.5),
        ("operator matter less. Feeding raw similarities works, but the",
         "normal", 12.5),
        ("result depends more on which operator you pick.", "normal", 12.5),
    ]
    text_block(canvas, 660, 230, lines, "#0f172a", line_height=24)


def main() -> None:
    write_outputs(build_chain, IMG_DIR, "scenario-05-chain",
                  width=1280, height=420)
    write_outputs(build_heatmap, IMG_DIR, "scenario-05-heatmap",
                  width=1320, height=340)
    write_outputs(build_headline_comparison, IMG_DIR,
                  "scenario-05-headline-comparison", width=1020, height=520)
    write_outputs(build_sensitivity_spread, IMG_DIR,
                  "scenario-05-sensitivity-spread", width=1080, height=460)
    write_outputs(build_takeaway, IMG_DIR, "scenario-05-takeaway",
                  width=1320, height=400)

    print(f"Wrote figures to {IMG_DIR}")
    for variant, vals in RESULTS.items():
        print(f"{variant} (input={VARIANTS[variant][0]:.3f}):")
        for name, v in vals.items():
            print(f"  {name:16s} {v:.4f}")
        print(f"  spread = {SPREADS[variant]:.4f}")


if __name__ == "__main__":
    main()
