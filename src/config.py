"""
Configuration file for transit corridor optimization project.

This file contains all constants, paths, and parameters that should be
frozen early and not changed during analysis.
"""

from pathlib import Path

# ============================================================================
# PATHS
# ============================================================================

ROOT = Path(__file__).parent.parent.resolve()

DATA_RAW = ROOT / "data_raw"
DATA_PROCESSED = ROOT / "data_processed"
DATA_INTERMEDIATE = ROOT / "data_intermediate"
OUTPUTS = ROOT / "outputs"
OUTPUTS_FIGURES = OUTPUTS / "figures"
OUTPUTS_TABLES = OUTPUTS / "tables"
DOCS = ROOT / "docs"

# ============================================================================
# ACCESSIBILITY PARAMETERS (FROZEN)
# ============================================================================

# Time threshold for accessibility (minutes)
TIME_THRESHOLD = 30  # or 45 - choose once and document

# Binary cutoff (no distance decay)
USE_DISTANCE_DECAY = False

# ============================================================================
# CORRIDOR PARAMETERS
# ============================================================================

# Stop spacing (meters)
DEFAULT_STOP_SPACING = 400  # meters

# Transit speed (km/h)
DEFAULT_TRANSIT_SPEED = 20  # km/h

# Headway (minutes) - for documentation, not used in accessibility
DEFAULT_HEADWAY = 10  # minutes

# Number of candidate corridors to generate
MAX_CANDIDATE_CORRIDORS = 50
MIN_CANDIDATE_CORRIDORS = 20

# ============================================================================
# GEOGRAPHIC PARAMETERS
# ============================================================================

# Los Angeles County FIPS codes
STATE_FIPS = "06"  # California
COUNTY_FIPS = "037"  # Los Angeles County

# Downtown LA coordinates (for distance calculations)
DOWNTOWN_LA_LAT = 34.0522
DOWNTOWN_LA_LON = -118.2437

# CRS for analysis (UTM Zone 11N)
ANALYSIS_CRS = "EPSG:32611"

# Geographic CRS (for mapping)
GEOGRAPHIC_CRS = "EPSG:4326"

# ============================================================================
# DEMOGRAPHIC PARAMETERS
# ============================================================================

# Transit desert threshold (bottom X% of accessibility)
DESERT_THRESHOLD_PERCENTILE = 20  # bottom 20%

# Income threshold for "high need" (dollars)
HIGH_NEED_INCOME_THRESHOLD = 50000  # $50k median household income

# ============================================================================
# OPTIMIZATION PARAMETERS
# ============================================================================

# Weight definition options
WEIGHT_METHOD = "population_x_inverse_income"  # or "population_x_desert", "population_only"

# Top-k corridors to analyze
TOP_K_CORRIDORS = 10

# ============================================================================
# DEMAND ESTIMATION PARAMETERS
# ============================================================================

# Epsilon for demand calculation (avoid division by zero)
DEMAND_EPSILON = 1.0  # jobs

# ============================================================================
# VALIDATION THRESHOLDS
# ============================================================================

# Minimum accessibility gain to be considered meaningful
MIN_ACCESSIBILITY_GAIN = 100  # jobs per 1,000 residents

# Maximum travel time to be considered reasonable
MAX_REASONABLE_TRAVEL_TIME = 120  # minutes

# ============================================================================
# FILE NAMES
# ============================================================================

# Output files
FILE_BASELINE_ACCESSIBILITY = DATA_PROCESSED / "baseline_accessibility.geojson"
FILE_TRAVEL_TIMES = DATA_INTERMEDIATE / "travel_times_matrix.parquet"
FILE_CANDIDATE_CORRIDORS = DATA_PROCESSED / "candidate_corridors.geojson"
FILE_COUNTERFACTUAL_GAINS = DATA_PROCESSED / "counterfactual_accessibility_gains.parquet"
FILE_OPTIMIZATION_RANKINGS = OUTPUTS_TABLES / "corridor_rankings.csv"
FILE_DEMAND_ESTIMATES = OUTPUTS_TABLES / "demand_estimates.csv"

# Figures
FIG_BASELINE_MAP = OUTPUTS_FIGURES / "baseline_accessibility_map.png"
FIG_CANDIDATE_CORRIDORS = OUTPUTS_FIGURES / "candidate_corridors_map.png"
FIG_TOP_CORRIDORS = OUTPUTS_FIGURES / "top_corridors_map.png"
FIG_ACCESSIBILITY_GAINS = OUTPUTS_FIGURES / "accessibility_gains_distribution.png"
FIG_DEMAND_RANKING = OUTPUTS_FIGURES / "demand_ranking.png"

