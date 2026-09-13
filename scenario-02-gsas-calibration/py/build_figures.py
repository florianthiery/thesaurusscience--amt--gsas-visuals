#!/usr/bin/env python3
"""Build the three figures for scenario-02 (GSAS as a calibration layer
between an embedding similarity score and AMT input).

Run standalone:
    python scenario-02-gsas-calibration/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-02

Reads:
- ../data/example_concepts.tsv       - real "clay"/"terracotta" candidate
  pair from thesaurusscience, plus an illustrative placeholder cosine value
  (0.78 - NOT a real embedding similarity, see that file's header).
- ../data/gsas_reference_values.tsv  - real precomputed degree-of-connection
  values copied unchanged from the actual GSAS repository's own CSV outputs
  (skos_minimal_degrees.csv, skos_7star_degrees.csv,
  skos_perceptions_stats.csv).

The 7-star exponential function and the perceptions logistic function below
are copied from the real GSAS scripts (skos/skos.py: degree_of_connection,
equivalent_star_for_degree; skos_perceptions/skos_perceptions.py: logistic),
with k=2.0 (7-star), k=0.348/r0=9.73 (perceptions) - the actual defaults in
those scripts, not re-derived approximations.

Writes img/scenario-02-calibration-curves.{svg,png},
img/scenario-02-pipeline.{svg,png} and img/scenario-02-model-comparison.{svg,png}.
"""

from __future__ import annotations

import csv
import math
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

# ---------------------------------------------------------------------------
# GSAS formulas, copied from the real scripts (see module docstring)
# ---------------------------------------------------------------------------
SEVEN_STAR_K = 2.0
PERCEPTIONS_LOGISTIC_K = 0.348
PERCEPTIONS_LOGISTIC_R0 = 9.73
MINIMAL_EXACT_MIN = 0.9382
MINIMAL_CLOSE_MIN = 0.4948


def seven_star_degree(star: float, k: float = SEVEN_STAR_K) -> float:
    """GSAS skos/skos.py: degree_of_connection(star, k). star may be
    fractional in [1, 7] - the GSAS scripts only ever call this at integers
    1..7; treating it as continuous here is a simplification introduced for
    this comparison figure only (see the scenario README), not a GSAS claim.
    """
    x = (star - 1.0) / 6.0
    return (1.0 - math.exp(-k * x)) / (1.0 - math.exp(-k))


def perceptions_logistic(rank: float, k: float = PERCEPTIONS_LOGISTIC_K,
                          r0: float = PERCEPTIONS_LOGISTIC_R0) -> float:
    """GSAS skos_perceptions/skos_perceptions.py: logistic(r, k, r0)."""
    return 1.0 / (1.0 + math.exp(-k * (rank - r0)))


def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    reader = csv.DictReader(rows, delimiter="\t")
    return list(reader)


def load_example():
    row = load_tsv(DATA_DIR / "example_concepts.tsv")[0]
    row["cosine_similarity"] = float(row["cosine_similarity"])
    return row


def load_reference():
    rows = load_tsv(DATA_DIR / "gsas_reference_values.tsv")
    minimal = [r for r in rows if r["model"] == "minimal"]
    seven_star = [r for r in rows if r["model"] == "7star"]
    perceptions = [r for r in rows if r["model"] == "perceptions"]
    four_level = [r for r in rows if r["model"] == "4level"]
    return minimal, seven_star, perceptions, four_level


EXAMPLE = load_example()
MINIMAL, SEVEN_STAR, PERCEPTIONS, FOUR_LEVEL = load_reference()
COSINE = EXAMPLE["cosine_similarity"]  # 0.78, illustrative placeholder

# Derived values used across all three figures (computed once, printed by
# main() so they can be sanity-checked against the figures)
STAR_POS = 1.0 + 6.0 * COSINE                       # continuous star position
NEAREST_STAR = max(1, min(7, round(STAR_POS)))
NEAREST_STAR_DEGREE = float(
    next(r["degree_of_connection"] for r in SEVEN_STAR
         if int(r["rank_or_star"]) == NEAREST_STAR))
