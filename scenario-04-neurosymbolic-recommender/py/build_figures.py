#!/usr/bin/env python3
"""Build the five figures for scenario-04 (neuro-symbolic recommender -
outlook, not a built system).

Run standalone:
    python scenario-04-neurosymbolic-recommender/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-04

Reads ../data/candidates.tsv - a real source concept (thesaurusscience) and
four real Getty AAT / FISH candidate concepts (Mappings/ads_aat.sssom.tsv),
each with a genuinely-computed graph in-degree (used as a simplified stand-in
for AMT graph plausibility - see the scenario README for the honest caveat
about this simplification) and an illustrative placeholder embedding
similarity (no real embeddings exist for thesaurusscience - same limitation
as scenario 2).

This scenario is an OUTLOOK, not a built system: no recommender, ranking
pipeline or embedding model is implemented anywhere in this repository.
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

DATA_DIR = SCENARIO_ROOT / "data"
IMG_DIR = SCENARIO_ROOT / "img"

SOURCE_LABEL = "clay pipe manufacture"
SOURCE_ID = "wnk:wk004175"


def load_candidates() -> list[dict]:
    with (DATA_DIR / "candidates.tsv").open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    data = list(csv.DictReader(rows, delimiter="\t"))
    max_deg = max(int(r["real_indegree_in_ads_aat"]) for r in data)
    for r in data:
        deg = int(r["real_indegree_in_ads_aat"])
        neural = float(r["neural_similarity_placeholder"])
        symbolic = (deg + 1) / (max_deg + 1)  # Laplace-smoothed in-degree
        r["neural"] = neural
        r["symbolic"] = symbolic
        r["product"] = neural * symbolic
        r["goedel"] = min(neural, symbolic)
        r["geomean"] = (neural * symbolic) ** 0.5
    return data


CANDIDATES = load_candidates()
RANKED_BY_PRODUCT = sorted(CANDIDATES, key=lambda r: -r["product"])
RANKED_BY_NEURAL = sorted(CANDIDATES, key=lambda r: -r["neural"])


# ---------------------------------------------------------------------------
# Small local chart helpers (same pattern as scenario-02's - not generic
# enough for the shared py/viz_utils.py)
# ---------------------------------------------------------------------------
def _to_px(x, y, x0, y0, w, h, xmin, xmax, ymin, ymax):
    px = x0 + (x - xmin) / (xmax - xmin) * w
    py = y0 + h - (y - ymin) / (ymax - ymin) * h
    return px, py


def draw_axes(canvas, x0, y0, w, h, xlabel="", ylabel="",
              x_ticks=(0, 0.25, 0.5, 0.75, 1.0),
              y_ticks=(0, 0.25, 0.5, 0.75, 1.0)):
    canvas.line(x0, y0 + h, x0 + w, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    for t in x_ticks:
        px, py = _to_px(t, 0, x0, y0, w, h, 0, 1, 0, 1)
        canvas.line(px, y0 + h, px, y0 + h + 6, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(px, y0 + h + 18, f"{t:g}", "#475569", font_size=10.5)
    for t in y_ticks:
        px2, py2 = _to_px(0, t, x0, y0, w, h, 0, 1, 0, 1)
        canvas.line(x0 - 6, py2, x0, py2, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 12, py2, f"{t:g}", "#475569", font_size=10.5, anchor="end")
    if xlabel:
        canvas.text(x0 + w, y0 + h + 36, xlabel, "#334155", font_size=12,
                    anchor="end")
    if ylabel:
        canvas.text(x0, y0 - 16, ylabel, "#334155", font_size=12, anchor="start")


CAND_COLOUR = "#1d4ed8"


# ---------------------------------------------------------------------------
# Figure 1: architecture diagram
# ---------------------------------------------------------------------------
def build_architecture(canvas) -> None:
    canvas.text(660, 30, "Two independent [0,1] signals, fused into one "
                "ranking score (outlook, not implemented)", "#0f172a",
                font_size=15, weight="600")

    oval(canvas, 110, 190, 110, 44, SOURCE_LABEL, Colours.SUBJECT_OBJECT,
         sub_label=SOURCE_ID)

    rect_shape(canvas, 300, 90, 300, 90, Colours.PROP_META)
    text_block(canvas, 450, 135, [
        ("Neural signal", "600", 13),
        ("embedding similarity,", "normal", 11),
        ("GSAS-calibrated (scenario 2)", "normal", 11),
    ], Colours.PROP_META["text"], line_height=16)

    rect_shape(canvas, 300, 240, 300, 90, Colours.PROP_META)
    text_block(canvas, 450, 285, [
        ("Symbolic signal", "600", 13),
        ("graph plausibility,", "normal", 11),
        ("AMT-composed (scenario 3-style)", "normal", 11),
    ], Colours.PROP_META["text"], line_height=16)

    arrow(canvas, 220, 190, 300, 135)
    arrow(canvas, 220, 190, 300, 285)

    rect_shape(canvas, 700, 165, 220, 90, Colours.CLASS)
    text_block(canvas, 810, 210, [
        ("Fusion operator", "600", 13),
        ("Product (headline)", "normal", 11),
        ("- see figure 4 for others", "normal", 10),
    ], Colours.CLASS["text"], line_height=16)
    arrow(canvas, 600, 135, 700, 195)
    arrow(canvas, 600, 285, 700, 235)

    oval(canvas, 1050, 210, 110, 60, "Ranked", Colours.REAL_OBJECT,
         sub_label="candidate list")
    arrow(canvas, 920, 210, 940, 210)

    canvas.text(660, 400,
                "For every source concept without a strong existing "
                "mapping, rank every candidate target by how well the two "
                "signals agree - not implemented here, see the README's "
                "Python sketch.", "#475569", font_size=11.5)


# ---------------------------------------------------------------------------
# Figure 2: ranking bar chart (grouped bars)
# ---------------------------------------------------------------------------
def build_ranking(canvas) -> None:
    x0, y0, w, h = 130, 80, 900, 320
    canvas.text(x0 + w / 2, 30,
                f'Ranking candidates for "{SOURCE_LABEL}" ({SOURCE_ID})',
                "#0f172a", font_size=15, weight="600")
    draw_axes(canvas, x0, y0, w, h, ylabel="score", x_ticks=())

    n = len(RANKED_BY_PRODUCT)
    group_w = w / n
    bar_w = 26
    legend_items = [("neural", Colours.SUBJECT_OBJECT, "fill"),
                     ("symbolic", Colours.PROP_META, "fill"),
                     ("fused (Product)", Colours.CLASS, "fill")]
    for i, row in enumerate(RANKED_BY_PRODUCT):
        gx = x0 + i * group_w + group_w / 2
        for j, (key, style) in enumerate([
            ("neural", Colours.SUBJECT_OBJECT),
            ("symbolic", Colours.PROP_META),
            ("product", Colours.CLASS),
        ]):
            bx = gx - 1.5 * bar_w + j * bar_w
            val = row[key]
            bar_h = val * h
            by = y0 + h - bar_h
            box(canvas, bx, by, bar_w - 4, bar_h, "", style, rx=3)
            canvas.text(bx + (bar_w - 4) / 2, by - 12, f"{val:.2f}",
                        "#0f172a", font_size=9.5)
        canvas.text(gx, y0 + h + 40, row["candidate_label"], "#0f172a",
                    font_size=11, weight="600")
        canvas.text(gx, y0 + h + 56, row["candidate_id"], "#64748b",
                    font_size=9.5)

    ly = y0 + h + 90
    for i, (name, style, _) in enumerate(legend_items):
        lx = x0 + i * 260
        box(canvas, lx, ly, 20, 16, "", style, rx=3)
        canvas.text(lx + 28, ly + 12, name, "#0f172a", font_size=11,
                    anchor="start")


# ---------------------------------------------------------------------------
# Figure 3: neural-vs-symbolic quadrant
# ---------------------------------------------------------------------------
def build_quadrant(canvas) -> None:
    x0, y0, w, h = 130, 70, 700, 500
    canvas.text(x0 + w / 2, 30,
                "Why one signal alone is not enough", "#0f172a",
                font_size=15, weight="600")
    draw_axes(canvas, x0, y0, w, h, xlabel="neural (embedding similarity)",
              ylabel="symbolic (graph plausibility)")

    mx, my = _to_px(0.5, 0.5, x0, y0, w, h, 0, 1, 0, 1)
    canvas.line(x0, my, x0 + w, my, colour="#e2e8f0", width=1.2, dashed=True,
                arrow=False)
    canvas.line(mx, y0, mx, y0 + h, colour="#e2e8f0", width=1.2, dashed=True,
                arrow=False)

    for row in CANDIDATES:
        px, py = _to_px(row["neural"], row["symbolic"], x0, y0, w, h, 0, 1, 0, 1)
        canvas.ellipse(px, py, 8, 8, {"fill": CAND_COLOUR, "stroke": CAND_COLOUR})
        canvas.text(px + 14, py - 10, row["candidate_label"], "#0f172a",
                    font_size=11.5, weight="600", anchor="start")
        canvas.text(px + 14, py + 8,
                    f'fused = {row["product"]:.2f}', "#475569", font_size=10,
                    anchor="start")

    canvas.text(x0 + w - 10, y0 + h - 36,
                "high neural, low symbolic:", "#b45309", font_size=10.5,
                anchor="end")
    canvas.text(x0 + w - 10, y0 + h - 20,
                "lexically close, unverified", "#b45309", font_size=10.5,
                anchor="end")
    canvas.text(x0 + 10, y0 + 20, "high on both: the actual winner",
                "#166534", font_size=10.5, anchor="start")


# ---------------------------------------------------------------------------
# Figure 4: operator robustness
# ---------------------------------------------------------------------------
def build_operator_robustness(canvas) -> None:
    x0, y0, w, h = 140, 80, 900, 320
    canvas.text(x0 + w / 2, 30,
                "Same four candidates, three fusion operators - the winner "
                "does not change", "#0f172a", font_size=15, weight="600")
    draw_axes(canvas, x0, y0, w, h, ylabel="fused score", x_ticks=())

    ops = [("Product", "product"), ("Goedel (min)", "goedel"),
           ("GeometricMean", "geomean")]
    n_ops = len(ops)
    n_cand = len(CANDIDATES)
    group_w = w / n_ops
    bar_w = 34
    for i, (op_name, key) in enumerate(ops):
        gx0 = x0 + i * group_w
        ranked = sorted(CANDIDATES, key=lambda r: -r[key])
        for j, row in enumerate(ranked):
            bx = gx0 + group_w / 2 - (n_cand * bar_w) / 2 + j * bar_w
            val = row[key]
            bar_h = val * h
            by = y0 + h - bar_h
            style = Colours.CLASS if j == 0 else Colours.PROP_META
            box(canvas, bx, by, bar_w - 4, bar_h, "", style, rx=3)
            canvas.text(bx + (bar_w - 4) / 2, by - 11, f"{val:.2f}",
                        "#0f172a", font_size=9)
        canvas.text(gx0 + group_w / 2, y0 + h + 24, op_name, "#0f172a",
                    font_size=12, weight="600")
        canvas.text(gx0 + group_w / 2, y0 + h + 42,
                    f'winner: {ranked[0]["candidate_label"]}', "#166534",
                    font_size=10.5)


# ---------------------------------------------------------------------------
# Figure 5: neural-only vs fused ranking
# ---------------------------------------------------------------------------
def build_before_after(canvas) -> None:
    canvas.text(660, 30, "Neural-only ranking vs. neural+symbolic fusion",
                "#0f172a", font_size=15, weight="600")
    canvas.text(330, 60, "Neural-only (embedding similarity alone)",
                "#0f172a", font_size=12.5, weight="600")
    canvas.text(990, 60, "Fused (neural x symbolic, Product)", "#0f172a",
                font_size=12.5, weight="600")
    canvas.line(660, 80, 660, 420, colour="#cbd5e1", width=1.5, dashed=True,
                arrow=False)

    for i, row in enumerate(RANKED_BY_NEURAL):
        y = 110 + i * 75
        style = Colours.CLASS if i == 0 else Colours.SUBJECT_OBJECT
        box(canvas, 150, y, 360, 55, row["candidate_label"], style,
            sub_label=f'neural = {row["neural"]:.2f}')

    for i, row in enumerate(RANKED_BY_PRODUCT):
        y = 110 + i * 75
        style = Colours.CLASS if i == 0 else Colours.SUBJECT_OBJECT
        box(canvas, 810, y, 360, 55, row["candidate_label"], style,
            sub_label=f'fused = {row["product"]:.2f}')

    canvas.text(660, 440,
                'Neural-only would recommend "CLAY PIPE KILN" - the closest '
                'label, but never independently confirmed elsewhere in the '
                'graph. Fusing in the symbolic signal correctly promotes '
                '"kilns" instead.', "#475569", font_size=11.5)


def main() -> None:
    write_outputs(build_architecture, IMG_DIR, "scenario-04-architecture",
                  width=1320, height=440)
    write_outputs(build_ranking, IMG_DIR, "scenario-04-ranking",
                  width=1160, height=560)
    write_outputs(build_quadrant, IMG_DIR, "scenario-04-quadrant",
                  width=960, height=620)
    write_outputs(build_operator_robustness, IMG_DIR,
                  "scenario-04-operator-robustness", width=1180, height=460)
    write_outputs(build_before_after, IMG_DIR, "scenario-04-before-after",
                  width=1320, height=480)

    print(f"Wrote figures to {IMG_DIR}")
    for row in RANKED_BY_PRODUCT:
        print(f'  {row["candidate_label"]:20s} neural={row["neural"]:.2f} '
              f'symbolic={row["symbolic"]:.3f} product={row["product"]:.3f} '
              f'goedel={row["goedel"]:.3f} geomean={row["geomean"]:.3f}')


if __name__ == "__main__":
    main()
