#!/usr/bin/env python3
"""Build the seven figures for scenario-07 (exact-match chaining at scale +
per-technique GSAS-style calibration, following up on Lasse Mempel's real
embedding-evaluation results).

Run standalone:
    python scenario-07-exact-match-chaining/py/build_figures.py

Or via the repo orchestrator:
    python main.py --only scenario-07

Style note, deliberately different from scenarios 1-6: no title text or
caption is drawn into any figure here, following the convention documented
in Research-Squirrel-Engineers/bb-5kbc-visuals ("No title header or
source-citation footer is baked in: these are general-purpose diagram
assets meant to be dropped into a slide... each of which supplies its own
caption"). The per-scenario slide sentence and explanatory paragraph live
in TALK_NOTES.md instead - for every scenario in this repository, not only
this one. Canvas size (1750x1000, a 7:4 slide aspect ratio) is the same
convention.

Reads ../data/real_bridges.tsv (three real cross-national exactMatch
"bridges" into shared AAT concepts) and ../data/example_calibration.tsv
(one real closeMatch pair with real per-technique similarity scores, from
Lasse's own Scripts/outputs/).
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
    elbow,
    oval,
    rect_shape,
    text_block,
    write_outputs,
)

DATA_DIR = SCENARIO_ROOT / "data"
IMG_DIR = SCENARIO_ROOT / "img"

WIDTH, HEIGHT = 1750, 1000  # 7:4, matching bb-5kbc-visuals' slide convention


def load_tsv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        rows = [line for line in f if not line.startswith("#")]
    return list(csv.DictReader(rows, delimiter="\t"))


BRIDGES = load_tsv(DATA_DIR / "real_bridges.tsv")
CALIBRATION = load_tsv(DATA_DIR / "example_calibration.tsv")


def bridge_group(name: str) -> list[dict]:
    return [r for r in BRIDGES if r["bridge"] == name]


# ---------------------------------------------------------------------------
# Shared helper: a three-source hub schema (solid asserted edges in, dashed
# inferred edges forming a triangle between the sources)
# ---------------------------------------------------------------------------
def draw_hub_triangle(canvas, cx, cy, radius, group: list[dict],
                       node_rx=150, node_ry=52, hub_rx=170, hub_ry=60,
                       show_weights=True, font_size=13):
    def ellipse_trim(x1, y1, x2, y2, rx1, ry1, rx2, ry2):
        """Exact ellipse-boundary intersection in the direction of the line,
        for each end - so an arrow starts/ends exactly on the oval outline
        regardless of approach angle, not at a uniform circular offset."""
        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy) or 1.0
        ux, uy = dx / dist, dy / dist
        r1 = 1.0 / math.hypot(ux / rx1, uy / ry1)
        r2 = 1.0 / math.hypot(ux / rx2, uy / ry2)
        return (x1 + ux * r1 * 1.05, y1 + uy * r1 * 1.05,
                x2 - ux * r2 * 1.05, y2 - uy * r2 * 1.05)

    angles = [-90, 150, 30]  # top, bottom-left, bottom-right (degrees)
    positions = [
        (cx + radius * math.cos(math.radians(a)),
         cy + radius * math.sin(math.radians(a)))
        for a in angles
    ]
    hub_label = group[0]["object_label"]
    hub_id = group[0]["object_id"]
    oval(canvas, cx, cy, hub_rx, hub_ry, hub_label, Colours.CLASS,
         font_size=font_size, sub_label=hub_id)

    for (x, y), row in zip(positions, group):
        oval(canvas, x, y, node_rx, node_ry, row["subject_label"],
             Colours.SUBJECT_OBJECT, font_size=font_size,
             sub_label=row["subject_id"])
        x1, y1, x2, y2 = ellipse_trim(x, y, cx, cy, node_rx, node_ry,
                                       hub_rx, hub_ry)
        arrow(canvas, x1, y1, x2, y2)
        if show_weights:
            mx, my = (x + cx) / 2, (y + cy) / 2
            edge_chip(canvas, mx, my, "exactMatch", "w=1.0", width=120)

    # dashed inferred edges directly between each pair of source nodes
    for i in range(3):
        (x1, y1) = positions[i]
        (x2, y2) = positions[(i + 1) % 3]
        tx1, ty1, tx2, ty2 = ellipse_trim(x1, y1, x2, y2, node_rx, node_ry,
                                           node_rx, node_ry)
        arrow(canvas, tx1, ty1, tx2, ty2, dashed=True, colour="#dc2626")


# ---------------------------------------------------------------------------
# Figure 1: the flagship bridge/pont/BRIDGE hub schema
# ---------------------------------------------------------------------------
def build_bridge_hub(canvas) -> None:
    draw_hub_triangle(canvas, WIDTH / 2, HEIGHT / 2 + 20, 330,
                       bridge_group("bridge"), font_size=15)


# ---------------------------------------------------------------------------
# Figure 2: axiom representation for the bridge chain
# ---------------------------------------------------------------------------
def build_axiom_representation(canvas) -> None:
    # Only two of the three real assertions feed THIS particular inference
    # (Bruecke exactMatch pont) - the third (BRIDGE) is a separate, equally
    # real input that would feed a different pairwise inference from the
    # same hub (see scenario-07-bridge-hub for all three at once).
    rows = [r for r in bridge_group("bridge") if r["subject_label"] != "BRIDGE"]
    box_w, box_h = 380, 150
    y1 = 160
    gap = 90
    total_w = 2 * box_w + gap
    start_x = (WIDTH - total_w) / 2
    xs = [start_x, start_x + box_w + gap]
    for x, r in zip(xs, rows):
        rect_shape(canvas, x, y1, box_w, box_h, Colours.OWL)
        text_block(canvas, x + box_w / 2, y1 + box_h / 2, [
            (r["subject_label"], "600", 16),
            (f'exactMatch  w=1.0', "normal", 13),
            (r["object_label"], "normal", 13),
        ], Colours.OWL["text"], line_height=26)

    row_y = 480
    inv_w, inv_h = box_w, 150
    inv_x = start_x
    rect_shape(canvas, inv_x, row_y, inv_w, inv_h, Colours.PROP_META)
    text_block(canvas, inv_x + inv_w / 2, row_y + inv_h / 2, [
        ("amt:InverseAxiom", "600", 16),
        ("antecedent = inverse", "normal", 13),
        ("= skos:exactMatch", "normal", 13),
    ], Colours.PROP_META["text"], line_height=24)
    arrow(canvas, xs[1] + box_w / 2, y1 + box_h, inv_x + inv_w / 2, row_y)

    rca_x, rca_w, rca_h = start_x + box_w + gap, box_w, 170
    rect_shape(canvas, rca_x, row_y, rca_w, rca_h, Colours.PROP_META)
    text_block(canvas, rca_x + rca_w / 2, row_y + rca_h / 2, [
        ("amt:RoleChainAxiom", "600", 16),
        ("antecedents = (exactMatch,", "normal", 12.5),
        ("exactMatch)", "normal", 12.5),
        ("consequent = exactMatch", "normal", 12.5),
        ("logic = GoedelLogic", "normal", 12.5),
    ], Colours.PROP_META["text"], line_height=22)
    arrow(canvas, inv_x + inv_w, row_y + inv_h / 2, rca_x, row_y + rca_h / 2)
    arrow(canvas, xs[0] + box_w / 2, y1 + box_h, rca_x + rca_w / 2, row_y)

    out_y = 760
    out_w, out_h = box_w, 150
    out_x = start_x + (box_w + gap) / 2
    rect_shape(canvas, out_x, out_y, out_w, out_h, Colours.REAL_OBJECT)
    text_block(canvas, out_x + out_w / 2, out_y + out_h / 2, [
        (f'{rows[0]["subject_label"]} exactMatch', "600", 15),
        (f'{rows[1]["subject_label"]}', "600", 15),
        ("w = 1.0", "normal", 13),
        ("(SHACL-validated, inferred)", "normal", 12),
    ], Colours.REAL_OBJECT["text"], line_height=23)
    arrow(canvas, rca_x + rca_w / 2, row_y + rca_h, out_x + out_w / 2, out_y)


# ---------------------------------------------------------------------------
# Figure 3: the pattern repeats (aqueduct + barracks, compact)
# ---------------------------------------------------------------------------
def build_pattern_repeats(canvas) -> None:
    draw_hub_triangle(canvas, WIDTH * 0.27, HEIGHT / 2 + 10, 260,
                       bridge_group("aqueduct"), node_rx=125, node_ry=46,
                       hub_rx=145, hub_ry=52, show_weights=False,
                       font_size=12.5)
    draw_hub_triangle(canvas, WIDTH * 0.73, HEIGHT / 2 + 10, 260,
                       bridge_group("barracks"), node_rx=125, node_ry=46,
                       hub_rx=145, hub_ry=52, show_weights=False,
                       font_size=12.5)
    canvas.line(WIDTH / 2, 90, WIDTH / 2, HEIGHT - 90, colour="#cbd5e1",
                width=1.5, dashed=True, arrow=False)


# ---------------------------------------------------------------------------
# Figure 4: calibration in the graph (petit appareil / brickwork)
# ---------------------------------------------------------------------------
def build_calibration_pipeline(canvas) -> None:
    rows = {r["technique"]: r for r in CALIBRATION}
    e5 = rows["emb_e5-large-instruct_full"]

    box_w, box_h = 340, 220
    y = HEIGHT / 2 - box_h / 2
    gap = 90
    xs = [70, 70 + box_w + gap, 70 + 2 * (box_w + gap), 70 + 3 * (box_w + gap)]

    rect_shape(canvas, xs[0], y, box_w, box_h, Colours.SUBJECT_OBJECT)
    text_block(canvas, xs[0] + box_w / 2, y + box_h / 2, [
        ("SSSOM row", "600", 15),
        ("", "normal", 6),
        (e5["subject_label"], "normal", 12.5),
        ("skos:closeMatch", "normal", 12),
        (e5["object_label"], "normal", 12.5),
    ], Colours.SUBJECT_OBJECT["text"], line_height=22)

    rect_shape(canvas, xs[1], y, box_w, box_h, Colours.OWL)
    text_block(canvas, xs[1] + box_w / 2, y + box_h / 2, [
        ("raw technique score", "600", 14),
        ("", "normal", 6),
        (f'e5-large-instruct: {float(e5["raw_value"]):.3f}', "normal", 12),
        ("", "normal", 4),
        (f'technique\u2019s own reference points:', "normal", 10.5),
        (f'random pairs ~ {e5["random_pair_mean"]}', "normal", 10.5),
        (f'closeMatch ~ {e5["closematch_mean"]}', "normal", 10.5),
        (f'exactMatch ~ {e5["exactmatch_mean"]}', "normal", 10.5),
    ], Colours.OWL["text"], line_height=19)
    arrow(canvas, xs[0] + box_w, y + box_h / 2, xs[1], y + box_h / 2)

    rect_shape(canvas, xs[2], y, box_w, box_h, Colours.PROP_META)
    text_block(canvas, xs[2] + box_w / 2, y + box_h / 2, [
        ("calibration step", "600", 15),
        ("", "normal", 6),
        ("place raw value against this", "normal", 11.5),
        ("technique\u2019s own real distribution,", "normal", 11.5),
        ("not an absolute threshold", "normal", 11.5),
        ("", "normal", 6),
        ("(no GSAS model covers embedding", "normal", 10.5),
        ("techniques - see scenario README)", "normal", 10.5),
    ], Colours.PROP_META["text"], line_height=19)
    arrow(canvas, xs[1] + box_w, y + box_h / 2, xs[2], y + box_h / 2)

    rect_shape(canvas, xs[3], y, box_w, box_h, Colours.TERM)
    text_block(canvas, xs[3] + box_w / 2, y + box_h / 2, [
        ("calibrated band", "600", 15),
        ("", "normal", 8),
        (e5["calibrated_band"], "600", 22),
        ("", "normal", 8),
        ("(GSAS 4-Level vocabulary,", "normal", 10.5),
        ("not a GSAS value)", "normal", 10.5),
    ], Colours.TERM["text"], line_height=20)
    arrow(canvas, xs[2] + box_w, y + box_h / 2, xs[3], y + box_h / 2)


# ---------------------------------------------------------------------------
# Figure 5: multi-provenance (same pair, three technique-specific edges)
# ---------------------------------------------------------------------------
def build_multi_provenance(canvas) -> None:
    rows = {r["technique"]: r for r in CALIBRATION}
    left_x, right_x = 280, WIDTH - 280
    cy = HEIGHT / 2

    subj = rows["emb_e5-large-instruct_full"]["subject_label"]
    obj = rows["emb_e5-large-instruct_full"]["object_label"]
    oval(canvas, left_x, cy, 190, 70, subj, Colours.SUBJECT_OBJECT,
         font_size=16)
    oval(canvas, right_x, cy, 190, 70, obj, Colours.SUBJECT_OBJECT,
         font_size=16)

    techniques = [
        ("emb_e5-large-instruct_full", "e5-large-instruct", "#1d4ed8", -220),
        ("emb_m2v-bge-m3-1024d_full", "m2v-bge-m3", "#dc2626", 0),
        ("str_levenshtein_full", "Levenshtein (string)", "#166534", 220),
    ]
    for key, label, colour, dy in techniques:
        r = rows[key]
        y = cy + dy
        elbow(canvas, [(left_x + 190, cy), (left_x + 260, y),
                       (right_x - 260, y), (right_x - 190, cy)],
              colour=colour, width=2.4, dashed=(key != "emb_e5-large-instruct_full"))
        edge_chip(canvas, WIDTH / 2, y - 34 if dy <= 0 else y + 34,
                  label, f'{float(r["raw_value"]):.3f}',
                  style={"fill": colour, "stroke": "#000000",
                         "text": "#ffffff"}, width=220)


# ---------------------------------------------------------------------------
# Figure 6: safe (curated) vs. candidate (calibrated) contrast
# ---------------------------------------------------------------------------
def build_safe_vs_candidate(canvas) -> None:
    col_w, col_h = 720, 760
    y = (HEIGHT - col_h) / 2
    xs = [80, 80 + col_w + 90]

    left_body = [
        ("Story A - curated", "600", 22),
        ("", "normal", 10),
        ("Both edges are real, asserted", "normal", 14),
        ("skos:exactMatch rows.", "normal", 14),
        ("", "normal", 10),
        ("GSAS degree = 1.0 for both,", "normal", 14),
        ("unconditionally - no calibration", "normal", 14),
        ("step involved.", "normal", 14),
        ("", "normal", 14),
        ("amt:RoleChainAxiom composes", "normal", 14),
        ("them with near-full confidence.", "normal", 14),
        ("", "normal", 10),
        ("Edge style: solid", "600", 13),
    ]
    right_body = [
        ("Story B - candidate", "600", 22),
        ("", "normal", 10),
        ("The edge is a raw similarity", "normal", 14),
        ("score from an embedding or", "normal", 14),
        ("string technique - not yet a", "normal", 14),
        ("curated mapping.", "normal", 14),
        ("", "normal", 14),
        ("Needs a calibration step before", "normal", 14),
        ("amt:weight means anything -", "normal", 14),
        ("see scenario-07-calibration-pipeline.", "normal", 14),
        ("", "normal", 10),
        ("Edge style: dashed", "600", 13),
    ]
    styles = [Colours.REAL_OBJECT, Colours.TERM]
    for x, body, style in zip(xs, [left_body, right_body], styles):
        rect_shape(canvas, x, y, col_w, col_h, style)
        text_block(canvas, x + col_w / 2, y + col_h / 2 - 40, body,
                    style["text"], line_height=30)


# ---------------------------------------------------------------------------
# Figure 7: scope boundary - modelled here vs. outlook
# ---------------------------------------------------------------------------
def build_scope_boundary(canvas) -> None:
    col_w, col_h = 720, 760
    y = (HEIGHT - col_h) / 2
    xs = [80, 80 + col_w + 90]

    modelled = [
        ("Modelled in this scenario", "600", 20),
        ("", "normal", 12),
        ("- exactMatch chaining across", "normal", 14),
        ("  real cross-national bridges", "normal", 14),
        ("  (amt:InverseAxiom +", "normal", 14),
        ("  amt:RoleChainAxiom)", "normal", 14),
        ("", "normal", 10),
        ("- per-technique calibration of a", "normal", 14),
        ("  raw similarity score into a", "normal", 14),
        ("  GSAS-vocabulary band", "normal", 14),
    ]
    outlook = [
        ("Outlook - not modelled here", "600", 20),
        ("", "normal", 12),
        ("- candidate generation: n-nearest", "normal", 14),
        ("  neighbours across the whole AAT", "normal", 14),
        ("  for a source concept", "normal", 14),
        ("", "normal", 10),
        ("- checking recall against real", "normal", 14),
        ("  training-data mapping partners", "normal", 14),
        ("", "normal", 10),
        ("- LLM re-ranking with context", "normal", 14),
        ("  (parent, siblings, scope note)", "normal", 14),
    ]
    styles = [Colours.PROP_META, Colours.NEUTRAL_PROCESS]
    for x, body, style in zip(xs, [modelled, outlook], styles):
        rect_shape(canvas, x, y, col_w, col_h, style)
        text_block(canvas, x + col_w / 2, y + col_h / 2 - 30, body,
                    style["text"], line_height=28)


def main() -> None:
    write_outputs(build_bridge_hub, IMG_DIR, "scenario-07-bridge-hub",
                  width=WIDTH, height=HEIGHT)
    write_outputs(build_axiom_representation, IMG_DIR,
                  "scenario-07-axiom-representation", width=WIDTH, height=HEIGHT)
    write_outputs(build_pattern_repeats, IMG_DIR, "scenario-07-pattern-repeats",
                  width=WIDTH, height=HEIGHT)
    write_outputs(build_calibration_pipeline, IMG_DIR,
                  "scenario-07-calibration-pipeline", width=WIDTH, height=HEIGHT)
    write_outputs(build_multi_provenance, IMG_DIR,
                  "scenario-07-multi-provenance", width=WIDTH, height=HEIGHT)
    write_outputs(build_safe_vs_candidate, IMG_DIR,
                  "scenario-07-safe-vs-candidate", width=WIDTH, height=HEIGHT)
    write_outputs(build_scope_boundary, IMG_DIR, "scenario-07-scope-boundary",
                  width=WIDTH, height=HEIGHT)

    print(f"Wrote figures to {IMG_DIR}")


if __name__ == "__main__":
    main()
