"""Paths and frozen parameters for the LA transit accessibility analysis."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = ROOT / "data_raw"
DATA_PROCESSED = ROOT / "data_processed"
OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"

TIME_THRESHOLD_MIN = 30
DESERT_PERCENTILE = 20

WALK_M_PER_MIN = 80.0
TRANSIT_M_PER_MIN = 500.0
WAIT_MIN = 5.0

GEO_CRS = "EPSG:4326"
PROJ_CRS = "EPSG:32611"

LA_BBOX = dict(min_lon=-118.7, max_lon=-117.9, min_lat=33.7, max_lat=34.8)

COUNTY_GEOID_PREFIX = "06037"
