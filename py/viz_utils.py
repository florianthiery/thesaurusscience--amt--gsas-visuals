#!/usr/bin/env python3
"""Shared drawing helpers for thesaurusscience--amt--gsas-visuals.

Every scenario's ``py/build_figures.py`` defines each figure ONCE, as a
function ``build(canvas)`` that calls the small set of primitives below
(``box``, ``oval``, ``arrow``, ``edge_chip``, ...). ``write_outputs`` then
calls that function twice, once against each of two Canvas backends:

- ``SVGCanvas``  - accumulates an SVG string (the vector deliverable).
- ``PNGCanvas``  - rasterises directly with Pillow's ``ImageDraw`` (the
  raster deliverable).

Geometry is defined exactly once; only the backend differs. This replaced an
earlier version that generated SVG and then rasterised it via ``cairosvg``.
cairosvg's Python package installs fine everywhere, but at import time it
dlopen()s a *native* Cairo library (``libcairo-2.dll`` on Windows) that pip
does not and cannot install - this broke on Florian's Windows machine with
"no library called 'cairo-2' was found" (2026-09-13). Rendering directly
with Pillow avoids any native/system dependency: Pillow ships self-contained
wheels for every platform, including a built-in scalable font
(``ImageFont.load_default(size=...)``, Pillow >= 10.1) so no external font
file is needed either.

Usage from a scenario script::

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "py"))
    from viz_utils import Colours, box, oval, arrow, edge_chip, write_outputs

    def build(canvas):
        box(canvas, 10, 10, 100, 40, "Hello", Colours.SUBJECT_OBJECT)

    write_outputs(build, out_dir, "my-figure", width=400, height=200)
"""

from __future__ import annotations

import math
from pathlib import Path

# No datetime.now() anywhere in this module or in any script that imports it -
# a fixed release string is used wherever a date is needed, so a rebuild is
# byte-identical when nothing has changed.
RELEASE = "2026-09-13"

FONT_FAMILY = "Segoe UI, Helvetica, Arial, sans-serif"  # SVG only; PNG uses
                                                          # Pillow's built-in
                                                          # scalable font


# ---------------------------------------------------------------------------
# Colour scheme
# ---------------------------------------------------------------------------
# Florian Thiery's standing colour convention for RDF/ontology node types,
# applied here to hand-built diagrams instead of Mermaid. Six categories are
# defined; a seventh ("NEUTRAL_PROCESS") is added for pipeline-stage boxes
# that are not themselves RDF node types (see the scenario-01 data-flow
# figure) and is NOT part of the original convention - flag if this reads as
# a misuse of the scheme rather than a deliberate, called-out extension.
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
# Backend 1: SVG (accumulates markup, arrowhead markers de-duplicated by colour)
# ---------------------------------------------------------------------------
class SVGCanvas:
    def __init__(self, width: int, height: int, bg: str = "#ffffff"):
        self.width = width
        self.height = height
        self.bg = bg
        self._body: list[str] = []
        self._markers: dict[str, str] = {}  # colour -> marker id

    def _marker_id(self, colour: str) -> str:
        if colour not in self._markers:
            marker_id = f"arrowhead_{len(self._markers)}"
            self._markers[colour] = marker_id
        return self._markers[colour]

    def rect(self, x, y, w, h, style, rx=10, dashed=False):
        dash = ' stroke-dasharray="6,4"' if dashed else ""
        self._body.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx}" ry="{rx}" fill="{style["fill"]}" '
            f'stroke="{style["stroke"]}" stroke-width="1.5"{dash}/>'
        )

    def ellipse(self, cx, cy, rx, ry, style):
        self._body.append(
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="1.5"/>'
        )

    def line(self, x1, y1, x2, y2, colour="#334155", width=1.8, dashed=False,
             arrow=True):
        dash = ' stroke-dasharray="7,5"' if dashed else ""
        marker = f' marker-end="url(#{self._marker_id(colour)})"' if arrow else ""
        self._body.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{colour}" stroke-width="{width}"{dash}{marker}/>'
        )

    def polyline(self, points, colour="#334155", width=1.8, dashed=False,
                 arrow=True):
        dash = ' stroke-dasharray="7,5"' if dashed else ""
        marker = f' marker-end="url(#{self._marker_id(colour)})"' if arrow else ""
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        self._body.append(
            f'<polyline points="{pts}" fill="none" stroke="{colour}" '
            f'stroke-width="{width}"{dash}{marker}/>'
        )

    def text(self, cx, cy, text, colour, font_size=13, weight="normal",
              anchor="middle"):
        fw = ' font-weight="600"' if weight in ("600", "bold", "700") else ""
        self._body.append(
            f'<text x="{cx:.1f}" y="{cy:.1f}" text-anchor="{anchor}" '
            f'dominant-baseline="middle" font-family="{FONT_FAMILY}" '
            f'font-size="{font_size}"{fw} fill="{colour}">{esc(text)}</text>'
        )

    def render(self) -> str:
        defs = "".join(
            f'<marker id="{marker_id}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{colour}"/></marker>'
            for colour, marker_id in self._markers.items()
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'viewBox="0 0 {self.width} {self.height}" '
            f'width="{self.width}" height="{self.height}">\n'
            f'<defs>{defs}</defs>\n'
            f'<rect x="0" y="0" width="{self.width}" height="{self.height}" '
            f'fill="{self.bg}"/>\n'
            f'{"".join(self._body)}\n</svg>\n'
        )


