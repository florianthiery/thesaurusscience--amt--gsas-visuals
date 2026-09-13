#!/usr/bin/env python3
"""Shared SVG/PNG helpers for thesaurusscience--amt--gsas-visuals.

Every scenario's ``py/build_figures.py`` imports this module for: the fixed
colour scheme, small SVG-primitive builders (boxes, ovals, arrows, edge-label
chips) and a deterministic SVG-to-PNG export step. Diagrams are hand-built SVG
(no matplotlib/graphviz dependency), matching the diagram style used across
Florian Thiery's other -visuals repositories.

Usage from a scenario script::

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "py"))
    from viz_utils import Colours, svg_document, box, oval, arrow, edge_chip, write_outputs
"""

from __future__ import annotations

from pathlib import Path

import cairosvg

# No datetime.now() anywhere in this module or in any script that imports it -
# a fixed release string is used wherever a date is needed, so a rebuild is
# byte-identical when nothing has changed.
RELEASE = "2026-09-13"

FONT_FAMILY = "Segoe UI, Helvetica, Arial, sans-serif"

# ---------------------------------------------------------------------------
# Colour scheme
# ---------------------------------------------------------------------------
# Florian Thiery's standing colour convention for RDF/ontology node types,
# applied here to hand-built SVG instead of Mermaid. Six categories are
# defined; a seventh ("NEUTRAL_PROCESS") is added for pipeline-stage boxes
# that are not themselves RDF node types (see the scenario-01 data-flow
# figure) and is NOT part of the original convention - flag if this reads as
# a misuse of the scheme rather than a deliberate extension.
class Colours:
    SUBJECT_OBJECT = {"fill": "#e2e8f0", "stroke": "#000000", "text": "#000000"}
    REAL_OBJECT = {"fill": "#166534", "stroke": "#000000", "text": "#ffffff"}
    CLASS = {"fill": "#9a3412", "stroke": "#000000", "text": "#ffffff"}
    TERM = {"fill": "#4c1d95", "stroke": "#000000", "text": "#ffffff"}
    OWL = {"fill": "#ffffff", "stroke": "#000000", "text": "#000000"}
    PROP_META = {"fill": "#fbbf24", "stroke": "#000000", "text": "#000000"}
    # Not part of Florian's original six - a neutral style for generic
    # pipeline/process boxes that are not RDF node types.
    NEUTRAL_PROCESS = {"fill": "#f8fafc", "stroke": "#475569", "text": "#0f172a"}


