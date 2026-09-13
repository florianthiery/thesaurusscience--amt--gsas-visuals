#!/usr/bin/env python3
"""Orchestrator for thesaurusscience--amt--gsas-visuals.

Every scenario is one step, each with its own ``build_figures.py``. Steps are
added to STEPS below as scenarios are discussed and built (see PRIMER.md,
Teil B/C) - only scenario-01 exists so far.

Usage:
    python main.py                     run all steps, in order
    python main.py --list              print steps and exit
    python main.py --only scenario-01  run one step
    python main.py --from scenario-02  this step and everything after
    python main.py --skip scenario-01  everything but this
    python main.py --dry-run           print the plan, run nothing
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# name -> path to that scenario's build_figures.py, relative to the repo root
STEPS: list[tuple[str, str]] = [
    ("scenario-01", "scenario-01-symmetric-closure/py/build_figures.py"),
    ("scenario-02", "scenario-02-gsas-calibration/py/build_figures.py"),
    ("scenario-03", "scenario-03-cidoc-class-inference/py/build_figures.py"),
    # Appended here once discussed and built (see PRIMER.md Teil B):
    # ("scenario-04", "scenario-04-neurosymbolic-recommender/py/build_figures.py"),
    # ("scenario-05", "scenario-05-embedding-feed-test/py/build_figures.py"),
]


def _load_module(script_path: Path):
    """Import a scenario's build_figures.py by file path (lazy - no heavy
    imports happen for --list or --dry-run)."""
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _select(names: list[str], only: str | None, frm: str | None,
            skip: str | None) -> list[str]:
    if only:
        return [only] if only in names else []
    selected = names
    if frm:
        idx = names.index(frm) if frm in names else 0
        selected = names[idx:]
    if skip:
        selected = [n for n in selected if n != skip]
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                      formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="print steps and exit")
    parser.add_argument("--only", metavar="NAME", help="run a single step")
    parser.add_argument("--from", dest="frm", metavar="NAME",
                         help="run this step and everything after")
    parser.add_argument("--skip", metavar="NAME", help="run everything but this step")
    parser.add_argument("--dry-run", action="store_true",
                         help="print the plan, run nothing")
    args = parser.parse_args()

    by_name = dict(STEPS)
    names = [n for n, _ in STEPS]

    if args.list:
        for n, p in STEPS:
            print(f"{n:<14} {p}")
        return

    for flag_name, flag_value in (("--only", args.only), ("--from", args.frm),
                                   ("--skip", args.skip)):
        if flag_value and flag_value not in by_name:
            print(f"Unknown step '{flag_value}' for {flag_name}. "
                  f"Known steps: {', '.join(names)}")
            sys.exit(1)

    selected = _select(names, args.only, args.frm, args.skip)
    if not selected:
        print("Nothing to do.")
        return

    timings: list[tuple[str, float]] = []
    for name in selected:
        rel_path = by_name[name]
        script_path = ROOT / rel_path
        if args.dry_run:
            print(f"[dry-run] {name}: would run {rel_path}")
            continue
        start = time.perf_counter()
        module = _load_module(script_path)
        module.main()
        timings.append((name, time.perf_counter() - start))

    if timings:
        total = sum(t for _, t in timings) or 1e-9
        print("\nTiming:")
        for name, elapsed in timings:
            print(f"  {name:<14} {elapsed:6.2f}s  ({100 * elapsed / total:5.1f}%)")


if __name__ == "__main__":
    main()
