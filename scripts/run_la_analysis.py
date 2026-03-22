#!/usr/bin/env python3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from la_analysis import run_pipeline  # noqa: E402


def main():
    gdf, moran, summary = run_pipeline()
    print("\n--- Summary ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")
    if moran:
        print(f"\n  Moran's I: {moran['I']:.4f} (p ≈ {moran['p_sim']:.4f})")
    print(f"\nFigures: {ROOT / 'outputs' / 'figures'}")
    print(f"Tables:  {ROOT / 'outputs' / 'tables'}")


if __name__ == "__main__":
    main()
