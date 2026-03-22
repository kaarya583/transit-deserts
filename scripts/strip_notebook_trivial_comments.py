#!/usr/bin/env python3
"""
Remove trivial full-line # comments from Jupyter notebook code cells.
Keeps substantive notes: warnings, formulas, methodology that isn't obvious from code.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Narrow: do not use broad tokens (GEOID, NaN, "align") — they appear in scaffolding.
KEEP_SUBSTR = re.compile(
    r"(IMPORTANT|CRITICAL|\bFROZEN\b|FIXME|TODO\b|WARNING\b|"
    r"NOTE:\s|approx\.|rationale|caveat|limitation|"
    r"haversine|vectorized|broadcast|"
    r"Δ|τ|epsilon|Σ|upper.?bound|counterfactual|"
    r"frozen baseline|A_i\^|per[- ]capita|"
    r"leading zero|preserve leading|11[- ]digit|"
    r"WGS84|UTM Zone|EPSG:\d+|"
    r"Formula|=\s*Σ|=\s*sum|T_ij|D_i\(|Score\(|"
    r"\bτ\s*=\s*|time threshold|km/h|walk speed|transit speed)",
    re.I,
)

DROP_PREFIX = re.compile(
    r"^\s*#\s*("
    r"Load\s|Save\s|Merge\s|Read\s|Write\s|Open\s|Get\s|Try\s|"
    r"Import\s|Install\s|Run\s|Place\s|Add\s|Remove\s|Drop\s|"
    r"Show\s|Print\s|Display\s|Plot\s|Create\s|Build\s|"
    r"Initialize\s|Prepare\s|Extract\s|Fetch\s)",
    re.I,
)

# Typical AI / notebook scaffolding — drop before KEEP_SUBSTR
DROP_AI_SCAFFOLD = re.compile(
    r"^\s*#\s*("
    r"If |Now |Ensure |Verify |Select |Align |Construct |Normalize |"
    r"Data validation|Scatter:|This ensures|Clean gains|Clean scores|Clean metadata|"
    r"Sanity check:|Filter out|Convert to |Additional validation|"
    r"Corridors that|Lower income|Visualize\s*$|Replace any|"
    r"Validation:|Table:|Optional |Quick |Hide |Wrap |"
    r"Iterate |Loop |For each |Parameters?\s*$|Constants?\s*\(|Constants?\s*$|"
    r"For efficiency|Matrix multiplication|Uses Euclidean|"
    r"This is approximate but sufficient|Project to UTM Zone|"
    r"Binary indicator:|Accessibility = sum of jobs|"
    r"Haversine distance function|"
    r"Set style|Set palette|Set figure|Add legend|Add grid|Add colorbar|"
    r"Save figure|Savefig|to_csv|read_csv|to_parquet|"
    r"Title:|Labels?:|X-?label|Y-?label|"
    r"Bar chart|Histogram|Box plot|Choropleth|Heatmap|Subplot|"
    r"Top \d|Bottom \d|Sample |Random |"
    r"Compare |Contrast |Rank |Sort |Identify |Aggregate |Compute summary|"
    r"Summary statistics|Print |Display map|Show map|"
    r"Install |Run notebooks|Place data|"
    r"Continue |Skip |Break |Return |Pass |"
    r"TODO:?\s*remove|placeholder|boilerplate"
    r")",
    re.I,
)

TRIVIAL_START = re.compile(
    r"^\s*#\s*("
    r"Setup|Imports?|Set |Load |Merge |Save |Create |Add |Try |"
    r"Extract |Compute |Aggregate |Visualize |Plot |Rank |Sort |Identify |"
    r"Filter |Print |Initialize |Prepare |Convert |Get |Find |Store |Separate |"
    r"Clean |Also |Basic checks?|Check |Map \d|Visualization \d|"
    r"Part \d|Notebook \d|"
    r"Define |Update |Sample |Flatten |"
    r"Figure|Legend|Colormap|Style|Color|"
    r"Merge on |Align |Read |Write |Close |"
    r"Histogram|KDE|Scatter |"
    r"Get bounding|LA County bbox|"
    r"OSMnx|bounding box"
    r")\b",
    re.I,
)

TRIVIAL_SHORT = re.compile(
    r"^\s*#\s*[A-Za-z]+\s+[a-z][a-z0-9_ ]{0,40}\s*$"
)


def should_keep_comment(line: str) -> bool:
    s = line.strip()
    if not s.startswith("#"):
        return True
    if re.match(r"^\s*#\s*\d+\.\d+\s", line):
        return False
    if re.match(r"^\s*#\s*\d+\.\s+", line):
        return False
    if re.match(r"^\s*#\s*\d+:\s", line):
        return False
    if re.search(r"bounding box \(approximate\)|bbox \(approximate\)", line, re.I):
        return False
    # Array shape hints next to dot products
    if re.match(r"^\s*#\s*[\w.]+\s*:\s*\([^)]+\)\s*$", line):
        return False
    if DROP_PREFIX.match(line):
        return False
    if DROP_AI_SCAFFOLD.match(line):
        return False
    if TRIVIAL_START.match(line):
        return False
    if KEEP_SUBSTR.search(s):
        return True
    if re.match(r"^#\s*[-=]{4,}", s):
        return True
    if len(s) > 130:
        return True
    if len(s) < 55 and TRIVIAL_SHORT.match(line) and not re.search(r"[0-9=ΔτεΣ]", s):
        return False
    return True


def clean_source(source: list[str] | str) -> tuple[list[str], bool]:
    if isinstance(source, str):
        lines = source.splitlines(keepends=True)
    else:
        lines = list(source)

    out: list[str] = []
    changed = False
    prev_kept_comment: str | None = None
    for line in lines:
        if line.lstrip().startswith("#") and not line.strip().startswith("#!"):
            if not should_keep_comment(line):
                changed = True
                prev_kept_comment = None
                continue
            if line == prev_kept_comment:
                changed = True
                continue
            out.append(line)
            prev_kept_comment = line
        else:
            out.append(line)
            prev_kept_comment = None
    return out, changed


def process_notebook(path: Path) -> bool:
    with open(path, encoding="utf-8") as f:
        nb = json.load(f)

    file_changed = False
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        new_src, changed = clean_source(src)
        if changed:
            cell["source"] = new_src
            file_changed = True

    if file_changed:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(nb, f, indent=1, ensure_ascii=False)
            f.write("\n")
    return file_changed


def main() -> int:
    roots = [ROOT / "notebooks"]
    changed_files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.ipynb")):
            if process_notebook(path):
                changed_files.append(path.relative_to(ROOT))

    for p in changed_files:
        print(f"updated: {p}")
    if not changed_files:
        print("no changes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