def esc(s: str) -> str:
    """Escape text for safe inclusion in SVG content."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------------------------------------------------------------------------
# Primitives
# ---------------------------------------------------------------------------
def box(x, y, w, h, label, style, rx=10, font_size=13, sub_label=None,
        dashed=False):
    """A rounded rectangle with one or two lines of centred label text."""
    dash = ' stroke-dasharray="6,4"' if dashed else ""
    parts = [
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx}" ry="{rx}" fill="{style["fill"]}" stroke="{style["stroke"]}" '
        f'stroke-width="1.5"{dash}/>'
    ]
    cx, cy = x + w / 2, y + h / 2
    if sub_label:
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - 6:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size}" font-weight="600" fill="{style["text"]}">'
            f'{esc(label)}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 12:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size - 2}" fill="{style["text"]}">'
            f'{esc(sub_label)}</text>'
        )
    else:
        parts.append(
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size}" font-weight="600" fill="{style["text"]}">'
            f'{esc(label)}</text>'
        )
    return "\n".join(parts)


def rect_shape(x, y, w, h, style, rx=10, dashed=False):
    """A rounded rectangle with no text - pair with ``_text_block`` for full
    control over multi-line, multi-size label content."""
    dash = ' stroke-dasharray="6,4"' if dashed else ""
    return (
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx}" ry="{rx}" fill="{style["fill"]}" stroke="{style["stroke"]}" '
        f'stroke-width="1.5"{dash}/>'
    )


def text_block(cx, cy, lines, colour, font_size=12, line_height=15):
    """Public wrapper around the internal multi-line text renderer."""
    return _text_block(cx, cy, lines, colour, font_size, line_height)


def oval(cx, cy, rx, ry, label, style, font_size=13, sub_label=None,
         lines=None, line_height=15):
    """An ellipse with centred label text.

    Either pass ``label`` (+ optional ``sub_label``) for the simple one- or
    two-line case, or pass ``lines`` - a list of ``(text, weight, size)``
    tuples, or plain strings (rendered at ``font_size``/normal weight) - for
    full control over an arbitrary number of stacked lines, vertically
    centred as a block on ``cy``.
    """
    parts = [
        f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="1.5"/>'
    ]
    if lines is not None:
        parts.append(_text_block(cx, cy, lines, style["text"], font_size,
                                  line_height))
    elif sub_label:
        parts.append(
            f'<text x="{cx:.1f}" y="{cy - 6:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size}" font-weight="600" fill="{style["text"]}">'
            f'{esc(label)}</text>'
        )
        parts.append(
            f'<text x="{cx:.1f}" y="{cy + 12:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size - 3}" fill="{style["text"]}">'
            f'{esc(sub_label)}</text>'
        )
    else:
        parts.append(
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size}" font-weight="600" fill="{style["text"]}">'
            f'{esc(label)}</text>'
        )
    return "\n".join(parts)


def _text_block(cx, cy, lines, colour, font_size, line_height):
    """Render a list of lines centred as a block around (cx, cy).

    Each entry in ``lines`` is either a plain string (normal weight,
    ``font_size``) or a ``(text, weight, size)`` tuple overriding either.
    """
    norm = []
    for entry in lines:
        if isinstance(entry, str):
            norm.append((entry, "normal", font_size))
        else:
            text, weight, size = entry
            norm.append((text, weight, size))
    total_h = line_height * (len(norm) - 1)
    top_y = cy - total_h / 2
    parts = []
    for i, (text, weight, size) in enumerate(norm):
        fw = f' font-weight="{weight}"' if weight != "normal" else ""
        parts.append(
            f'<text x="{cx:.1f}" y="{top_y + i * line_height:.1f}" '
            f'text-anchor="middle" dominant-baseline="middle" '
            f'font-family="{FONT_FAMILY}" font-size="{size}"{fw} '
            f'fill="{colour}">{esc(text)}</text>'
        )
    return "\n".join(parts)


def arrow(x1, y1, x2, y2, dashed=False, colour="#334155", width=1.8,
          marker_id="arrowhead"):
    """A straight connector with an arrowhead marker at (x2, y2)."""
    dash = ' stroke-dasharray="7,5"' if dashed else ""
    return (
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
        f'stroke="{colour}" stroke-width="{width}"{dash} '
        f'marker-end="url(#{marker_id})"/>'
    )


def elbow(points, dashed=False, colour="#334155", width=1.8,
          marker_id="arrowhead"):
    """A right-angle polyline connector through the given (x, y) points."""
    dash = ' stroke-dasharray="7,5"' if dashed else ""
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return (
        f'<polyline points="{pts}" fill="none" stroke="{colour}" '
        f'stroke-width="{width}"{dash} marker-end="url(#{marker_id})"/>'
    )


def edge_chip(cx, cy, label, sub_label=None, style=None, font_size=11,
              width=None, height=None, dashed=False):
    """A small rounded chip used to annotate an edge (predicate + weight).

    Defaults to the PropMeta colour, matching "PropMeta/Property(Metadata)"
    in Florian's scheme: an edge label is exactly a property/metadata
    annotation on the connection it sits next to.
    """
    style = style or Colours.PROP_META
    longest = max(len(label), len(sub_label or ""))
    w = width or (8 * longest + 20)
    h = height or (34 if sub_label else 20)
    x, y = cx - w / 2, cy - h / 2
    return box(x, y, w, h, label, style, rx=h / 2 if not sub_label else 8,
               font_size=font_size, sub_label=sub_label, dashed=dashed)


def defs_arrowhead(marker_id="arrowhead", colour="#334155"):
    return (
        f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{colour}"/></marker>'
    )


def svg_document(width, height, body, defs="", bg="#ffffff"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}">\n'
        f'<defs>{defs}</defs>\n'
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="{bg}"/>\n'
        f'{body}\n'
        f'</svg>\n'
    )


# ---------------------------------------------------------------------------
# Deterministic export
# ---------------------------------------------------------------------------
def write_outputs(svg_str: str, out_dir: Path, name: str, scale: float = 2.0):
    """Write ``<name>.svg`` and a rasterised ``<name>.png`` into ``out_dir``.

    Byte-reproducibility: the SVG is written with a fixed newline convention
    and no embedded content that varies run to run (no timestamps, no random
    ids - every id in the primitives above is caller-supplied, never
    generated). cairosvg does not embed a creation timestamp into the PNG, so
    no further pinning (cf. SOURCE_DATE_EPOCH / svg.hashsalt for matplotlib)
    is needed here; verified by running the build twice and comparing output
    with ``cmp``.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"{name}.svg"
    png_path = out_dir / f"{name}.png"
    svg_path.write_text(svg_str, encoding="utf-8", newline="\n")
    cairosvg.svg2png(
        url=str(svg_path),
        write_to=str(png_path),
        scale=scale,
        background_color="white",
    )
    return svg_path, png_path