NEAREST_STAR_PARENT = next(r["skos_parent"] for r in SEVEN_STAR
                            if int(r["rank_or_star"]) == NEAREST_STAR)
SEVEN_STAR_CONTINUOUS_DEGREE = seven_star_degree(STAR_POS)

RANK_POS = 1.0 + 16.0 * COSINE                      # continuous rank position
PERCEPTIONS_LOGISTIC_DEGREE = perceptions_logistic(RANK_POS)
NEAREST_PHRASE = min(
    PERCEPTIONS, key=lambda r: abs(float(r["degree_of_connection"]) - COSINE))

if COSINE >= MINIMAL_EXACT_MIN:
    MINIMAL_DEGREE, MINIMAL_LABEL = 1.0, "exactMatch"
elif COSINE >= MINIMAL_CLOSE_MIN:
    MINIMAL_DEGREE, MINIMAL_LABEL = 0.9380796757830466, "closeMatch"
else:
    MINIMAL_DEGREE, MINIMAL_LABEL = 0.49465994151156367, "relatedMatch"


# ---------------------------------------------------------------------------
# Small charting helpers (local to this scenario - not generic enough for
# the shared py/viz_utils.py, which stays diagram-primitive-only)
# ---------------------------------------------------------------------------
def _to_px(x, y, x0, y0, w, h, xmin, xmax, ymin, ymax):
    px = x0 + (x - xmin) / (xmax - xmin) * w
    py = y0 + h - (y - ymin) / (ymax - ymin) * h
    return px, py