# ---------------------------------------------------------------------------
# Backend 2: PNG (pure Pillow - no cairo, no reportlab, no external font)
# ---------------------------------------------------------------------------
class PNGCanvas:
    def __init__(self, width: int, height: int, bg: str = "#ffffff",
                 scale: float = 2.0):
        from PIL import Image, ImageDraw  # deferred: --list/--dry-run stay light

        self.width = width
        self.height = height
        self.scale = scale
        self._img = Image.new("RGB", (round(width * scale), round(height * scale)),
                               bg)
        self._draw = ImageDraw.Draw(self._img)
        self._font_cache: dict[int, object] = {}

    def _s(self, v):
        return v * self.scale

    def _font(self, size):
        from PIL import ImageFont

        px = round(size * self.scale)
        if px not in self._font_cache:
            self._font_cache[px] = ImageFont.load_default(size=px)
        return self._font_cache[px]

    def rect(self, x, y, w, h, style, rx=10, dashed=False):
        x0, y0, x1, y1 = self._s(x), self._s(y), self._s(x + w), self._s(y + h)
        radius = self._s(rx)
        outline_w = max(1, round(self._s(1.5)))
        if dashed:
            self._draw.rounded_rectangle([x0, y0, x1, y1], radius=radius,
                                          fill=style["fill"])
            self._dashed_rounded_rect(x0, y0, x1, y1, radius, style["stroke"])
        else:
            self._draw.rounded_rectangle(
                [x0, y0, x1, y1], radius=radius, fill=style["fill"],
                outline=style["stroke"], width=outline_w,
            )

    def ellipse(self, cx, cy, rx, ry, style):
        x0, y0 = self._s(cx - rx), self._s(cy - ry)
        x1, y1 = self._s(cx + rx), self._s(cy + ry)
        outline_w = max(1, round(self._s(1.5)))
        self._draw.ellipse([x0, y0, x1, y1], fill=style["fill"],
                            outline=style["stroke"], width=outline_w)

    def line(self, x1, y1, x2, y2, colour="#334155", width=1.8, dashed=False,
             arrow=True):
        p1 = (self._s(x1), self._s(y1))
        p2 = (self._s(x2), self._s(y2))
        w = max(1, round(self._s(width)))
        if dashed:
            self._dashed_segment(p1, p2, colour, w)
        else:
            self._draw.line([p1, p2], fill=colour, width=w)
        if arrow:
            self._arrowhead(p1, p2, colour)

    def polyline(self, points, colour="#334155", width=1.8, dashed=False,
                 arrow=True):
        pts = [(self._s(x), self._s(y)) for x, y in points]
        w = max(1, round(self._s(width)))
        for a, b in zip(pts, pts[1:]):
            if dashed:
                self._dashed_segment(a, b, colour, w)
            else:
                self._draw.line([a, b], fill=colour, width=w)
        if arrow and len(pts) >= 2:
            self._arrowhead(pts[-2], pts[-1], colour)

    def text(self, cx, cy, text, colour, font_size=13, weight="normal",
              anchor="middle"):
        font = self._font(font_size)
        x, y = self._s(cx), self._s(cy)
        bbox = self._draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if anchor == "middle":
            x -= tw / 2
        y -= th / 2 + bbox[1]
        bold = weight in ("600", "bold", "700")
        offsets = [(0, 0), (self._s(0.4), 0)] if bold else [(0, 0)]
        for dx, dy in offsets:
            self._draw.text((x + dx, y + dy), text, font=font, fill=colour)

    def _arrowhead(self, p_from, p_to, colour):
        angle = math.atan2(p_to[1] - p_from[1], p_to[0] - p_from[0])
        size = self._s(9)
        spread = math.radians(24)
        p2 = (p_to[0] - size * math.cos(angle - spread),
              p_to[1] - size * math.sin(angle - spread))
        p3 = (p_to[0] - size * math.cos(angle + spread),
              p_to[1] - size * math.sin(angle + spread))
        self._draw.polygon([p_to, p2, p3], fill=colour)

    def _dashed_segment(self, p1, p2, colour, width, dash=None, gap=None):
        dash = dash if dash is not None else self._s(7)
        gap = gap if gap is not None else self._s(5)
        x1, y1 = p1
        x2, y2 = p2
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            return
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        pos = 0.0
        while pos < length:
            seg_end = min(pos + dash, length)
            self._draw.line(
                [(x1 + ux * pos, y1 + uy * pos),
                 (x1 + ux * seg_end, y1 + uy * seg_end)],
                fill=colour, width=width,
            )
            pos += dash + gap

    def _dashed_rounded_rect(self, x0, y0, x1, y1, radius, colour):
        # Straight-segment approximation (corners are not rounded in the
        # dash pattern itself, only the fill beneath is) - visually close
        # enough at diagram scale and much simpler than dashing an arc.
        self._dashed_segment((x0 + radius, y0), (x1 - radius, y0), colour, 2)
        self._dashed_segment((x1, y0 + radius), (x1, y1 - radius), colour, 2)
        self._dashed_segment((x1 - radius, y1), (x0 + radius, y1), colour, 2)
        self._dashed_segment((x0, y1 - radius), (x0, y0 + radius), colour, 2)

    def save(self, path):
        self._img.save(path, "PNG")