def draw_axes(canvas, x0, y0, w, h, xmax=1.0, ymax=1.0, xlabel="", ylabel="",
              x_ticks=(0, 0.25, 0.5, 0.75, 1.0), y_ticks=(0, 0.25, 0.5, 0.75, 1.0)):
    canvas.line(x0, y0 + h, x0 + w, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    canvas.line(x0, y0, x0, y0 + h, colour="#94a3b8", width=1.3, arrow=False)
    for xt in x_ticks:
        px, py = _to_px(xt, 0, x0, y0, w, h, 0, xmax, 0, ymax)
        canvas.line(px, y0 + h, px, y0 + h + 6, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(px, y0 + h + 18, f"{xt:g}", "#475569", font_size=10.5)
    for yt in y_ticks:
        px, py = _to_px(0, yt, x0, y0, w, h, 0, xmax, 0, ymax)
        canvas.line(x0 - 6, py, x0, py, colour="#94a3b8", width=1.3, arrow=False)
        canvas.text(x0 - 14, py, f"{yt:g}", "#475569", font_size=10.5, anchor="end")
    if xlabel:
        canvas.text(x0 + w / 2, y0 + h + 36, xlabel, "#334155", font_size=12)
    if ylabel:
        canvas.text(x0, y0 - 16, ylabel, "#334155", font_size=12, anchor="start")


def draw_curve(canvas, fn, x0, y0, w, h, xmax=1.0, ymax=1.0, colour="#334155",
               width=2.2, n=120):
    pts = []
    for i in range(n + 1):
        x = xmax * i / n
        y = fn(x)
        pts.append(_to_px(x, y, x0, y0, w, h, 0, xmax, 0, ymax))
    canvas.polyline(pts, colour=colour, width=width, dashed=False, arrow=False)


def draw_point(canvas, x, y, x0, y0, w, h, xmax, ymax, colour, r=4):
    px, py = _to_px(x, y, x0, y0, w, h, 0, xmax, 0, ymax)
    canvas.ellipse(px, py, r, r, {"fill": colour, "stroke": colour})


# ---------------------------------------------------------------------------
# Figure 1: calibration-curve comparison
# ---------------------------------------------------------------------------
def build_calibration_curves(canvas) -> None:
    x0, y0, w, h = 110, 60, 760, 380

    canvas.text(x0 + w / 2, 26,
                "GSAS calibration models, same [0,1] input axis (this figure "
                "only - see caveat in the README)", "#0f172a", font_size=15,
                weight="600")

    draw_axes(canvas, x0, y0, w, h,
              xlabel="normalised input position x in [0,1]",
              ylabel="degree of connection")

    # 7-star: continuous curve, star = 1 + 6x
    draw_curve(canvas, lambda x: seven_star_degree(1.0 + 6.0 * x), x0, y0, w, h,
               colour="#1d4ed8")
    # Real discrete 7-star points, at their real x = (star-1)/6
    for r in SEVEN_STAR:
        star = int(r["rank_or_star"])
        deg = float(r["degree_of_connection"])
        draw_point(canvas, (star - 1) / 6.0, deg, x0, y0, w, h, 1.0, 1.0, "#1d4ed8")

    # Perceptions: continuous logistic curve, rank = 1 + 16x, PLUS real median points
    draw_curve(canvas, lambda x: perceptions_logistic(1.0 + 16.0 * x), x0, y0, w, h,
               colour="#0f766e")
    for r in PERCEPTIONS:
        rank = int(r["rank_or_star"])
        deg = float(r["degree_of_connection"])
        draw_point(canvas, (rank - 1) / 16.0, deg, x0, y0, w, h, 1.0, 1.0, "#0f766e")

    # Minimal: not a function of x at all - three flat reference levels
    for r in MINIMAL:
        deg = float(r["degree_of_connection"])
        px1, py = _to_px(0, deg, x0, y0, w, h, 0, 1.0, 0, 1.0)
        px2, _ = _to_px(1.0, deg, x0, y0, w, h, 0, 1.0, 0, 1.0)
        canvas.line(px1, py, px2, py, colour="#b45309", width=1.6, dashed=True,
                    arrow=False)

    # Marker at the illustrative cosine value
    mx, _ = _to_px(COSINE, 0, x0, y0, w, h, 0, 1.0, 0, 1.0)
    canvas.line(mx, y0, mx, y0 + h, colour="#7c3aed", width=1.6, dashed=True,
                arrow=False)
    canvas.text(mx, y0 - 10, f"x = {COSINE:g} (placeholder cosine)", "#7c3aed",
                font_size=11.5, weight="600")

    # Legend
    ly = y0 + h + 66
    canvas.line(x0, ly, x0 + 34, ly, colour="#1d4ed8", width=2.2, arrow=False)
    canvas.text(x0 + 44, ly + 4, "7-Star (continuous interpolation, k=2.0)",
                "#0f172a", font_size=11.5, anchor="start")
    canvas.line(x0 + 330, ly, x0 + 364, ly, colour="#0f766e", width=2.2, arrow=False)
    canvas.text(x0 + 374, ly + 4,
                "Perceptions (logistic, k=0.348, r0=9.73) + 17 real medians",
                "#0f172a", font_size=11.5, anchor="start")
    canvas.line(x0, ly + 26, x0 + 34, ly + 26, colour="#b45309", width=1.6,
                dashed=True, arrow=False)
    canvas.text(x0 + 44, ly + 30, "Minimal (3 fixed levels, not a function of x)",
                "#0f172a", font_size=11.5, anchor="start")


# ---------------------------------------------------------------------------
# Figure 2: pipeline (concrete worked example, discrete GSAS usage)
# ---------------------------------------------------------------------------
def build_pipeline(canvas) -> None:
    cy = 110
    oval(canvas, 100, cy, 90, 42, EXAMPLE["concept_a_label"],
         Colours.SUBJECT_OBJECT, sub_label=EXAMPLE["concept_a_id"])
    oval(canvas, 100, cy + 170, 90, 42, EXAMPLE["concept_b_label"],
         Colours.SUBJECT_OBJECT, sub_label=EXAMPLE["concept_b_id"])

    edge_chip(canvas, 330, cy + 85, f"cosine ~ {COSINE:g}", "(placeholder, not real)",
               style=Colours.PROP_META)
    arrow(canvas, 190, cy, 300, cy + 70)
    arrow(canvas, 190, cy + 170, 300, cy + 100)

    box(canvas, 470, cy + 45, 220, 90, "GSAS 7-Star calibration",
        Colours.PROP_META,
        sub_label=f"nearest star = {NEAREST_STAR} (of 7)")
    arrow(canvas, 415, cy + 85, 470, cy + 90)

    box(canvas, 760, cy + 45, 240, 90, NEAREST_STAR_PARENT,
        Colours.OWL,
        sub_label=f"degree_of_connection = {NEAREST_STAR_DEGREE:.4f}")
    arrow(canvas, 690, cy + 90, 760, cy + 90)

    box(canvas, 1070, cy + 30, 210, 120, "AMT-ready assertion",
        Colours.REAL_OBJECT,
        sub_label="graded RDF quad, amt:weight = degree")
    arrow(canvas, 1000, cy + 90, 1070, cy + 90)

    canvas.text(660, cy + 210,
                "The continuous position is only used to pick the nearest of "
                "the 7 discrete GSAS star levels - GSAS itself defines "
                "degrees for those 7 levels, not for arbitrary continuous "
                "input (see README).", "#475569", font_size=11.5)


# ---------------------------------------------------------------------------
# Figure 3: same-input model comparison (bar chart)
# ---------------------------------------------------------------------------
def build_model_comparison(canvas) -> None:
    x0, y0, w, h = 140, 60, 520, 320
    canvas.text(x0 + w / 2, 26,
                f"Same placeholder input (cosine = {COSINE:g}), three models",
                "#0f172a", font_size=15, weight="600")

    draw_axes(canvas, x0, y0, w, h, xlabel="", ylabel="degree of connection",
              x_ticks=(), y_ticks=(0, 0.25, 0.5, 0.75, 1.0))

    bars = [
        ("Minimal", MINIMAL_DEGREE, f"-> {MINIMAL_LABEL}", Colours.PROP_META),
        ("7-Star", NEAREST_STAR_DEGREE, f"-> star {NEAREST_STAR} ({NEAREST_STAR_PARENT})",
         Colours.PROP_META),
        ("Perceptions", float(NEAREST_PHRASE["degree_of_connection"]),
         f"-> \"{NEAREST_PHRASE['level_or_phrase']}\"", Colours.PROP_META),
    ]
    bar_w = 110
    gap = (w - 3 * bar_w) / 4
    for i, (name, value, note, style) in enumerate(bars):
        bx = x0 + gap + i * (bar_w + gap)
        bar_h = value * h
        by = y0 + h - bar_h
        box(canvas, bx, by, bar_w, bar_h, "", style, rx=6)
        canvas.text(bx + bar_w / 2, by - 16, f"{value:.3f}", "#0f172a",
                    font_size=13, weight="600")
        canvas.text(bx + bar_w / 2, y0 + h + 22, name, "#0f172a", font_size=12.5,
                    weight="600")
        canvas.text(bx + bar_w / 2, y0 + h + 42, note, "#475569", font_size=10.5)

    canvas.text(x0 + w / 2, y0 + h + 74,
                "Perceptions gives a visibly different answer here - the "
                "same evidence, read through three calibration philosophies.",
                "#475569", font_size=11.5)



# ---------------------------------------------------------------------------
# Figure 4: the 4-Level model (real GSAS data, not shown in figures 1-3)
# ---------------------------------------------------------------------------
def build_four_level(canvas) -> None:
    x0, y0, w, h = 130, 90, 640, 320
    canvas.text(x0 + w / 2, 34,
                "The 4-Level model: bin means of the 7-Star degrees",
                "#0f172a", font_size=15, weight="600")

    draw_axes(canvas, x0, y0, w, h, ylabel="degree of connection",
              x_ticks=())

    n = len(FOUR_LEVEL)
    bar_w = 100
    gap = (w - n * bar_w) / (n + 1)
    for i, r in enumerate(FOUR_LEVEL):
        val = float(r["degree_of_connection"])
        bx = x0 + gap + i * (bar_w + gap)
        bar_h = val * h
        by = y0 + h - bar_h
        box(canvas, bx, by, bar_w, bar_h, "", Colours.PROP_META, rx=5)
        canvas.text(bx + bar_w / 2, by - 14, f"{val:.3f}", "#0f172a",
                    font_size=12, weight="600")
        label, note = r["level_or_phrase"].split(" (")
        canvas.text(bx + bar_w / 2, y0 + h + 22, label, "#0f172a",
                    font_size=12, weight="600")
        canvas.text(bx + bar_w / 2, y0 + h + 40, "(" + note, "#64748b",
                    font_size=10)

    canvas.text(x0 + w / 2, y0 + h + 72,
                "Each level is the mean of the 7-Star degrees in its bin -",
                "#475569", font_size=11.5)
    canvas.text(x0 + w / 2, y0 + h + 90,
                "a coarser, more communicable view of the same curve used "
                "in figure 1.", "#475569", font_size=11.5)


# ---------------------------------------------------------------------------
# Figure 5: model-selection guide (paraphrased from the GSAS paper's own
# stated use cases for each model, Sections 2.3-2.6 - not verbatim quotes)
# ---------------------------------------------------------------------------
def build_model_selection_guide(canvas) -> None:
    canvas.text(640, 34, "Which GSAS model fits which situation?",
                "#0f172a", font_size=16, weight="600")

    col_w, col_h = 280, 300
    gap = 40
    xs = [40 + i * (col_w + gap) for i in range(4)]
    y = 80

    cards = [
        ("Minimal", ["Only plain SKOS mappings", "exist, no confidence data.",
                     "", "Quick ranking or", "threshold-based filtering."]),
        ("4-Level", ["Human annotation, curation", "or documentation work.",
                     "", "Communicable categories", "matter more than precision."]),
        ("7-Star", ["Technical pipelines and", "research infrastructure.",
                     "", "Fine-grained, reproducible,", "formally reasoned degrees."]),
        ("Perceptions", ["Confidence is expressed in", "natural-language phrases,",
                          "not explicit mapping types.", "",
                          "Empirically grounded degrees."]),
    ]
    for x, (title, lines) in zip(xs, cards):
        rect_shape(canvas, x, y, col_w, col_h, Colours.PROP_META)
        canvas.text(x + col_w / 2, y + 34, title, Colours.PROP_META["text"],
                    font_size=14, weight="600")
        text_block(canvas, x + col_w / 2, y + 160,
                    [(t, "normal", 11.5) for t in lines],
                    Colours.PROP_META["text"], line_height=20)

    canvas.text(640, y + col_h + 40,
                "Paraphrased from the GSAS paper's own stated rationale for "
                "each model (Sections 2.3-2.6) - the four are complementary",
                "#475569", font_size=11.5)
    canvas.text(640, y + col_h + 58,
                "entry points into the same Degree-of-Connection scale, not "
                "a hierarchy from worst to best.", "#475569", font_size=11.5)


def main() -> None:
    write_outputs(build_calibration_curves, IMG_DIR,
                  "scenario-02-calibration-curves", width=980, height=600)
    write_outputs(build_pipeline, IMG_DIR, "scenario-02-pipeline",
                  width=1340, height=340)
    write_outputs(build_model_comparison, IMG_DIR,
                  "scenario-02-model-comparison", width=800, height=520)
    write_outputs(build_four_level, IMG_DIR, "scenario-02-four-level",
                  width=900, height=520)
    write_outputs(build_model_selection_guide, IMG_DIR,
                  "scenario-02-model-selection-guide", width=1280, height=460)

    print(f"Wrote figures to {IMG_DIR}")
    print(f"cosine={COSINE}  7-star continuous degree={SEVEN_STAR_CONTINUOUS_DEGREE:.4f}  "
          f"nearest star={NEAREST_STAR} (degree {NEAREST_STAR_DEGREE:.4f})")
    print(f"perceptions logistic degree={PERCEPTIONS_LOGISTIC_DEGREE:.4f}  "
          f"nearest phrase={NEAREST_PHRASE['level_or_phrase']!r} "
          f"(degree {NEAREST_PHRASE['degree_of_connection']})")
    print(f"minimal model degree={MINIMAL_DEGREE:.4f} ({MINIMAL_LABEL})")


if __name__ == "__main__":
    main()