# ---------------------------------------------------------------------------
# Backend-agnostic primitives (used by scenario build_figures.py scripts)
# ---------------------------------------------------------------------------
def box(canvas, x, y, w, h, label, style, rx=10, font_size=13, sub_label=None,
        dashed=False):
    """A rounded rectangle with one or two lines of centred label text."""
    canvas.rect(x, y, w, h, style, rx=rx, dashed=dashed)
    cx, cy = x + w / 2, y + h / 2
    if sub_label:
        canvas.text(cx, cy - 6, label, style["text"], font_size=font_size,
                    weight="600")
        canvas.text(cx, cy + 12, sub_label, style["text"],
                    font_size=font_size - 2)
    else:
        canvas.text(cx, cy, label, style["text"], font_size=font_size,
                    weight="600")


def oval(canvas, cx, cy, rx, ry, label, style, font_size=13, sub_label=None,
         lines=None, line_height=15):
    """An ellipse with centred label text.

    Either pass ``label`` (+ optional ``sub_label``) for the simple one- or
    two-line case, or ``lines`` - a list of plain strings or
    ``(text, weight, size)`` tuples - for full control over an arbitrary
    number of stacked lines, vertically centred as a block on ``cy``.
    """
    canvas.ellipse(cx, cy, rx, ry, style)
    if lines is not None:
        text_block(canvas, cx, cy, lines, style["text"], font_size, line_height)
    elif sub_label:
        canvas.text(cx, cy - 6, label, style["text"], font_size=font_size,
                    weight="600")
        canvas.text(cx, cy + 12, sub_label, style["text"],
                    font_size=font_size - 3)
    else:
        canvas.text(cx, cy, label, style["text"], font_size=font_size,
                    weight="600")


def text_block(canvas, cx, cy, lines, colour, font_size=12, line_height=15):
    """Render a list of lines centred as a block around (cx, cy).

    Each entry is either a plain string (normal weight, ``font_size``) or a
    ``(text, weight, size)`` tuple overriding either.
    """
    norm = []
    for entry in lines:
        if isinstance(entry, str):
            norm.append((entry, "normal", font_size))
        else:
            norm.append(entry)
    total_h = line_height * (len(norm) - 1)
    top_y = cy - total_h / 2
    for i, (text, weight, size) in enumerate(norm):
        canvas.text(cx, top_y + i * line_height, text, colour,
                    font_size=size, weight=weight)


def arrow(canvas, x1, y1, x2, y2, dashed=False, colour="#334155", width=1.8):
    canvas.line(x1, y1, x2, y2, colour=colour, width=width, dashed=dashed,
                arrow=True)


def elbow(canvas, points, dashed=False, colour="#334155", width=1.8):
    """A right-angle polyline connector through the given (x, y) points."""
    canvas.polyline(points, colour=colour, width=width, dashed=dashed, arrow=True)


def edge_chip(canvas, cx, cy, label, sub_label=None, style=None, font_size=11,
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
    box(canvas, x, y, w, h, label, style, rx=h / 2 if not sub_label else 8,
        font_size=font_size, sub_label=sub_label, dashed=dashed)


def rect_shape(canvas, x, y, w, h, style, rx=10, dashed=False):
    """A rounded rectangle with no text - pair with ``text_block`` for full
    control over multi-line, multi-size label content."""
    canvas.rect(x, y, w, h, style, rx=rx, dashed=dashed)


# ---------------------------------------------------------------------------
# Entry point used by every scenario's build_figures.py
# ---------------------------------------------------------------------------
def write_outputs(build_fn, out_dir: Path, name: str, width: int, height: int,
                   scale: float = 2.0):
    """Call ``build_fn(canvas)`` once per backend and write both outputs.

    ``build_fn`` must take a single argument (the canvas) and draw the
    figure onto it using the primitives above; it must not return anything
    or hold state between calls, since it runs twice (once for SVG, once for
    PNG) against two different, independent canvas instances.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    svg_canvas = SVGCanvas(width, height)
    build_fn(svg_canvas)
    svg_path = out_dir / f"{name}.svg"
    svg_path.write_text(svg_canvas.render(), encoding="utf-8", newline="\n")

    png_canvas = PNGCanvas(width, height, scale=scale)
    build_fn(png_canvas)
    png_path = out_dir / f"{name}.png"
    png_canvas.save(png_path)

    return svg_path, png_path
